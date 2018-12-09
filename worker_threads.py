import socket
import time
import subprocess
import sys
from datetime import datetime
from queue import Queue, Empty

import ping as ping_interface
import trace_route

                
def ping_worker(queue, ping_results, end_queue):
    """ Pings an IPv4 address, returning RTT if there is a response. """
    while True:
        try:
            try:
                end_queue.get(block=True, timeout = 1)
                break
            except Empty:
                pass

            item = queue.get(block=True, timeout = 1)
            queue.task_done()
            
            RTT = ping_interface.ping(item)
            if RTT is not None:
                ping_results.append([item, RTT])

        except Empty:
            break

def ping_worker_unis(queue, ping_results, end_queue):
    """ Pings an IPv4 address, returning RTT if there is a response. """
    while True:
        try:
            try:
                end_queue.get(block=True, timeout = 1)
                break
            except Empty:
                pass

            uni, host = queue.get(block=True, timeout = 1)
            queue.task_done()
            
            RTT = ping_interface.ping(host)
            if RTT is not None:
                ping_results.append([uni, host, RTT])

        except Empty:
            break

def ping_worker_end_if_found(queue, ping_results, end_queue, num_threads):
    """ Pings an IPv4 address, returning RTT if there is a response. """
    while True:
        try:
            try:
                end_queue.get(block=True, timeout = 1)
                break
            except Empty:
                pass

            item = queue.get(block=True, timeout = 1)
            queue.task_done()
            
            RTT = ping_interface.ping(item)
            if RTT is not None:
                ping_results.append([item, RTT])

                # Quit all threads once a host is found
                for _ in range(num_threads + 1):
                    end_queue.put("quit")
            
            break

        except Empty:
            break

def port_scan_worker(queue, open_ports, end_queue):
    """Scans a port of a host, returning host and port if port open"""
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
