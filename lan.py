import time
import itertools
from threading import Thread
from queue import Queue, Empty
import netifaces # https://pypi.org/project/netifaces/
import arpreq # https://pypi.org/project/arpreq/

# Local Files
import viz
import verbose
import ping as ping_interface
import worker_threads as worker


def LAN_hosts(is_verbose, is_visualized):
    """ Obtain information about the hosts residing on the LAN. """

    if is_verbose:
        verbose.LAN_start()

    # Get information about the LAN
    local_IP, gateway_mask, interface = LAN_info(is_verbose)
    gateway = gateway_IP()

    # Ping LAN range and find other hosts if a local IP and gateway mask were found
    if local_IP == '' or gateway_mask == '':
        verbose.LAN_no_info()

    else:
        if is_verbose:
            verbose.LAN_info(local_IP, gateway, gateway_mask, interface)

        # Get the possible LAN addresses
        possible_LAN_addrs = LAN_possibilities(is_verbose, local_IP, gateway_mask)

        # Run ping over the LAN range
        if is_verbose:
            verbose.LAN_ping_start(possible_LAN_addrs[0], possible_LAN_addrs[-1])

        ping_start = time.time()
        ping_hosts = ping_LAN(is_verbose, possible_LAN_addrs)
        ping_time_elapsed = round(time.time() - ping_start, 2)

        if is_verbose:
            verbose.LAN_ping_results(ping_time_elapsed, ping_hosts, local_IP, gateway)

        # Arp request over the LAN range
        if is_verbose:
            verbose.LAN_ARP_start(possible_LAN_addrs[0], possible_LAN_addrs[-1])

        ARP_start = time.time()
        ARP_hosts = ARP_LAN(possible_LAN_addrs)
        ARP_time_elapsed = round(time.time() - ARP_start, 2)
        
        if is_verbose:
            verbose.LAN_ARP_results(ARP_time_elapsed, ARP_hosts, local_IP, gateway)

        # Run port scan
        if is_verbose:
            verbose.LAN_port_scan_start()

        port_scan_start = time.time()
        open_ports = open_LAN_ports(ping_hosts, ARP_hosts)
        port_scan_elapsed = round(time.time() - port_scan_start, 2)

        if is_verbose:
            verbose.LAN_port_scan_results(port_scan_elapsed, open_ports)

        # Create dictionary about the LAN for visualization
        LAN_Dict = create_LAN_dict(ping_hosts, ARP_hosts, open_ports, local_IP, gateway)
        if is_visualized:
            viz.visualize_LAN(LAN_Dict)
    
def LAN_info(is_verbose):
    """ Returns the local IP, gateway, and gateway mask if they are found. """

    # Returns names of local interfaces
    interfaces = netifaces.interfaces()

    # Find local IP address and netmask of gateway
    local_IP = ''
    gateway_mask = ''
    interface = ''
    for inter in interfaces:
        # Returns dictionary of address
        addrs = netifaces.ifaddresses(inter) 
        
        # AF_INET (IPv4 Internet addresses) is the address family that we desire
        # Note an interface may have more than one set of address, so we iterate over them
        IPv4_addrs = addrs[netifaces.AF_INET]
        for addr in IPv4_addrs:
            addr_IP = addr['addr']
            addr_netmask = addr['netmask']

            # Ignore loopback address
            if addr_IP != '127.0.0.1' and addr_netmask != '255.0.0.0':
                local_IP = addr_IP
                gateway_mask = addr_netmask
                interface = inter

    return [local_IP, gateway_mask, interface]

def gateway_IP():
    """ Returns the default gateway IPv4 address. """
    gws = netifaces.gateways()
    return gws['default'][netifaces.AF_INET][0]  

def logical_AND_dotted_quads(quad1, quad2):
    """ Returns dotted quad of two anded dotted quad addresses """

    quad1_split = [int(i) for i in quad1.split('.')]
    quad2_split = [int(i) for i in quad2.split('.')]

    anded_quads_bin = []
    for a, b in zip(quad1_split, quad2_split):
        anded_quads_bin.append(a & b)

    anded_quads_dotted = ''
    for i in range(len(anded_quads_bin)):
        if i != len(anded_quads_bin) - 1:
            anded_quads_dotted += str(int(anded_quads_bin[i])) + '.'
        else:
            anded_quads_dotted += str(int(anded_quads_bin[i]))

    return anded_quads_dotted
    
def LAN_possibilities(isVerbose, local_IP, gatewayMask):
    """ Get all possibilites of IPv4 addresses within the LAN. """

    # AND local IP and gateway mask
    anded_quad = logical_AND_dotted_quads(local_IP, gatewayMask)

    # Convert dotted quads to binary strings
    anded_bitStr = quad_to_bin_str(anded_quad)
    mask_bitStr = quad_to_bin_str(gatewayMask)

    # Find the index at which the mask ends (the first 0 bit)
    mask_end_index = 0
    for i in range(len(mask_bitStr)):
        if mask_bitStr[i] == "0":
            mask_end_index = i
            break

    # Get the number of 0 bits that can be altered, according to the mask
    changeable_bit_length = 32 - mask_end_index
    bin_possibilities = bin_combinations(changeable_bit_length)

    # Get the entire binary representation of all possible LAN IPv4 addresses
    LAN_possibilities_bin = []
    for combo in bin_possibilities:
        host_bin = anded_bitStr[:mask_end_index] + combo

        # Exclude addresses that end in 0 or 255
        if host_bin[24:32] != "11111111" and host_bin[24:32] != "00000000":
            LAN_possibilities_bin.append(anded_bitStr[:mask_end_index] + combo)

    LAN_possibilities = [bin_to_dotted_quad(i) for i in LAN_possibilities_bin]

    return LAN_possibilities

