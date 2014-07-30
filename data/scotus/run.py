import igraph
from igraph import VertexClustering
import os
import sys
import urllib.request
import csv
from circulo.download_utils import download_with_notes

DATA_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/judicial.csv'
VERTEX_DATA_FILE = 'SCOTUS_DATA.csv'

EDGE_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/allcites.txt'
EDGE_DATA_FILE = 'SCOTUS_EDGES.edgelist'

GRAPH_NAME = 'SCOTUS'
GRAPH_TYPE = '.graphml'

def __download__(data_dir):
    """
    TEMPLATE COMMENT: downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DATA_DOWNLOAD_URL, VERTEX_DATA_FILE, data_dir)
    download_with_notes(EDGE_DOWNLOAD_URL, EDGE_DATA_FILE, data_dir)

def __prepare__(data_dir):
    """
    TEMPLATE COMMENT: prepare the data into graphml format.
    """

    vertex_filename = os.path.join(data_dir, VERTEX_DATA_FILE)
    edge_filename = os.path.join(data_dir, EDGE_DATA_FILE)

    g = igraph.load(edge_filename)

    vertex_file = open(vertex_filename)
    reader = csv.DictReader(vertex_file)

    for case in reader:
        caseid = int(case['caseid'])
        v = g.vs[caseid]

        v['caseid']  = case['caseid']
        v['usid']    = case['usid']
        v['parties'] = case['parties']
        v['year']    = case['year']

    vertex_file.close()

    # Case IDs are 1-indexed, so we delete the 0th vertex as it was extraneous.
    g.delete_vertices([0])

    graph_file = os.path.join(data_dir, GRAPH_NAME + GRAPH_TYPE)
    g.write_graphml(graph_file)

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
