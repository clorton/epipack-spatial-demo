import os

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml


basedir = os.path.join(os.path.dirname(__file__), "..")


params = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["configure"]

state = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["state"]
# state = "Nigeria"
# state = "Jigawa"

location_file = f"{state}_population_locations.csv"
df = pd.read_csv(os.path.join(basedir, "data", "parsed", location_file), index_col=0)


if state != "Nigeria":
    df = df[df.adm1_name==state]  # clip to boundary shape (not just bbox)

df = df[df.population > 0]  # drop NaN population nodes

# df = df[df['type'].isin(("Small Settlement Area", "Built-up Area"))]  # drop Hamlet nodes
df = df[df['type']=="Built-up Area"]  # only 67 BUAs in Jigawa w/ population from 1.8k to 172k

gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
# coordinates = np.column_stack((gdf.geometry.x, gdf.geometry.y))

print(gdf[['x', 'y', 'population']].head())
print(gdf.sort_values("population", ascending=False).head(10))
print(gdf.sort_values("population", ascending=False).tail(10))

plt.scatter(x=gdf.x, y=gdf.y, s=np.sqrt(gdf.population), c=np.sqrt(gdf.population), alpha=0.5, cmap='jet')

# from https://github.com/InstituteforDiseaseModeling/sandbox-ewenger/blob/master/mesoscale-test/mixing.py

earth_radius_km = 6367

def pairwise_haversine(df):

    """ pairwise distances for all (lon, lat) points """

    data = df[['x', 'y']].applymap(np.radians).to_numpy()  # N.B. conversion to radians
    lon = data[:, 0]
    lat = data[:, 1]

    # matrices of pairwise differences for latitudes & longitudes
    dlat = lat[:, None] - lat
    dlon = lon[:, None] - lon

    # vectorized haversine distance calculation
    d = np.sin(dlat/2)**2 + np.cos(lat[:, None])*np.cos(lat) * np.sin(dlon/2)**2
    return 2 * earth_radius_km * np.arcsin(np.sqrt(d))

distances = pairwise_haversine(gdf)

i_village = 0
x_threshold = 1.5
links = []

for i_village in range(len(gdf)):
    distance_from_village = distances[i_village]
    threshold = gdf.population.values[i_village] * x_threshold
    above_threshold = gdf.population.values > threshold
    distances_above_threshold = distance_from_village[above_threshold]

    ixs = np.where(above_threshold)[0]
    if len(ixs) == 0:
        continue
    j_village = ixs[np.argmin(distances_above_threshold)]

    links += [(i_village, j_village)]

print(links)

for i, j in links:
    x_i = gdf.iloc[i].x
    y_i = gdf.iloc[i].y
    x_j = gdf.iloc[j].x
    y_j = gdf.iloc[j].y
    plt.plot((x_i, x_j), (y_i, y_j), c='gray')

# TODO: refactor this code within configure_network.py
# nx.compose the two graphs together with relative weighting
# However, it appears that GeoDataFrame --> weights.KNN object --> networkx.DiGraph
# drops the gdf index, so different filters would result in different node IDs
# Also, some thought needs to go into whether graph should still be directional or not (?)
# In any case, pausing this project for a bit...

plt.show()