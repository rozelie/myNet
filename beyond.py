import trace_route
from threading import Thread
from queue import Queue, Empty

import trace_route
import create_threads
from viz import beyond_viz

def retrieve_beyond_info():
    """Initiates traceroutes and passes results to generate visualization"""
    host_trace_res = get_trace_paths()
    
    beyond_viz(host_trace_res).visualize_traceroute()
    
def get_trace_paths():
    """Run traceroute on a number of servers, returning information about the hops"""
    queue = Queue()
    servers = ["google.com", "spotify.com", "stackoverflow.com"]
    ports = [33434, 33435, 33436]
    for addr, port in zip(servers, ports):
        queue.put([addr, port])
    
    num_threads = len(servers)
    host_trace_res = {}
    host_trace_res = create_threads.get_thread_res(queue, host_trace_res, num_threads, trace_route.run_trace)

    return host_trace_res