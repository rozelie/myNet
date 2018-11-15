from graphviz import Digraph

def visualize_LAN(LAN_Dict):
    """ Create Graphviz network from LAN hosts and display as image. """

    dot = Digraph(comment="LAN Visualization", format="png", engine="circo")
    
    # Create the gateway node
    try:
        gateway_IP = [host for host in LAN_Dict if LAN_Dict[host][4] == "Gateway"][0]
        gateway_RTT, gateway_MAC, gateway_manuf, gateway_comment, gateway_desc, gateway_open_ports = LAN_Dict[gateway_IP]
        gateway_label = "Gateway\n{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}".format(gateway_IP, gateway_RTT, gateway_MAC,
                                                                                                                        gateway_manuf, gateway_comment, gateway_open_ports)

        # Do not include the gateway node again
        del LAN_Dict[gateway_IP]
        
    except IndexError:
        gateway_IP = ""
        gateway_label = "Gateway not found."

    dot.attr('node', color='green')
    dot.node(gateway_IP, gateway_label)

    # Create nodes for every host on LAN with an edge to the gateway
    max_nodes = 30
    nodes_created = 0
    for host in LAN_Dict:
        if nodes_created <= max_nodes:
            RTT, MAC, manuf, comment, desc, open_ports = LAN_Dict[host]

            # Color hosts found only through ARP blue, otherwise red
            if RTT == "null":
                dot.attr('node', color='blue')
                dot.attr('edge', color='blue')
            else:
                dot.attr('node', color='red')
                dot.attr('edge', color='red')

            host_label = ""
            if desc == "Local Host":
                host_label = "Local Host\n{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}".format(host, RTT, MAC, manuf, comment, open_ports)
                dot.attr('node', color='green')
                dot.attr('edge', color='green')
            else:
                host_label = "{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}".format(host, RTT, MAC, manuf, comment, open_ports)

            dot.node(host, host_label)
            dot.edge(host, gateway_IP)

            nodes_created += 1
        else:
            break

    # Save and display graph
    dot.render('graphviz/LANvis.gv', view=True)