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


GRAPH_NAME = 'PGPgiantcompo'
DOWNLOAD_URL = 'http://deim.urv.cat/~aarenas/data/xarxes/PGP.zip'


def __download__(data_dir):
    """
    Downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DOWNLOAD_URL, GRAPH_NAME, data_dir)


def __prepare__(data_dir):
    """
    """
    pass


def get_graph():
    """
    TEMPLATE COMMENT: Downloads and prepares a graph
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, GRAPH_NAME + ".net")

    if not os.path.exists(graph_path):
        __download__(data_dir)
        __prepare__(data_dir)
    else:
        print(graph_path, "already exists. Using old file.")

    return igraph.load(graph_path)


def get_ground_truth(G=None):
    """
    returns a VertexClustering object of the 
    ground truth of the graph G.
    """
    raise(NotImplementedError)


def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
