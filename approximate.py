import csv
import worker_threads
from queue import Queue, Empty
from threading import Thread
from statistics import mean
import mapping

def approximate_location():
    """Approximate user's location by finding shortest RTT of universities."""

    # Read in csv of universities
    uni_lookup = read_university_lookup_dict()

    # Get ping results of university hosts
    uni_RTT = ping_uni_hosts(uni_lookup)

    # Find the shortest average RTT of the pinged universities
    closest_uni, shortest_uni_RTT = get_closest_university(uni_RTT)
    print("Closest University: {}".format(closest_uni))
    print("Average University RTT: {}".format(str(round(shortest_uni_RTT, 2))))

    mapping.map_universities(uni_lookup, closest_uni)

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

    university_RTT = {}
    for uni, hosts_dict in iter(uni_lookup.items()):
        # Build a queue of all of the university's hosts
        queue = Queue()
        num_threads = 50
        hosts = [host for host, _ in iter(hosts_dict.items())]
        for addr in hosts:
            queue.put(addr)
        
        # Create threads that accumulate results in host_RTT
        end_queue = Queue()
        host_RTT = []
        threads = []
        for _ in range(num_threads):
            t = Thread(target=worker_threads.ping_worker, args=(queue, host_RTT, end_queue))
            t.start()
            threads.append(t)

        for thread in threads:
            thread.join()

        try:
            university_RTT[uni] = host_RTT
        except:
            pass

    return university_RTT

def get_closest_university(university_RTT):
    """Find the closest university based on average RTTs."""

    closest_uni = ''
    shortest_avg_RTT = 1000000
    for uni, host_RTTs in iter(university_RTT.items()):
        avg_RTT = mean([RTT for _, RTT in host_RTTs])
        
        if avg_RTT < shortest_avg_RTT:
            closest_uni = uni
            shortest_avg_RTT = avg_RTT
        
    return closest_uni, shortest_avg_RTT


approximate_location()