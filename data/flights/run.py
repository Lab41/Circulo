import networkx as nx
from subprocess import call
import igraph
from igraph import VertexClustering
import os
import sys
import glob
import urllib


# from http://openflights.org/data.html

SOURCE_URL = 'https://sourceforge.net/p/openflights/code/HEAD/tree/openflights/data/routes.dat?format=raw'
FILENAME = 'routes'
SCHEMA = {"airline": 0, "airline_id": 1, "source_airport": 2, "source_id": 3, 
          "dest_airport": 4, "dest_id": 5, "codeshare": 6, "stops": 7, 
          "equipment": 8}

def __download__(data_dir):
    """
    TODO
    """
    #mkdir data
    try:
        result = urllib.request.urlretrieve(SOURCE_URL, os.path.join(data_dir, FILENAME + ".dat"))
    except Exception as e:
        print("Download failed -- make sure the url is still valid, and that urllib is properly installed.")
        raise(e)
    return result[0] # filename



def __prepare__(data_dir):
    """
    TODO
    """

    # in case there are multiple .dat files to be examined.
    for f in glob.glob(os.path.join(data_dir, "*.dat")):
        print(f)
        newFileName = f[:f.rfind('.')] + ".graphml"
        if os.path.exists(newFileName):
            continue
        G = dat_to_graph(f)
        G.write_graphml(newFileName)


def dat_to_graph(fileName):
    G = igraph.Graph()
    with open(fileName, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            print(line)


def get_graph():
    """
    TOOD
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, FILENAME + ".graphml")

    if not os.path.exists(graph_path):
        __download__(data_dir)
        __prepare__(data_dir)

    return igraph.load(graph_path)


def get_ground_truth(G=None):
    """
    TODO
    """

    # if G is None:
    #     G = get_graph()


    # class_list = G.vs['classname']
    # class_dict = dict.fromkeys(class_list)

    # #set the indices for lookup purposes. These will be the cluster ids
    # for idx, k in enumerate(class_dict):
    #     class_dict[k] = idx


    # membership = [ class_dict[student]  for student in class_list]

    # return VertexClustering(G, membership)



def main():
    G = get_graph()
    get_ground_truth(G)

if __name__ == "__main__":
    main()
