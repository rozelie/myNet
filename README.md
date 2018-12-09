# myNet
Combine functionalities of networking probes through custom and/or existing implementations to capture and view networking information and topologies within the LAN and beyond.

## Usage
All functionalities require root privileges for socket creations.

usage: myNet.py [-h] [-l] [-b] [-a]

optional arguments:
- -h, --help         show this help message and exit
- -l, --lan          view LAN information
- -b, --beyond       view information about networks beyond the LAN
- -a, --approximate  determine approximate location of machine

## Functionalities
### LAN
- Discovers local IP, gateway IP, gateway mask, and local network interface

- Pings IP addresses within the LAN
  - Creates a thread for each ping, cancelable via 'ctrl+c' interrupt

- Queries ARP cache to discover more hosts
  - Displays MAC and manufacturer info for each host

- Port scans all found local IPs from pings and ARP cache query
  - Creates a thread for each port scan, cancelable via 'ctrl+c' interrupt

- Generates a graph of information found about LAN hosts

### Beyond
- Discovers public IP address of the gateway

- Pings neighboring subnets (assumes /24 prefix of neighbors)
  - Only pings a sample of these neighboring subnets

- Generates a graph of neighboring subnets and their round-trip times

- Runs traceroutes to multiple servers across the world

- Generates a graph of the traceroutes

### Approximate
- Pings hundreds of universities that have their own autonomous systems

- Based on round-trip times (RTTs) of the universities, generates a color-coded map
  - Green:  Top ten closest RTTs
  - Yellow: First half of next closest RTTs
  - Red:    Last half of next closest RTTs

- Run university_lookup.py to update univeristy autonomous system lookup
    - Requires a valid IP2Location binary (must also alter path in university_lookup.add_host_location())

## Sources
- netifaces: https://pypi.org/project/netifaces/
- ICMP Packet and Ping Implementation: https://gist.github.com/pyos/10980172
- arpreq: https://pypi.org/project/arpreq/
- graphviz: https://pypi.org/project/graphviz/
- manuf library: https://github.com/coolbho3k/manuf
- trace_route: http://staff.washington.edu/jon/python-course/python_traceroute.py
- IP2Location: https://www.ip2location.com/developers/python