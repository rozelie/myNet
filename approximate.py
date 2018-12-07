import csv
import worker_threads
from queue import Queue, Empty
from threading import Thread
from statistics import mean
import IP2Location #https://www.ip2location.com/developers/python
import mapping

def approximate_location():
    """Approximate user's location by finding shortest RTT of universities."""

    # Read in csv of universities
    uni_lookup = read_university_lookup_dict()

    # Get ping results of university hosts
    uni_RTT = ping_uni_hosts(uni_lookup)

    # Find the shortest average RTT of the pinged universities
    sorted_unis = sort_universities(uni_RTT, uni_lookup)

    print_closest_unis(sorted_unis, uni_lookup)

    sorted_unis_location = add_location(sorted_unis, uni_lookup)

    # test = [['South Suburban College of Cook County', 0.034956863948277066, ['41.600868', '-87.606987']], ['University of Illinois at Urbana-Champaign', 0.03752471179496951,['40.111023', '-88.19706']], ['Lake Michigan College', 0.03934621810913086, ['42.201721', '-85.59462']], ['College of duPage', 0.04018974304199219, ['41.785858', '-88.147293']], ['State Fair Community College', 0.04199028015136719, ['39.227249', '-92.846581']]]

    mapping.plot_approximate_location(sorted_unis_location)

def read_university_lookup_dict():
    """Builds dictionary from university hosts file."""

    uni_lookup = {}
    with open('university_hosts.csv', mode='r') as hosts_file:
        reader = csv.reader(hosts_file, delimiter=',')
        
        for row in reader:
            uni = row[0]
            uni_hosts = row[1:]

            host_location_dict = {}
            for host_info in uni_hosts:
                addr, location = host_info.split(":")
                location = location.split(" ")
                host_location_dict[addr] = location

            uni_lookup[uni] = host_location_dict

    return uni_lookup

def ping_uni_hosts(uni_lookup):
    """Record RTT of pinged university hosts."""
    print("Pinging universities...")
    university_RTT = {}

    # Build a queue of all of the university's hosts
    queue = Queue()
    for uni, hosts_dict in iter(uni_lookup.items()):   
        hosts = [host for host, _ in iter(hosts_dict.items())]
        for addr in hosts:
            queue.put([uni, addr])

    # Create threads that accumulate results in host_RTT
    end_queue = Queue()
    num_threads = 200
    host_RTT = []
    threads = []
    for _ in range(num_threads):
        t = Thread(target=worker_threads.ping_worker_unis, args=(queue, host_RTT, end_queue))
        t.start()
        threads.append(t)

    for thread in threads:
        thread.join()

    for uni, _, RTT in host_RTT:
        if uni in university_RTT:
            university_RTT[uni].append(RTT)
        else:
            university_RTT[uni] = [RTT]

    print("University pings completed.\n")
    return university_RTT

def sort_universities(university_RTT, uni_lookup):
    """Find the closest university based on average RTTs."""

    for uni, RTTs in iter(university_RTT.items()):
        university_RTT[uni] = mean(RTTs)

    sorted_unis = []
    for uni in sorted(university_RTT, key=university_RTT.get, reverse=False):
        sorted_unis.append([uni, university_RTT[uni]])

    return sorted_unis

def add_location(sorted_unis, uni_lookup):
    """Add location of universities based on the lookup."""

    sorted_unis_location = []
    for uni, RTT in sorted_unis:
        uni_info_dict = uni_lookup[uni]
        coordinates = [coords for host, coords in iter(uni_info_dict.items())][0]
        sorted_unis_location.append([uni, RTT, coordinates])

    return sorted_unis_location

def print_closest_unis(sorted_unis, uni_lookup):
    """Prints the closest universities, their avg. RTT, and location."""

    # Open IP2Location binary
    IP2LocObj = IP2Location.IP2Location()
    IP2LocObj.open("IP2LOCATION-LITE-DB5.BIN")

    print("Ten Closest Universities and RTT:")
    header_str = "{:35} {:5}   {}".format("University", "Avg. RTT", "Location")
    print(header_str)
    print("=" * len(header_str))

    for i in range(10):
        uni_name = sorted_unis[i][0]
        uni_RTT = sorted_unis[i][1] 

        # Get the first IP address associated with the university
        uni_hosts = uni_lookup[uni_name]
        uni_IP = [host for host, _ in iter(uni_hosts.items())][0]

        # Lookup the location of the IP address
        record = IP2LocObj.get_all(uni_IP)         
        location = str(record.city)[2:-1] + ", " + str(record.country_long)[2:-1]

        # Trim university name to fit format
        if len(uni_name) > 35:
            uni_name = uni_name[:32] + "..."
        
        print("{:35} {:8}   {}".format(uni_name, str(round(uni_RTT, 3)), location))
