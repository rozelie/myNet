#!/usr/bin/env python
"""Performs a trace route to remote server, returning
   hop addresses and RTTs. 

   Source: http://staff.washington.edu/jon/python-course/python_traceroute.py
"""

import socket
import struct
import sys
import time
from queue import Queue, Empty

def run_trace(dest_name, max_hops=30):

    # Setup traceroute
    dest_addr = socket.gethostbyname(dest_name)
    port = 33434
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1

    responses = []
   
    # Perform traceroute
    while True:
        trace_start = time.time()
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        # Build the GNU timeval struct (seconds, microseconds)
        timeout = struct.pack("ll", 2, 0)
        
        # Set the receive timeout so we behave more like regular traceroute
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
        
        recv_socket.bind((b"", port))
        send_socket.sendto(b"", (dest_name, port))
        curr_addr = None
        curr_name = None
        finished = False
        tries = 3
        while not finished and tries > 0:
            try:
                _, curr_addr = recv_socket.recvfrom(512)
                finished = True
                curr_addr = curr_addr[0]
                try:
                    curr_name = socket.gethostbyaddr(curr_addr)[0]
                except socket.error:
                    curr_name = curr_addr
            except socket.error:
                tries = tries - 1
        
        send_socket.close()
        recv_socket.close()
        
        if not finished:
            # responses.append(["*", 0])
            pass
        
        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = ""

        if curr_host != "":
            trace_time_elapsed = round(time.time() - trace_start, 2)
            responses.append([curr_host, trace_time_elapsed])

        if curr_addr == dest_addr:
            trace_time_elapsed = round(time.time() - trace_start, 2)
            responses.append([dest_name, trace_time_elapsed])
            break

        ttl += 1

        if ttl > max_hops:
            break

    print(dest_name, "traceroute completed.")

    return responses