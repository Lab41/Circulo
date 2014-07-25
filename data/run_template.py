# This template should be copied and modified as necessary to become the 
# `run.py` in each directory. 
# 
# Do not modify this file unless the template needs changind -- modify
# its copies in each data directory. 


import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes


GRAPH_NAME = # Graph name goes here.
DOWNLOAD_URL = # url goes here.


def __download__(data_dir):
    """
    TEMPLATE COMMENT: downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DOWNLOAD_URL, GRAPH_NAME, data_dir)


def __prepare__(data_dir):
    """
    TEMPLATE COMMENT: prepare the data into graphml format.
    """
    raise(NotImplementedError)


def get_graph():
    """
    TEMPLATE COMMENT: Downloads and prepares a graph
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, GRAPH_NAME + ".graphml")

    if not os.path.exists(graph_path):
        __download__(data_dir)
        __prepare__(data_dir)
    else:
        print(graph_path, "already exists. Using old file.")

    return igraph.load(graph_path)


def get_ground_truth(G=None):
    """
    TEMPLATE COMMENT: returns a VertexClustering object of the 
    ground truth of the graph G.
    """
    raise(NotImplementedError)

    # if G is None:
    #     G = get_graph()

    # return # VertexClustering(G, membership)


def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