def bin_combinations(bin_str_len):
    """ Returns list of strings of all of the possible binary combinations """

    bin_possibilities = []

    # Only try subnet masks with less than 12 alterable bits as to not 
    # ping or arp more than 2^13 (8192) addresses
    if bin_str_len < 13:
        # Get all of the binary possibilities of bin_str_len bits
        bin_possibilities = list(itertools.product(["0", "1"], repeat=bin_str_len))
        bin_possibilities = [''.join(i) for i in bin_possibilities]
    else:
        raise Exception("LAN subnet too large to ping.")

    return bin_possibilities

def quad_to_bin_str(quad):
    """ Returns binary string representation of a dotted quad string. """

    bin_str_final = ''
    for quad in quad.split('.'):
        bin_str = "{0:b}".format(int(quad))

        # Pad each binary representation to 8 bits
        if len(bin_str) != 8:
            bin_str = "0" * (8 - len(bin_str)) + bin_str

        bin_str_final += bin_str

    return bin_str_final

def bin_to_dotted_quad(bin_in):
    """ Returns the dotted quad representation of a binary string. """

    if len(bin_in) != 32:
        raise Exception("Binary string input to bin_to_dotted_quad must be 32 bits.")

    IP_addr = ""
    # Build dotted quad by partitioning bits into the four quads  
    for i in range(0, 25, 8):
        if i != 24:
            IP_addr += str(int(bin_in[i:i+8], 2)) + "."
        else:
            IP_addr += str(int(bin_in[i:i+8], 2))

    return IP_addr

def ping_LAN(is_verbose, LAN_possibilities):
    """ Pings all IPv4 address within LAN range. """

    ping_results = []

    # https://stackoverflow.com/questions/39501529/python-stop-thread-with-raw-input
    # Build a queue of all of the LAN addresses
    queue = Queue()
    num_threads = 100
    for addr in LAN_possibilities:
        queue.put(addr)
    
    # Start a thread to afford user to quit LAN ping
    end_queue = Queue()
    input_thread = Thread(target=worker.input_thread, args=(end_queue, num_threads))
    input_thread.start()
    print("Enter 'q' and <ENTER> to end the LAN ping.")

    threads = []
    for i in range(num_threads):
        t = Thread(target=worker.ping_worker, args=(queue, ping_results, end_queue))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    LAN_hosts = []
    for res in ping_results:
        if res != []:
            LAN_hosts.append(res)

    return LAN_hosts

def ARP_LAN(LAN_possibilities):
    """ Returns IPv4 and MAC addresses of ARP requests of the LAN. """

    found_with_ARP = []
    for ip in LAN_possibilities:
        res = arpreq.arpreq(ip)
        if res is not None:
            found_with_ARP.append([ip, res])

    return found_with_ARP

def open_LAN_ports(ping_hosts, ARP_hosts):
    # Get the list of unique hosts
    ping_hosts = set([host for host, RTT in ping_hosts])
    ARP_hosts = set([host for host, MAC in ARP_hosts])
    only_in_ARP = ARP_hosts - ping_hosts
    all_hosts = list(ping_hosts) + list(only_in_ARP)

    # Build queue of host, port pairs
    queue = Queue()
    num_threads = 100
    ports_to_try = [i for i in range(1,1025)]
    for addr in all_hosts:
        for port in ports_to_try:
            queue.put([addr, port])
    
    # Start a thread to afford user to quit port scan
    end_queue = Queue()
    input_thread = Thread(target=worker.input_thread, args=(end_queue, num_threads))
    input_thread.start()
    print("Enter 'q' and <ENTER> to end the port scan.")

    open_ports = []
    threads = []
    for i in range(num_threads):
        t = Thread(target=worker.port_scan_worker, args=(queue, open_ports, end_queue))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    return open_ports

def create_LAN_dict(ping_hosts, ARP_hosts, open_ports, local_IP, gateway):
    """ Return dictionary with LAN info in the form of: {host : [RTT, MAC, Description, Open Ports]}"""
    
    LAN_dict = {}
    # Add description and RTT from ping_hosts
    for host, RTT in ping_hosts:
        description = ''
        if host == local_IP:
            description = "Local Host"
        elif host == gateway:
            description = "Gateway"
        
        LAN_dict[host] = [str(round(RTT, 4)), '', description, []]

    # Add MAC and new hosts from ARP_hosts
    for host, MAC in ARP_hosts:
        if host in LAN_dict:
            LAN_dict[host][1] = MAC
        else:
            LAN_dict[host] = ["null", MAC, '', []]

    # Add found open ports
    for host_info in open_ports:
        host = host_info[0]
        ports = host_info[1]

        ports_str = ""
        for i in range(len(ports)):
            if i != len(ports) - 1:
                ports_str += ports[i] + ','
            else:
                ports_str += ports[i]

        if host in LAN_dict:
            LAN_dict[host][3] = ports
        else:
            LAN_dict[host] = ["null", '', '', ports]

    return LAN_dict