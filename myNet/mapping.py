#!/usr/bin/env python
"""Performs approximate (-b) mapping functions through 
   generating a geopandas mapped based on RTT of university
   host pings. 
"""

import geopandas
import matplotlib.pyplot as plt
from shapely.geometry import Point
import pandas as pd

def plot_approximate_location(sorted_unis):
    """Create color-coded geopandas map based on RTT"""
    
    # Plot blank world map
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    ax = world.plot(color='white', edgecolor='black')

    # Build GeoDataFrame of university locations
    uni_points = get_uni_points(sorted_unis)

    # Split the universities based on RTT
    closest_ten_unis, yellow_unis, red_unis = split_unis(uni_points)

    # Plot the universities
    closest_ten_unis.plot(ax=ax, color='green', markersize=15)
    yellow_unis.plot(ax=ax, color='yellow', markersize=5)
    red_unis.plot(ax=ax, color='red', markersize=1)

    plt.show()

def get_uni_points(sorted_unis):
    """Create GeoDataFrame of the university locations"""

    locations_dict = {'Latitude' : [], 'Longitude' : []}
    for uni in sorted_unis:
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

def split_unis(uni_points):
    """Split university locations based on their RTT (list already sorted by RTT)"""

    # Split universities into three groups:
    #   green:  ten closest
    #   yellow: first half of closest remaining universities
    #   red:    last half of closest remaining universities
    closest_ten_unis = uni_points.loc[:10]

    uni_points = uni_points.loc[10:]
    split_size = int(len(uni_points) / 2)

    yellow_unis = uni_points.loc[:split_size]
    red_unis = uni_points.loc[split_size:]

    return closest_ten_unis, yellow_unis, red_unis