import time
from multiprocessing import Pool
import netifaces # https://pypi.org/project/netifaces/
import itertools
import arpreq # https://pypi.org/project/arpreq/

# Local Files
import viz
import verbose
import ping as pingInterface


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

        LAN_Dict = create_LAN_Dict(ping_hosts, ARP_hosts, local_IP, gateway)

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
    """ Get the dotted quad representation of possibilites of IPv4 addresses within the LAN. """

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

    # Only try subnet masks with less than 16 alterable bits for computational complexity reasons
    if bin_str_len < 16:
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

    # https://stackabuse.com/parallel-processing-in-python/
    agents = 12
    chunck_size = len(LAN_possibilities) // agents
    with Pool(processes=agents) as pool:
        ping_results = pool.map(ping, LAN_possibilities, chunck_size)
    
    LAN_hosts = []
    for res in ping_results:
        if res != []:
            LAN_hosts.append(res)

    return LAN_hosts

def ping(dest_addr):
    """ Pings an IPv4 address, returning RTT if there is a response. """

    RTT = pingInterface.ping(dest_addr)
    if RTT is not None:
        return [dest_addr, RTT]
    else:
        return []

def ARP_LAN(LAN_possibilities):
    """ Returns IPv4 and MAC addresses of ARP requests of the LAN. """

    found_with_ARP = []
    for ip in LAN_possibilities:
        res = arpreq.arpreq(ip)

        if res is not None:
            found_with_ARP.append([ip, res])

    return found_with_ARP

def create_LAN_Dict(ping_hosts, ARP_hosts, local_IP, gateway):
    """ Return dictionary with LAN info in the form of: {host : [RTT, MAC, Description]}"""
    LAN_Dict = {}
    for host, RTT in ping_hosts:
        description = ''
        if host == local_IP:
            description = "Local Host"
        elif host == gateway:
            description = "Gateway"
        
        LAN_Dict[host] = [str(round(RTT, 4)), '', description]

    for host, MAC in ARP_hosts:
        if host in LAN_Dict:
            LAN_Dict[host][1] = MAC
        else:
            LAN_Dict[host] = ["null", MAC, '']

    return LAN_Dict