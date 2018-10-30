import time
from multiprocessing import Pool
import netifaces # https://pypi.org/project/netifaces/
import itertools

# Local Files
import viz
import verbose
import ping


def get_LAN_hosts(is_verbose, is_visualized):
    """ Obtain information about the hosts residing on the LAN. """

    if is_verbose:
        verbose.LAN_start()

    # Get information about the LAN
    local_IP, gateway_IP, gateway_mask, interface = get_LAN_info(is_verbose)

    # Ping LAN range and find other hosts if a local IP and gateway mask were found
    if local_IP == '' or gateway_mask == '':
        verbose.LAN_no_info()

    else:
        if is_verbose:
            verbose.LAN_info(local_IP, gateway_IP, gateway_mask, interface)

        LAN_possibilities = get_LAN_possibilities(is_verbose, local_IP, gateway_mask)

        if is_verbose:
            verbose.LAN_ping_start(LAN_possibilities[0], LAN_possibilities[-1])

        ping_start = time.time()
        LAN_hosts = do_LAN_ping(is_verbose, LAN_possibilities)
        ping_time_elapsed = round(time.time() - ping_start, 2)

        if is_verbose:
            verbose.LAN_ping_results(ping_time_elapsed, LAN_hosts, local_IP, gateway_IP)

        if is_visualized:
            viz.visualize_LAN(LAN_hosts, local_IP, gateway_IP)

def get_LAN_info(is_verbose):
    """ Returns the local IP, gateway, gateway mask, and interface if they are found. """

    # Returns names of local interfaces
    interfaces = netifaces.interfaces()

    # Find local IP address and netmask of gateway
    local_IP = ''
    gateway_mask = ''
    for interface in interfaces:
        # Returns dictionary of address
        addrs = netifaces.ifaddresses(interface) 
        
        # AF_INET (IPv4 Internet addresses) is the address family that we desire
        # Note an interface may have more than one set of address
        IPv4_addrs = addrs[netifaces.AF_INET]
        for addr in IPv4_addrs:
            addrIP = addr['addr']
            addrNetmask = addr['netmask']

            if addrIP != '127.0.0.1' and addrNetmask != '255.0.0.0':
                local_IP = addrIP
                gateway_mask = addrNetmask

    if local_IP == '' or gateway_mask == '':
        print("Unable to locate local IP address or gateway mask.")

    # Get default gateway IP
    gws = netifaces.gateways()
    gateway_IP = gws['default'][netifaces.AF_INET][0]

    return [local_IP, gateway_IP, gateway_mask, interface]

def get_LAN_possibilities(isVerbose, local_IP, gatewayMask):
    """ Get the possibilites of IPv4 addresses within the LAN. """

    local_IP_quads = [int(i) for i in local_IP.split('.')]
    gateway_quads = [int(i) for i in gatewayMask.split('.')]
    anded_quads = []
    for a, b in zip(local_IP_quads, gateway_quads):
        anded_quads.append(a & b)

    anded_bitStr = quad_to_bin_str(anded_quads)
    mask_bitStr = quad_to_bin_str(gateway_quads)

    first_zero_index = 0
    for i in range(len(mask_bitStr)):
        if mask_bitStr[i] == "0":
            first_zero_index = i
            break

    num_bin_combinations = 32 - first_zero_index
    bin_combination_ends = []

    #TODO explain this logic
    if num_bin_combinations < 16:
        bin_combination_ends = list(itertools.product(["0", "1"], repeat=num_bin_combinations))
        bin_combination_ends = [''.join(i) for i in bin_combination_ends]

    LAN_possibilities_bin = []
    for combo in bin_combination_ends:
        LAN_host_bin = anded_bitStr[:first_zero_index] + combo
        # Exclude addresses that end in 0 or 255
        if LAN_host_bin[24:32] != "11111111" and LAN_host_bin[24:32] != "00000000":
            LAN_possibilities_bin.append(anded_bitStr[:first_zero_index] + combo)

    LAN_possibilities = [bin_to_IP(i) for i in LAN_possibilities_bin]

    return LAN_possibilities

def quad_to_bin_str(quads):
    bin_str_final = ''
    for i in quads:
        bin_str = "{0:b}".format(i)
        if len(bin_str) != 8:
            bin_str = "0" * (8 - len(bin_str)) + bin_str
        bin_str_final += bin_str

    return bin_str_final

def bin_to_IP(bin_in):
    IP_addr = ""
    # 0,8  8,16   16,24    24,32
    for i in range(0, 25, 8):
        if i != 24:
            IP_addr += str(int(bin_in[i:i+8], 2)) + "."
        else:
            IP_addr += str(int(bin_in[i:i+8], 2))

    return IP_addr

def do_LAN_ping(is_verbose, LAN_possibilities):
    """ Pings all IPv4 address within LAN range. """

    ping_results = []

    # https://stackabuse.com/parallel-processing-in-python/
    agents = 12
    chunck_size = len(LAN_possibilities) // agents
    with Pool(processes=agents) as pool:
        ping_results = pool.map(do_ping, LAN_possibilities, chunck_size)
    
    LAN_hosts = []
    for res in ping_results:
        if res != []:
            LAN_hosts.append(res)

    return LAN_hosts

def do_ping(dest_addr):
    """ Pings an IPv4 address, returning RTT if there is a response. """

    RTT = ping.ping(dest_addr)
    if RTT is not None:
        return [dest_addr, RTT]
    else:
        return []