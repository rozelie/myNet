import csv
import worker_threads
from queue import Queue, Empty
from threading import Thread
from statistics import mean

def approximate_location():
    university_lookup = get_university_lookup_dict()
    university_RTT = ping_university_hosts(university_lookup)
    closest_uni, uni_RTT = get_closest_university(university_RTT)
    print(closest_uni, uni_RTT)

def get_university_lookup_dict():
    university_lookup = {}
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

            university_lookup[uni] = host_location_dict

    return university_lookup

def ping_university_hosts(university_lookup):
    university_RTT = {}
    for uni, hosts_dict in iter(university_lookup.items()):
        # Build a queue of all of the university's hosts
        queue = Queue()
        num_threads = 50
        hosts = [host for host, _ in iter(hosts_dict.items())]
        for addr in hosts:
            queue.put(addr)
        
        # Create threads that accumulate results in ping_results
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
    closest_uni = ''
    shortest_avg_RTT = 1000000
    for uni, host_RTTs in iter(university_RTT.items()):
        avg_RTT = mean([RTT for _, RTT in host_RTTs])
        
        if avg_RTT < shortest_avg_RTT:
            closest_uni = uni
            shortest_avg_RTT = avg_RTT
        
    return closest_uni, shortest_avg_RTT


approximate_location()