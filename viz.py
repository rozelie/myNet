from graphviz import Digraph

def visualize_LAN(LAN_Dict):
    """Create Graphviz network from LAN hosts and display as image."""

    dot = Digraph(comment="LAN Visualization", format="png", engine="circo")
    info_to_display = "{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}"
    
    # Create the gateway node
    gateway_IP = create_gateway_node(LAN_Dict, dot, info_to_display)

    # Create nodes for hosts on the LAN with an edge to the gateway
    create_host_nodes(LAN_Dict, dot, info_to_display, gateway_IP)
    
    # Save and display graph
    dot.render('graphviz/LANvis.gv', view=True)

def create_gateway_node(LAN_Dict, dot, info_to_display):
    """Creates the gateway node that all other hosts will have an edge to."""
    
    try:
        gateway_IP = [host for host in LAN_Dict if LAN_Dict[host][4] == "Gateway"][0]
        gateway_RTT, gateway_MAC, gateway_manuf, gateway_comment, gateway_desc, gateway_open_ports = LAN_Dict[gateway_IP]
        gateway_label = info_to_display.format("Gateway", gateway_IP, gateway_RTT, gateway_MAC, gateway_manuf, gateway_comment, gateway_open_ports)

        # Do not include the gateway node again
        del LAN_Dict[gateway_IP]
        
    except IndexError:
        gateway_IP = ""
        gateway_label = "Gateway not found."

    dot.attr('node', color='green')
    dot.node(gateway_IP, gateway_label)

    return gateway_IP

def create_host_nodes(LAN_Dict, dot, info_to_display, gateway_IP):
    """Create nodes for hosts on the LAN with an edge to the gateway."""

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

            # Create the local host node
            host_label = ""
            if desc == "Local Host":
                host_label = info_to_display.format("Local Host", RTT, MAC, manuf, comment, open_ports)
                dot.attr('node', color='green')
                dot.attr('edge', color='green')
            else:
                host_label = info_to_display.format(host, RTT, MAC, manuf, comment, open_ports)

            dot.node(host, host_label)
            dot.edge(host, gateway_IP)

            nodes_created += 1
        else:
            break