import time
from threading import Thread
from queue import Queue, Empty
import netifaces # https://pypi.org/project/netifaces/
import arpreq # https://pypi.org/project/arpreq/
from manuf import manuf as mac_manuf

# Local Files
from viz import lan_viz
import verbose
import ping as ping_interface
import worker_threads as worker
import create_threads
import bin_tools


def retrieve_LAN_info(is_verbose, is_visualized):
    """Obtain information about the hosts residing on the LAN, presenting information along the way"""

    verbose.LAN_start()

    # Get information about the LAN
    local_IP, gateway_mask, interface = basic_info()
    gateway = gateway_IP()

    # Ping LAN range and find other hosts if a local IP and gateway mask were found
    if local_IP == '' or gateway_mask == '':
        verbose.LAN_no_info()

    else:
        verbose.LAN_info(local_IP, gateway, gateway_mask, interface)

        # Get the possible LAN addresses
        possible_LAN_addrs = LAN_possibilities(local_IP, gateway_mask)

        # Run ping over the LAN range
        verbose.LAN_ping_start(possible_LAN_addrs[0], possible_LAN_addrs[-1])

        ping_start = time.time()
        ping_hosts = ping_LAN(is_verbose, possible_LAN_addrs)
        ping_time_elapsed = round(time.time() - ping_start, 2)

        verbose.LAN_ping_results(ping_time_elapsed, ping_hosts, local_IP, gateway)

        # Arp request over the LAN range
        # Skip the first and last items - reserved addresses
        verbose.LAN_ARP_start(possible_LAN_addrs[0], possible_LAN_addrs[-1])

        ARP_start = time.time()
        ARP_hosts = ARP_LAN(possible_LAN_addrs)
        ARP_time_elapsed = round(time.time() - ARP_start, 2)
        
        verbose.LAN_ARP_results(ARP_time_elapsed, ARP_hosts, local_IP, gateway)

        # Run port scan
        verbose.LAN_port_scan_start()

        port_scan_start = time.time()
        open_ports = open_LAN_ports(ping_hosts, ARP_hosts)
        port_scan_elapsed = round(time.time() - port_scan_start, 2)

        verbose.LAN_port_scan_results(port_scan_elapsed, open_ports)

        # Create dictionary about the LAN for visualization
        LAN_Dict = create_LAN_dict(ping_hosts, ARP_hosts, open_ports, local_IP, gateway)

        # Create graphviz representation of the LAN
        if is_visualized:
            lan_viz(LAN_Dict).visualize_LAN()
    
def basic_info():
    """Returns the local IP, gateway mask, and interface if they are found"""

    # Returns names of local interfaces
    interfaces = netifaces.interfaces()

    # Find local IP address and netmask of gateway
    local_IP = ''
    gateway_mask = ''
    interface = ''
    for inter in interfaces:
        # Returns dictionary of addresses
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
    """Returns the default gateway IPv4 address"""

    gws = netifaces.gateways()
    return gws['default'][netifaces.AF_INET][0]  
    
def LAN_possibilities(local_IP, gateway_mask):
    """Get all possibilites of IPv4 addresses within the LAN"""

    # AND local IP and gateway mask
    anded_quad = bin_tools.logical_AND_dotted_quads(local_IP, gateway_mask)

    # Convert dotted quads to binary strings
    anded_bitStr = bin_tools.quad_to_bin_str(anded_quad)
    mask_bitStr = bin_tools.quad_to_bin_str(gateway_mask)

    # Find the index at which the mask ends (the first 0 bit)
    mask_end_index = 0
    for i in range(len(mask_bitStr)):
        if mask_bitStr[i] == "0":
            mask_end_index = i
            break

    # Get the number of 0 bits that can be altered, according to the mask
    changeable_bit_length = 32 - mask_end_index
    bin_possibilities = bin_tools.bin_combinations(changeable_bit_length)

    # Exclude the first and last addresses of the subnet: x.x.x.0 and x.x.x.255
    # x.x.x.0 is usually not used by convention and x.x.x.255 is reserved for a broadcast address
    bin_possibilities = bin_possibilities[1:-1]

    # Get the entire binary representation of all possible LAN IPv4 addresses
    LAN_possibilities_bin = []
    for combo in bin_possibilities:
        LAN_possibilities_bin.append(anded_bitStr[:mask_end_index] + combo)

    # Transform binary addresses to IPv4
    LAN_possibilities = [bin_tools.bin_to_dotted_quad(i) for i in LAN_possibilities_bin]

    return LAN_possibilities

def ping_LAN(is_verbose, LAN_possibilities):
    """ Pings all IPv4 address within LAN range. """

    # Build a queue of all of the LAN addresses
    queue = Queue()
    num_threads = 200
    for addr in LAN_possibilities:
        queue.put(addr)
    
    ping_results = []
    ping_results = create_threads.get_thread_res(queue, ping_results, num_threads, worker.ping_worker)

    LAN_hosts = []
    for res in ping_results:
        if res != []:
            LAN_hosts.append(res)

    return LAN_hosts

def ARP_LAN(LAN_possibilities):
    """Returns IPv4 and MAC addresses of the ARP cache."""

    found_with_ARP = []
    mac_parser = mac_manuf.MacParser(update=True)
    for ip in LAN_possibilities:
        res = arpreq.arpreq(ip)
        if res is not None:
            manuf = mac_parser.get_manuf(res)
            comment = mac_parser.get_comment(res)

            found_with_ARP.append([ip, res, manuf, comment])
   
    return found_with_ARP

def open_LAN_ports(ping_hosts, ARP_hosts):
    """Scan ports of LAN hosts."""

    # Get the list of unique hosts
    ping_hosts = set([host for host, RTT in ping_hosts])
    ARP_hosts = set([host for host, MAC, manuf, comment in ARP_hosts])
    only_in_ARP = ARP_hosts - ping_hosts
    all_hosts = list(ping_hosts) + list(only_in_ARP)

    # Build queue of host, port pairs
    queue = Queue()
    num_threads = 100
    ports_to_try = [i for i in range(1,1025)]
    for addr in all_hosts:
        for port in ports_to_try:
            queue.put([addr, port])

    open_ports = []
    open_ports = create_threads.get_thread_res(queue, open_ports, num_threads, worker.port_scan_worker)

    return open_ports

def create_LAN_dict(ping_hosts, ARP_hosts, open_ports, local_IP, gateway):
    """Return dictionary with LAN info in the form of: 
       {host : [RTT, MAC, Manfuacturer, Product Description, Description, Open Ports]}.
    """
    
    LAN_dict = {}

    # Add local host and gateway
    LAN_dict[local_IP] = ['', '', '', '', "Local Host", []]
    LAN_dict[gateway] = ['', '', '', '', "Gateway", []]

    # Add description and RTT from ping_hosts
    for host, RTT in ping_hosts:
        if host in LAN_dict:
            LAN_dict[host][0] = str(round(RTT, 4))
        else:
            LAN_dict[host] = [str(round(RTT, 4)), '', '', '', '', []]

    # Add MAC and new hosts from ARP_hosts
    for host, MAC, manuf, comment in ARP_hosts:
        if host in LAN_dict:
            LAN_dict[host][1] = MAC
            LAN_dict[host][2] = manuf
            LAN_dict[host][3] = comment
        else:
            LAN_dict[host] = ["null", MAC, manuf, comment, '', []]

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
            LAN_dict[host][5] = ports
        else:
            LAN_dict[host] = ["null", '', '', '', '', ports]

    return LAN_dict