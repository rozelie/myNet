import trace_route
from threading import Thread
from queue import Queue, Empty

import worker_threads as worker
import create_threads
from viz import beyond_viz

def retrieve_beyond_info():
    host_trace_res = get_trace_paths()
    print(host_trace_res)
    beyond_viz(host_trace_res).visualize_traceroute()
    

def get_trace_paths():
    """Run traceroute on a number of servers, returning information about the hops."""
    queue = Queue()
    servers = ["google.com", "spotify.com", "stackoverflow.com"]
    for addr in servers:
        queue.put(addr)
    
    num_threads = len(servers)
    host_trace_res = {}
    host_trace_res = create_threads.get_thread_res(queue, host_trace_res, num_threads, worker.trace_worker)

    return host_trace_res