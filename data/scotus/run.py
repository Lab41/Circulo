import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes

GRAPH_DATA_NAME = 'SCOTUS_DATA'
GRAPH_EDGE_NAME = 'SCOTUS_EDGES'
DATA_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/judicial.csv'
EDGE_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/allcites.txt'

GRAPH_NAME = 'SCOTUS'
GRAPH_TYPE = '.graphml'

def __download__(data_dir):
    """
    TEMPLATE COMMENT: downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DATA_DOWNLOAD_URL, GRAPH_DATA_NAME, data_dir)
    download_with_notes(EDGE_DOWNLOAD_URL, GRAPH_EDGE_NAME, data_dir)

def __prepare__(data_dir):
    """
    TEMPLATE COMMENT: prepare the data into graphml format.
    """
    raise(NotImplementedError)
    g = igraph.Graph()

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

    # if G is None:
    #     G = get_graph()

    # return # VertexClustering(G, membership)


def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
