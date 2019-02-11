#!/usr/bin/env python
"""Creates threads for functions passed as parameter,
   returning results upon completion. 
"""

import worker_threads as worker

from threading import Thread
from queue import Queue, Empty

def get_thread_res(inputs_queue, res_obj, num_threads, worker_func):    
    """Start input and worker_func threads, returning worker_thread results"""

    # Allow user to end threads with 'ctrl+c'
    print("'ctrl+c' to end the threads.")

    # Create threads that accumulate results in res_obj
    end_queue = Queue()
    threads = []
    for _ in range(num_threads):
        t = Thread(target=worker_func, args=(inputs_queue, res_obj, end_queue))
        t.start()
        threads.append(t)

    # Try to join threads, catching 'ctrl+c' interrupt
    try:
        for thread in threads:
            thread.join()

    except KeyboardInterrupt: 
        print("\nExiting threads.")

        # Fill end_queue with quit message
        for _ in range(len(threads)):
            end_queue.put("quit")

        for thread in threads:
            thread.join()

    return res_obj