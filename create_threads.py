from threading import Thread
from queue import Queue, Empty
import worker_threads as worker

def get_thread_res(inputs_queue, res_obj, num_threads, worker_func):    
    """Start input and worker_func threads, returning worker_thread results"""

    # Start a thread to afford user to quit the traceroute
    end_queue = Queue()
    input_thread = Thread(target=worker.input_thread, args=(end_queue, num_threads))
    input_thread.start()
    print("Enter 'q' and <ENTER> to end the traceroute.")

    # Create threads that accumulate results in res_obj
    threads = []
    for i in range(num_threads):
        t = Thread(target=worker_func, args=(inputs_queue, res_obj, end_queue))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    return res_obj