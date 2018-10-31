import socket
import time
import subprocess
import sys
from datetime import datetime

def get_open_ports(remote_IP):
    """ """
    # Adapted from https://www.pythonforbeginners.com/code-snippets-source-code/port-scanner-in-python
    skipped_ports = [1, 22, 23]
    ports_to_try = [i for i in range(1,1025) if i not in skipped_ports]
    
    open_ports = []
    for port in ports_to_try:  
        # print(remote_IP, port)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((remote_IP, port))

        if result == 0:
            open_ports.append(str(port))
        sock.close()

    result_ports = [remote_IP]
    result_ports.append(open_ports)
    return result_ports
