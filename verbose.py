def LAN_start():
    print("BEGIN LAN HOST RETRIEVAL")
    print("========================\n")

def LAN_no_info():
    print("Unable to obtain LAN information.")

def LAN_info(local_IP, gateway_IP, gateway_mask, interface):
    print("{:16} {:16} {:16} {}".format("Local IP", "Gateway IP", "Gateway Mask", "Interface"))
    print("*" * 60)
    print("{:16} {:16} {:16} {}\n".format(local_IP, gateway_IP, gateway_mask, interface))

def LAN_ping_start(start_LAN, end_LAN):
    print("Pinging LAN Range {} to {} ...".format(start_LAN, end_LAN))

def LAN_ping_results(ping_time_elapsed, LAN_hosts, local_IP, gateway_IP):
    print("LAN Ping Elapsed Time:", ping_time_elapsed, "seconds\n")
    print("{:16} {:8} {}".format("Host", "RTT(s)", "Description"))  
    print("*" * 37)      
    for host, RTT in LAN_hosts:
        description = ""
        if host == local_IP:
            description = "Local Host"
        elif host == gateway_IP:
            description = "Gateway"

        print("{:16} {:8} {}".format(host, str(round(RTT, 3)), description))
    print()

def LAN_ARP_start(start_LAN, end_LAN):
    print("ARP request of the LAN Range {} to {} ...".format(start_LAN, end_LAN))

def LAN_ARP_results(ARP_time_elapsed, ARP_hosts, local_IP, gateway_IP):
    print("ARP Requests Elapsed Time:", ARP_time_elapsed, "seconds\n")
    print("{:16} {:18} {}".format("Host", "MAC", "Description"))  
    print("*" * 46)      
    for host, MAC in ARP_hosts:
        description = ""
        if host == local_IP:
            description = "Local Host"
        elif host == gateway_IP:
            description = "Gateway"

        print("{:16} {:18} {}".format(host, MAC, description))
    print()

def LAN_port_scan_start():
    print("Beginning LAN port scanning.")

def LAN_port_scan_results(port_scan_elapsed, open_ports):
    print("Port Scan Elapsed Time:", port_scan_elapsed, "seconds\n")
    # print("{:16} {:18} {}".format("Host", "MAC", "Description"))  
    # print("*" * 46)      
    # for host, MAC in ARP_hosts:
    #     description = ""
    #     if host == local_IP:
    #         description = "Local Host"
    #     elif host == gateway_IP:
    #         description = "Gateway"

    #     print("{:16} {:18} {}".format(host, MAC, description))
    print()