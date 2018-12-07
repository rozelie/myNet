import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pandas as pd

def plot_approximate_location(sorted_unis):
    num_unis_to_plot = 5
    lat_min, lat_max, long_min, long_max = get_map_bounds(sorted_unis, num_unis_to_plot)
    
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

    world = world.cx[long_min:long_max, lat_min:lat_max]

    uni_points = get_uni_points(sorted_unis, num_unis_to_plot)

    ax = world.plot(color='white', edgecolor='black')

    uni_points.plot(ax=ax, color='red', markersize=1)

    plt.show()

def get_uni_points(sorted_unis, num_unis_to_plot):

    locations_dict = {'Latitude' : [], 'Longitude' : []}
    unis = sorted_unis[:num_unis_to_plot]
    for uni in unis:
        coords = uni[2]
        lat = float(coords[0])
        long_ = float(coords[1])
        locations_dict['Latitude'].append(lat)
        locations_dict['Longitude'].append(long_)

    df = pd.DataFrame(locations_dict)
    df['Coordinates'] = list(zip(df.Longitude, df.Latitude))
    df['Coordinates'] = df['Coordinates'].apply(Point)
    uni_points = geopandas.GeoDataFrame(df, geometry='Coordinates')

    return uni_points

def get_map_bounds(sorted_unis, num_unis_to_plot):
    unis = sorted_unis[:num_unis_to_plot]

    # Get bounds for map
    lat_min = 1000
    lat_max = -1000
    long_min = 1000
    long_max = -1000
    for uni in unis:
        coords = uni[2]
        lat = float(coords[0])
        long_ = float(coords[1])

        if lat < lat_min:
            lat_min = lat
        if lat > lat_max:
            lat_max = lat

        if long_ < long_min:
            long_min = long_
        if long_ > long_max:
            long_max = long_

    # Extend the map along all edges a fixed amount
    bounds_buffer = 0
    return lat_min + bounds_buffer, lat_max - bounds_buffer, long_min + bounds_buffer, long_max - bounds_buffer