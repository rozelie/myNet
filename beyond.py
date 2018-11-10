import trace_route
from threading import Thread
from queue import Queue, Empty
import worker_threads as worker
import create_threads

def retrieve_beyond_info():
    found_hops = get_hops()
    print(found_hops)
    return 0

def get_hops():
    """Run traceroute on a number of servers, returning information about the hops"""
    queue = Queue()
    servers = ["google.com", "spotify.com", "stackoverflow.com"]
    for addr in servers:
        queue.put(addr)
    
    num_threads = len(servers)
    found_hops = {}
    found_hops = create_threads.get_thread_res(queue, found_hops, num_threads, worker.trace_worker)

    return found_hops