# myNet
[In development] Combine functionalities of networking probes through custom and/or existing implementations to capture and view networking information and topologies within the LAN and beyond.

## Usage
usage: myNet.py [-h] [-l] [-b] [-a] [-vis] [-v]

optional arguments:
- -h, --help         show this help message and exit
- -l, --lan          view LAN information
- -b, --beyond       view information about networks beyond the LAN [in development]
- -a, --approximate  determine approximate location of machine [in development]
- -vis, --visualize  visualize information from -l or -b
- -v, --verbose      increase verbosity of output

## Sources
- netifaces: https://pypi.org/project/netifaces/
- ICMP Packet and Ping Implementation: https://gist.github.com/pyos/10980172
- arpreq: https://pypi.org/project/arpreq/
- graphviz: https://pypi.org/project/graphviz/
- manuf library: https://github.com/coolbho3k/manuf
- trace_route: http://staff.washington.edu/jon/python-course/python_traceroute.py
- IP2Location: #https://www.ip2location.com/developers/python