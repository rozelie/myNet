from graphviz import Digraph

def visualize_LAN(LAN_Dict):
    dot = Digraph(comment="LAN Visualization", format="png", engine="circo")
    dot.attr('node', color='green')

    # Create the gateway node
    gateway_IP = [host for host in LAN_Dict if LAN_Dict[host][2] == "Gateway"][0]
    gateway_entry = LAN_Dict[gateway_IP]
    gateway_label = "Gateway\n{}\nRTT: {}\nMAC: {}".format(gateway_IP, gateway_entry[0], gateway_entry[1])
    dot.node(gateway_IP, gateway_label)

    del LAN_Dict[gateway_IP]

    # Create nodes for every host on LAN with an edge to the gateway
    for host in LAN_Dict:
        RTT, MAC, desc = LAN_Dict[host]

        # Color hosts found only through ARP blue, otherwise red
        if RTT == "null":
            dot.attr('node', color='blue')
            dot.attr('edge', color='blue')
        else:
            dot.attr('node', color='red')
            dot.attr('edge', color='red')

        host_label = ""
        if desc == "Local Host":
            host_label = "Local Host\n{}\nRTT: {}\nMAC: {}".format(host, RTT, MAC)
            dot.attr('node', color='green')
            dot.attr('edge', color='green')
        else:
            host_label = "{}\nRTT: {}\nMAC: {}".format(host, RTT, MAC)

        dot.node(host, host_label)
        dot.edge(host, gateway_IP)

    # Save and display graph
    dot.render('graphviz/LANvis.gv', view=True)