import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from itertools import chain
import numpy as np

# Mapping functionalities adapted from:
#   https://jakevdp.github.io/PythonDataScienceHandbook/04.13-geographic-data-with-basemap.html

def map_universities(uni_locations, closest_uni):
    fig = plt.figure(figsize=(8, 6), edgecolor='w')
    m = Basemap(projection='cyl', resolution=None,
                llcrnrlat=-90, urcrnrlat=90,
                llcrnrlon=-180, urcrnrlon=180, )
    
    for _, hosts_location in iter(uni_locations.items()):
        uni_host = [host for host, _ in iter(hosts_location.items())][0]
        lat, long_ = hosts_location[uni_host]
        m.scatter(long_, lat, latlon=True, color='red', alpha=0.5)

    closest_uni_hosts = hosts_location[closest_uni]
    closest_uni_host = [host for host, _ in iter(closest_uni.items())][0]
    closest_lat, closest_long = closest_uni_hosts[closest_uni_host]
    m.scatter(closest_long, closest_lat, latlon=True, color='green', alpha=0.5)

    draw_map(m)

def draw_map(m, scale=0.2):
    # draw a shaded-relief image
    m.shadedrelief(scale=scale)
    
    # lats and longs are returned as a dictionary
    lats = m.drawparallels(np.linspace(-90, 90, 13))
    lons = m.drawmeridians(np.linspace(-180, 180, 13))

    # keys contain the plt.Line2D instances
    lat_lines = chain(*(tup[1][0] for tup in lats.items()))
    lon_lines = chain(*(tup[1][0] for tup in lons.items()))
    all_lines = chain(lat_lines, lon_lines)
    
    # cycle through these lines and set the desired style
    for line in all_lines:
        line.set(linestyle='-', alpha=0.3, color='w')