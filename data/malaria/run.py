import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes


GRAPH_NAME = 'malaria'
DOWNLOAD_URL = 'http://danlarremore.com/bipartiteSBM/malariaData.zip'
GRAPH_TYPE = '.edgelist'

def __download__(data_dir):
    """
    downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DOWNLOAD_URL, GRAPH_NAME, data_dir)


def __prepare__(data_dir):
    with open(os.path.join(data_dir, "malariaData", GRAPH_NAME + GRAPH_TYPE), 'r') as f:
        with open(os.path.join(data_dir, GRAPH_NAME + GRAPH_TYPE), 'w') as new:
            for line in f:
                new.write(line[:-2] + '\n')


def get_graph():
    """
    Downloads and prepares a graph
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
    returns a VertexClustering object of the 
    ground truth of the graph G.
    """
    if G is None:
        G = get_graph()

    raise(Exception(NotImplementedError))

def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
