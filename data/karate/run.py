import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
from circulo.download_utils import download_with_notes


GRAPH_NAME = 'karate'
DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/karate.zip'
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

    #ground truth table
    groups = {
            "1":0,
            "2":0,
            "3":0,
            "4":0,
            "5":0,
            "6":0,
            "7":0,
            "8":0,
            "9":1,
            "10":1,
            "11":0,
            "12":0,
            "13":0,
            "14":0,
            "15":1,
            "16":1,
            "17":0,
            "18":0,
            "19":1,
            "20":0,
            "21":1,
            "22":0,
            "23":1,
            "24":1,
            "25":1,
            "26":1,
            "27":1,
            "28":1,
            "29":1,
            "30":1,
            "31":1,
            "32":1,
            "33":1,
            "34":1,
            }

    membership = [groups[str(int(karatemember))] for karatemember in G.vs['id']]

    return VertexClustering(G, membership)

def main():
    G = get_graph()
#    get_ground_truth(G)

if __name__ == "__main__":
    main()
