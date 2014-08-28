import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes


ZIP_NAME = "Davis-GraphML.zip"
DOWNLOAD_URL = "http://nexus.igraph.org/api/dataset?id=23&format=GraphML"

GRAPH_NAME = "davis"
GRAPH_TYPE = ".graphml"

def __download__(data_dir):
    """
    TEMPLATE COMMENT: downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DOWNLOAD_URL, ZIP_NAME, data_dir, progressbar=False)

def __prepare__(data_dir):
    """
    TEMPLATE COMMENT: prepare the data into graphml format.
    """
    pass

def get_graph():
    """
    TEMPLATE COMMENT: Downloads and prepares a graph
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, GRAPH_NAME + GRAPH_TYPE)

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


def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
