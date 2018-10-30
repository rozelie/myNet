from graphviz import Digraph

def visualize_LAN(LAN_hosts, local_IP, gateway_IP):
    dot = Digraph(comment="LAN Visualization", format="png")

    # Create the gateway node
    gateway_RTT = [LAN_hosts[i][1] for i in range(len(LAN_hosts)) if LAN_hosts[i][0] == gateway_IP][0]
    gateway_Label = "Gateway: {}\nRTT(s): {}".format(gateway_IP, str(round(gateway_RTT, 4)))
    dot.node(gateway_IP, gateway_Label)

    # Create nodes for every host on LAN with an edge to the gateway
    for host, RTT in LAN_hosts:
        if host != gateway_IP:
            if host == local_IP:
                hostLabel = "Local: " + host    
            else:
                hostLabel = host + "\nRTT(s): " + str(round(RTT, 4))
                
            dot.node(host, hostLabel)
            dot.edge(host, gateway_IP)

    # Save and display graph
    dot.render('graphviz/LANvis.gv', view=True)