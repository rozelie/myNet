import subprocess
import bin_tools
import worker_threads
from queue import Queue, Empty
from threading import Thread
import IP2Location #https://www.ip2location.com/developers/python

# Leveraged to find IP's associated with a university's IP:
#   https://www.quora.com/Is-there-a-way-to-find-all-the-IP-blocks-associated-with-a-university

def create_university_lookup():
    """Find university AS, find pingable hosts within AS, then export to csv."""

    uni_AS_dict = get_uni_AS()
    uni_IP_subnet_dict = get_uni_IP_subnet(uni_AS_dict)
    print("IPs and subnets found")
    
    # test = {'Carnegie Mellon University': ['209.129.244.0', '23']}

    uni_pingable_hosts = find_pingable_hosts(uni_IP_subnet_dict)
    
    uni_pingable_hosts = add_host_location(uni_pingable_hosts)
    
    write_hosts_to_file(uni_pingable_hosts)
    
def get_uni_AS():
    """Retrieve names of universities and their Autonomous System (AS) number from maxmind.com."""

    # Adapted from https://stackoverflow.com/questions/13332268/python-subprocess-command-with-pipe
    AS_uni_cmd = 'curl -s http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2.zip | gunzip | cut -d"," -f3 | sed \'s/"//g\' | sort -u | grep \'University\''
    AS_uni_proc = subprocess.Popen(AS_uni_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    AS_uni_out = str(AS_uni_proc.communicate()[0])

    # Remove leading 'b'
    AS_uni_out = AS_uni_out[1:]

    AS_uni_split = AS_uni_out.split("\\n")

    # Build dict of {university : AS}
    uni_AS_dict = {}
    for AS_uni in AS_uni_split:
        if AS_uni != '"':
            AS = AS_uni.split(" ")[0]
            uni_name = ' '.join(AS_uni.split(" ")[1:])
            uni_AS_dict[uni_name] = AS

    return uni_AS_dict

def get_uni_IP_subnet(uni_AS_dict):
    """Leverage 'whois' to get a subnet associated with university AS."""

    uni_IP_subnet_dict = {}
    for uni, AS in iter(uni_AS_dict.items()):
        whois_AS_cmd = 'whois -h whois.radb.net -- \'-i origin ' + AS + '\' | grep -Eo "([0-9.]+){4}/[0-9]+"'
        whois_AS_proc = subprocess.Popen(whois_AS_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        whois_AS_out = str(whois_AS_proc.communicate()[0])

        # Remove leading "b'"
        whois_AS_out = whois_AS_out[2:]

        whois_AS_first_IP_range = whois_AS_out.split("\\n")[0]

        if whois_AS_first_IP_range != "'":
            uni_IP_subnet_dict[uni] = whois_AS_first_IP_range.split("/")

    return uni_IP_subnet_dict

def find_pingable_hosts(uni_IP_subnet_dict):
    """Ping hosts within university subnets to gather hosts that respond to pings."""

    uni_pingable_hosts = {}
    for uni, (subnet, mask) in iter(uni_IP_subnet_dict.items()):

        # Get all possible IPv4 addresses within subnet
        subnet_possibilities = get_possible_subnet_addrs(subnet, mask)

        # Build a queue of all of the subnet addresses
        queue = Queue()
        for addr in subnet_possibilities:
            queue.put(addr)
        
        # Create threads that accumulate results in pingable_hosts
        end_queue = Queue()
        num_threads = 200
        pingable_hosts = []
        threads = []
        for _ in range(num_threads):
            t = Thread(target=worker_threads.ping_worker_end_if_found, args=(queue, pingable_hosts, end_queue, num_threads))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        try:
            hosts_dict = {host : [0, 0] for host, _ in pingable_hosts}
            uni_pingable_hosts[uni] = hosts_dict
        except:
            pass
        
    return uni_pingable_hosts

def get_possible_subnet_addrs(subnet, mask):
    """Get all possible IPv4 addresses within subnet."""

    mask = int(mask)
        
    bin_possibilities = bin_tools.bin_combinations(32 - mask)

    # Exclude the first and last addresses of the subnet: x.x.x.0 and x.x.x.255
    # x.x.x.0 is usually not used by convention and x.x.x.255 is reserved for a broadcast address
    bin_possibilities = bin_possibilities[1:-1]

    # Get the entire binary representation of all possible subnet IPv4 addresses
    subnet_bin = bin_tools.quad_to_bin_str(subnet)
    subnet_possibilities_bin = []
    for combo in bin_possibilities:
        subnet_possibilities_bin.append(subnet_bin[:mask] + combo)

    # Transform binary addresses to IPv4
    subnet_possibilities = [bin_tools.bin_to_dotted_quad(i) for i in subnet_possibilities_bin]

    return subnet_possibilities

def add_host_location(uni_pingable_hosts):
    """Add host's latitude and longitude to dictionary."""

    # Open IP2Location binary
    IP2LocObj = IP2Location.IP2Location()
    IP2LocObj.open("IP2LOCATION-LITE-DB5.BIN")
    
    for uni, hosts_dict in iter(uni_pingable_hosts.items()):
        for host, _ in iter(hosts_dict.items()):
            
            record = IP2LocObj.get_all(host)         
            if record:
                hosts_dict[host] = [record.latitude, record.longitude]
            else:
                # Delete host that does not have a location
                del hosts_dict[host]

        uni_pingable_hosts[uni] = hosts_dict

    return uni_pingable_hosts

def write_hosts_to_file(uni_pingable_hosts):
    """Write university host locations to csv."""

    with open('university_hosts.csv', mode='w') as hosts_file:
        # Create csv rows in format 'university, host_addr: latitude longitude'
        for uni, hosts in iter(uni_pingable_hosts.items()):
            host_loc_str = ','
            for addr, loc in iter(hosts.items()):
                host_loc_str += addr + ":" + ' '.join([str(i) for i in loc]) + ","

            host_loc_str = host_loc_str[:-1]
            hosts_file.write(uni + host_loc_str + "\n")

    print("{} university hosts written to csv.".format(len(uni_pingable_hosts)))

create_university_lookup()