from graphviz import Digraph

class lan_viz():
    """Creates graphviz diagram for the LAN visualization"""

    dot = Digraph(comment="LAN Visualization", format="png", engine="circo")
    info_to_display = "{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}"

    def __init__(self, LAN_Dict_in):
        self.LAN_Dict = LAN_Dict_in

    def visualize_LAN(self):
        """Create Graphviz network from LAN hosts and display as image."""
   
        # Create the local host node
        local_host_IP = self.create_unique_node("Local Host")

        # Create the gateway node and connect it to the local host
        gateway_IP = self.create_unique_node("Gateway")
        self.dot.attr('edge', color='green')
        self.dot.edge(local_host_IP, gateway_IP)

        # Create nodes for hosts on the LAN with an edge to the local host
        self.create_host_nodes(local_host_IP)
        
        # Save and display graph
        self.dot.render('graphviz/LANvis.gv', view=True)

    def create_unique_node(self, node_desc):
        """Creates a special node based on node description."""
        
        try:
            IP = [host for host in self.LAN_Dict if self.LAN_Dict[host][4] == node_desc][0]
            RTT, MAC, manuf, comment, desc, open_ports = self.LAN_Dict[IP]
            label = self.info_to_display.format(node_desc, IP, RTT, MAC, manuf, comment, open_ports)

            # Do not include the node again
            del self.LAN_Dict[IP]
            
        except IndexError:
            IP = ""
            label = node_desc + " not found."

        self.dot.attr('node', color='green')
        self.dot.node(IP, label)

        return IP

    def create_host_nodes(self, local_host_IP):
        """Create nodes for hosts on the LAN with an edge to the local host."""

        max_nodes = 30
        nodes_created = 0
        for host in self.LAN_Dict:
            if nodes_created <= max_nodes:
                RTT, MAC, manuf, comment, desc, open_ports = self.LAN_Dict[host]

                # Color hosts found only through ARP blue, otherwise red
                if RTT == "null":
                    self.dot.attr('node', color='blue')
                    self.dot.attr('edge', color='blue')
                else:
                    self.dot.attr('node', color='red')
                    self.dot.attr('edge', color='red')

                host_label = self.info_to_display.format(host, RTT, MAC, manuf, comment, open_ports)

                self.dot.node(host, host_label)
                self.dot.edge(local_host_IP, host)

                nodes_created += 1
            else:
                break