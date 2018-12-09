from graphviz import Digraph
import lan

class lan_viz():
    """Creates graphviz diagram for the LAN visualization."""

    def __init__(self, LAN_Dict_in):
        self.LAN_Dict = LAN_Dict_in
        self.dot = Digraph(comment="LAN Visualization", format="png", engine="circo")
        self.node_info = "{}\nRTT: {}\nMAC: {}\nManufacturer: {}\nProduct Description: {}\nOpen Ports:{}"

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
            RTT, MAC, manuf, comment, _, open_ports = self.LAN_Dict[IP]
            label = self.node_info.format(node_desc + " (" + IP + ")", RTT, MAC, manuf, comment, open_ports)

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
                RTT, MAC, manuf, comment, _, open_ports = self.LAN_Dict[host]

                # Color hosts found only through ARP blue, otherwise red
                if RTT == "null":
                    self.dot.attr('node', color='blue')
                    self.dot.attr('edge', color='blue')
                else:
                    self.dot.attr('node', color='red')
                    self.dot.attr('edge', color='red')

                host_label = self.node_info.format(host, RTT, MAC, manuf, comment, open_ports)

                self.dot.node(host, host_label)
                self.dot.edge(local_host_IP, host)

                nodes_created += 1
            else:
                break

class neighboring_subnets():
    """Creates graphviz diagram for the neighboring subnets visualization."""

    def __init__(self, ping_res, gateway_IP):
        self.ping_res = ping_res
        self.gateway_IP = gateway_IP
        self.dot = Digraph(comment="Neighboring Subnets Visualization", format="png", engine="circo")
        self.node_info = "{}\nRTT: {}"

    def visualize_neighbors(self):
        # Create the gateway node
        self.dot.attr('node', color='green')
        self.dot.node(self.gateway_IP, "Local Gateway\n" + self.gateway_IP)

        for subnet, found_hosts in iter(self.ping_res.items()):
            if found_hosts:
                # Connect gateway to a subnet node
                self.dot.attr('node', color='red')
                self.dot.node(subnet, subnet)
                self.dot.edge(self.gateway_IP, subnet)
                    
                # Connect each subnet host to the subnet node
                for host in found_hosts:
                    self.dot.attr('node', color='blue')
                    host_IP = host[0]
                    host_RTT = str(round(host[1], 2))
                    host_label = self.node_info.format(host_IP, host_RTT)

                    self.dot.node(host_IP, host_label)
                    self.dot.edge(subnet, host_IP)

        # Save and display graph
        self.dot.render('graphviz/neighbors_vis.gv', view=True)
                    
class beyond_viz():
    """Creates graphviz diagram for the traceroute visualization."""

    def __init__(self, trace_res):
        self.trace_res = trace_res
        self.dot = Digraph(comment="Beyond Visualization", format="png")
        self.node_info = "{}\nRTT: {}"

        # Get local IP for future usage
        self.local_IP, _, __ = lan.basic_info()
 

    def visualize_traceroute(self):
        """Create diagram of traceroute nodes"""

        # Create the local host node
        self.dot.attr('node', color='green')
        self.dot.node(self.local_IP, "Local Host\n" + self.local_IP)

        for server in self.trace_res:
            last_host = self.local_IP

            for host, RTT in self.trace_res[server]:
                host_label = self.node_info.format(host, RTT)
                self.dot.node(host, host_label)
                self.dot.edge(last_host, host)
                last_host = host

        # Save and display graph
        self.dot.render('graphviz/beyond_vis.gv', view=True)