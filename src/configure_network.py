import logging
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from libpysal import weights
import networkx as nx
import netwulf as nw
import yaml


basedir = os.path.join(os.path.dirname(__file__), "..")


def repair_graph(G_in):
    """ 
    _json_default only converts np.int64 and np.float64
    https://github.com/benmaier/netwulf/blob/master/netwulf/interactive.py#L30
    """
    G_out = nx.DiGraph()

    G_out.graph = G_in.graph

    for n, nd in G_in.nodes(data=True):
        G_out.add_node(n, **nd)

    for e1, e2, ed in G_in.edges(data=True):
        G_out.add_edge(e1, int(e2), **ed)  # np.int32 -> int :(
        
    return G_out


def visualize(G):

    stylized_network = nx.node_link_data(G)
    logging.debug(stylized_network["links"][0])
    logging.debug(stylized_network["nodes"][0])

    xmin, xmax = G.graph["xlim"]
    ymin, ymax = G.graph["ylim"]

    xwidth, ywidth, padding = 821, 821, 10
    stylized_network["xlim"] = (0, xwidth)
    stylized_network["ylim"] = (0, ywidth)
    for n in stylized_network["nodes"]:
        n["x_canvas"] = padding + (xwidth-2*padding) * (n["x"] - xmin) / (xmax - xmin)
        n["y_canvas"] = padding + (ywidth-2*padding) * (n["y"] - ymin) / (ymax - ymin)
        # n["radius"] = 0.75
        n["radius"] = 1.0 * np.log10(n["pop"])
    for l in stylized_network["links"]:
        l["width"] = 0.25
    stylized_network["linkAlpha"] = 0.2

    config = nw.default_config
    config.update(dict(node_stroke_width=0))  # for better visibility of partly overlapping nodes

    return stylized_network, config


def generate_network(df, state, k):
    
    """ Adapted from https://networkx.org/documentation/stable/auto_examples/geospatial/plot_points.html """

    if state != "Nigeria":
        df = df[df.adm1_name==state]  # clip to boundary shape (not just bbox)

    df = df[df.population > 0]  # drop NaN population nodes

    df = df[df['type'].isin(("Small Settlement Area", "Built-up Area"))]  # drop Hamlet nodes

    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.x, df.y))
    coordinates = np.column_stack((gdf.geometry.x, gdf.geometry.y))

    ## k-nearest-neighbor graph
    knn_graph = weights.KNN.from_dataframe(gdf, k=k).to_networkx()
    nx.set_node_attributes(knn_graph, dict(zip(knn_graph.nodes, coordinates[:, 0])), 'x')
    nx.set_node_attributes(knn_graph, dict(zip(knn_graph.nodes, coordinates[:, 1])), 'y')
    nx.set_node_attributes(knn_graph, dict(zip(knn_graph.nodes, gdf.population)), 'pop')
    knn_graph.graph.update(dict(xlim=(coordinates[:, 0].min(), coordinates[:, 0].max()),
                                ylim=(coordinates[:, 1].min(), coordinates[:, 1].max())))
    logging.debug(list(knn_graph.nodes(data=True))[:3])
    logging.debug(list(knn_graph.edges(data=True))[:3])
    logging.debug(knn_graph.graph)

    # Set some netwulf display parameters ourselves without using GUI
    stylized_network, config = visualize(repair_graph(knn_graph))

    # Spawns netwulf GUI, which is really cool, but seems to have some bugs with "freeze" settings?
    # https://netwulf.readthedocs.io/en/latest/python_api/data_io.html
    # stylized_network, config = nw.visualize(repair_graph(knn_graph))

    os.makedirs(os.path.join(basedir, "data", "configured"), exist_ok=True)    
    nw.save(os.path.join(basedir, "data", "configured", f"{state}_knn_graph.json"), stylized_network, config)


if __name__ == '__main__':

    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    params = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["configure"]

    # state = "Jigawa"
    # state = "Nigeria"
    state = yaml.safe_load(open(os.path.join(basedir, "params.yaml")))["state"]

    location_file = f"{state}_population_locations.csv"
    df = pd.read_csv(os.path.join(basedir, "data", "parsed", location_file), index_col=0)
    logging.debug(df.head())

    generate_network(df, state, k=params["knn"])

    plt.show()