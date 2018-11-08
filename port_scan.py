import socket
import time
import subprocess
import sys
from datetime import datetime
from queue import Queue, Empty

def port_scan_worker(queue, open_ports, end_queue):
    """ """
    # Adapted from https://www.pythonforbeginners.com/code-snippets-source-code/port-scanner-in-python
    
    while True:
        try:
            try:
                end_queue.get(block=True, timeout = 1)
                break
            except Empty:
                pass

            remote_IP, port = queue.get(block=True, timeout = 1)
            queue.task_done()

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((remote_IP, port))

            if result == 0:
                open_ports.append([remote_IP, str(port)])

            sock.close()

        except Empty:
            break