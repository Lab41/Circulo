import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes


GRAPH_NAME = 'netscience'
DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/netscience.zip'
GRAPH_TYPE = '.gml'

def __download__(data_dir):
    """
    downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
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
    Downloads and prepares the network science collaboration graph
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
    Returns a VertexClustering object of the 
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
