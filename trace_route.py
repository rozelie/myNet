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


# def run_trace_threads(queue, trace_res, end_queue, max_hops=30):
#     while True:
#         try:
#             try:
#                 end_queue.get(block=True, timeout = 1)
#                 break
#             except Empty:
#                 pass

#             # Get destination from queue
#             dest_name, port = queue.get(block=True, timeout = 1)
#             queue.task_done()

#             # Setup traceroute
#             dest_addr = socket.gethostbyname(dest_name)
#             # port = 33434
#             icmp = socket.getprotobyname('icmp')
#             udp = socket.getprotobyname('udp')
#             ttl = 1

#             responses = []
#             trace_start = time.time()

#             # Perform traceroute
#             while True:
#                 recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
#                 send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
#                 send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                
#                 # Build the GNU timeval struct (seconds, microseconds)
#                 timeout = struct.pack("ll", 5, 0)
                
#                 # Set the receive timeout so we behave more like regular traceroute
#                 recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)
                
#                 recv_socket.bind((b"", port))
#                 send_socket.sendto(b"", (dest_name, port))
#                 curr_addr = None
#                 curr_name = None
#                 finished = False
#                 tries = 3
#                 while not finished and tries > 0:
#                     try:
#                         _, curr_addr = recv_socket.recvfrom(512)
#                         finished = True
#                         curr_addr = curr_addr[0]
#                         try:
#                             curr_name = socket.gethostbyaddr(curr_addr)[0]
#                         except socket.error:
#                             curr_name = curr_addr
#                     except socket.error:
#                         tries = tries - 1
                
#                 send_socket.close()
#                 recv_socket.close()
                
#                 if not finished:
#                     pass
                
#                 if curr_addr is not None:
#                     curr_host = "%s (%s)" % (curr_name, curr_addr)
#                 else:
#                     curr_host = ""

#                 if curr_host != "":
#                     trace_time_elapsed = round(time.time() - trace_start, 2)
#                     responses.append([curr_host, trace_time_elapsed])

#                 ttl += 1
#                 if curr_addr == dest_addr or ttl > max_hops:
#                     break


#             print(dest_name, "traceroute completed.")

#             # Add to dict the traced hosts and their RTT
#             print(dest_name, ":", responses)
#             for found_host, RTT in responses:
#                 hop_info = [found_host, RTT]
                
#                 if dest_name in trace_res:
#                     hop_already_found = False

#                     for host_found, _ in trace_res[dest_name]:
#                         if found_host == host_found:
#                             hop_already_found = True
#                             break

#                     if not hop_already_found:
#                         trace_res[dest_name].append(hop_info)

#                 else:
#                     trace_res[dest_name] = [hop_info]

#         except Empty:
#             break

def run_trace_to_uni(queue, trace_res, end_queue):
    while True:
        try:
            try:
                end_queue.get(block=True, timeout = 1)
                break
            except Empty:
                pass

            # Get destination from queue
            dest_name, ttl = queue.get(block=True, timeout = 1)
            queue.task_done()
            print(dest_name, ttl)

            # Setup traceroute
            dest_addr = socket.gethostbyname(dest_name)
            port = 33434
            icmp = socket.getprotobyname('icmp')
            udp = socket.getprotobyname('udp')

            trace_start = time.time()

            # Perform traceroute
            while True:
                recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
                send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)
                send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                
                # Build the GNU timeval struct (seconds, microseconds)
                timeout = struct.pack("ll", 5, 0)
                
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
                    pass
                
                if curr_addr is not None:
                    curr_host = "%s (%s)" % (curr_name, curr_addr)
                else:
                    curr_host = ""

                if curr_host != "":
                    trace_time_elapsed = round(time.time() - trace_start, 2)
                    host_responses = trace_res[dest_name]
                    host_responses[ttl] = [curr_host, trace_time_elapsed]
                    break
                else:
                    host_responses = trace_res[dest_name]
                    host_responses[ttl] = ["*", 0]
                    break

        except Empty:
            break