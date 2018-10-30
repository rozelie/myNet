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
    print("Pinging LAN Range {} to {} ...\n".format(start_LAN, end_LAN))

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