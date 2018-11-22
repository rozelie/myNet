"""
http://staff.washington.edu/jon/python-course/python_traceroute.py
Phllip Calvin's python-traceroute.py, from http://gist.github.com/502451
based on Leonid Grinberg's traceroute, from
http://blog.ksplice.com/2010/07/learning-by-doing-writing-your-own-traceroute-in-8-easy-steps/
"""

import socket
import struct
import sys
import time

def run_trace(dest_name, max_hops=30):
    # print("Tracing to {} with {} maximum hops.".format(dest_name, max_hops))
    dest_addr = socket.gethostbyname(dest_name)
    port = 33434
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1

    responses = []
    trace_start = time.time()
    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        
        # Build the GNU timeval struct (seconds, microseconds)
        timeout = struct.pack("ll", 5, 0)
        
        # Set the receive timeout so we behave more like regular traceroute
        recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
        
        recv_socket.bind((b"", port))
        # print(" %d  " % ttl)
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
                # print("* ")
        
        send_socket.close()
        recv_socket.close()
        
        if not finished:
            pass
        
        if curr_addr is not None:
            curr_host = "%s (%s)" % (curr_name, curr_addr)
        else:
            curr_host = ""

        # print("%s\n" % (curr_host))
        if curr_host != "":
            trace_time_elapsed = round(time.time() - trace_start, 2)
            responses.append([curr_host, trace_time_elapsed])

        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            break

    return responses