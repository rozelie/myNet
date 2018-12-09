import trace_route
from threading import Thread
from queue import Queue, Empty
from requests import get

import trace_route
import lan
import worker_threads as worker
import bin_tools
import create_threads
from viz import beyond_viz, neighboring_subnets

def retrieve_beyond_info():
    """Initiates traceroutes and passes results to generate visualization."""
    # Deduce neighboring subnets and ping a sample of those subnets
    neighbor_res, public_IP = check_neighboring_subnets()

    # Visualize the found neighboring subnets
    neighboring_subnets(neighbor_res, public_IP).visualize_neighbors()

    # Run traceroute to servers across the world
    #host_trace_res = get_trace_paths()
    
    # Visualize the traceroute
    #beyond_viz(host_trace_res).visualize_traceroute()

def check_neighboring_subnets():
    # Get information about the LAN
    _, gateway_mask, _ = lan.basic_info()
    public_IP = get('https://api.ipify.org').text
    print("Public IP address:", public_IP)

    # Get the smallest and largest possible IP addresses within the subnet
    smallest_IP, largest_IP = subnet_range(public_IP, gateway_mask)
    print("Public LAN IP range: {} to {}".format(smallest_IP, largest_IP))

    # Generate list of neighboring IP ranges to ping (assuming /24 masks)
    neighboring_subnets = get_neighboring_subnets(smallest_IP, largest_IP)

    # Ping subnet neighbors to retrieve information about surrounding subnets
    neighbor_res = ping_neighbors(neighboring_subnets)

    return neighbor_res, public_IP
    
def subnet_range(public_IP, gateway_mask):
    # AND public IP and gateway mask
    anded_quad = bin_tools.logical_AND_dotted_quads(public_IP, gateway_mask)

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
    
    # Get the smallest and largest binary representation of the changeable bits of IPv4 addresses
    smallest_bin_combo = bin_possibilities[0]
    largest_bin_combo = bin_possibilities[-1]

    # Get the full, smallest and largest binary representation of IPv4 addresses
    anded_bitStr = bin_tools.quad_to_bin_str(anded_quad)
    smallest_bin_IP = anded_bitStr[:mask_end_index] + smallest_bin_combo
    largest_bin_IP = anded_bitStr[:mask_end_index] + largest_bin_combo

    # Generate the smallest and largest IPv4 addresses of the subnet
    smallest_IP = bin_tools.bin_to_dotted_quad(smallest_bin_IP)
    largest_IP = bin_tools.bin_to_dotted_quad(largest_bin_IP)

    return smallest_IP, largest_IP
    
def get_neighboring_subnets(smallest_IP, largest_IP ):
    smallest_split = smallest_IP.split(".")
    largest_split = largest_IP.split(".")
    smallest_third_quad = smallest_split[2]
    largest_third_quad = largest_split[2]
    
    range_to_expand = 5
    new_third_quad_largest = int(largest_third_quad) + range_to_expand
    new_third_quad_smallest = int(smallest_third_quad) - range_to_expand

    neighboring_subnets = []
    for i in range(new_third_quad_smallest, new_third_quad_largest + 1):     
        new_quad = '.'.join(largest_split[:2]) + "." + str(i) + ".0"
        neighboring_subnets.append(new_quad)

    return neighboring_subnets
  
def ping_neighbors(neighboring_subnets):
    # Build a queue of addresses to ping in each neighboring subnet
    queue = Queue()

    # Construct IPv4 addresses in the subnets to ping
    num_addr_to_try = 10
    for addr in neighboring_subnets:
        split_addr = addr.split(".")
        for i in range(1, num_addr_to_try + 1):
            new_addr = '.'.join(split_addr[:3]) + '.' + str(i)
            queue.put(new_addr)

    print("Pinging subnets.")

    # Start a thread for each ping
    num_threads = 200
    ping_results = []
    threads = []
    for _ in range(num_threads):
        t = Thread(target=worker.ping_worker, args=(queue, ping_results, Queue()))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    # Construct dictionary of subnet ping results
    ping_neighbors_res = {}
    for res in ping_results:
        if res != []:
            pinged_subnet_split = res[0].split(".")
            pinged_subnet = '.'.join(pinged_subnet_split[:3]) + '.0'

            if pinged_subnet not in ping_neighbors_res:
                ping_neighbors_res[pinged_subnet] = [res]
            else:
                ping_neighbors_res[pinged_subnet].append(res)

    return ping_neighbors_res

def get_trace_paths():
    """Run traceroute on a number of servers, returning information about the hops."""

    # University of Alaska - Anchorage, Florida Atlantic University, Middle East University
    servers = ["www.uaa.alaska.edu", "www.fau.edu", "meu.edu.lb"]
    host_trace_res = {}
    for server in servers:
        print("Running traceroute to", server)

        # Run traceroute to sever
        trace_res = trace_route.run_trace(server)

        # Remove duplicate hops
        hops_found = {}
        trace_res_no_dups = []
        for host, RTT in trace_res:
            if host not in hops_found:
                hops_found[host] = 1
                trace_res_no_dups.append([host, RTT])

        host_trace_res[server] = trace_res_no_dups
        print("Traceroute to", server, "completed.")

    print("Traceroutes completed.")
    return host_trace_res