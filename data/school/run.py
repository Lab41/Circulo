import networkx as nx
from subprocess import call
import igraph
import os
import sys
import glob


def __download__(data_dir):
    """
    Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
    and saves them in a directory data. If data already exists, it will not redownload
    the files
    """

    try:
        call(["curl", "--create-dirs","-o", os.path.join(data_dir, "out_#1.gexf.gz"),"http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz"])
    except Exception as e:
        print("cURL failed -- make sure you have cURL, and make sure the site still has the graph data.")
        raise(e)
    for filename in glob.glob(os.path.join(data_dir,"*.gz")):
        call(["gunzip", filename])



def __prepare__(data_dir):
    """
    Takes each file in .gexf format and converts it into the igraph-readable graphml.
    """

    """
    Takes a list of files in .gexf format, and converts each to GraphML.
    """

    for f in glob.glob(os.path.join(data_dir, "*.gexf")):
        print(f)
        newFileName = f[:f.rfind('.')] + ".graphml"

        if os.path.exists(newFileName):
            continue

        G = nx.read_gexf(f)
        for node in G.node:
            for attrib in G.node[node]:
                if type(G.node[node][attrib]) == dict:
                    # graphML doesn't play nice with dictionaries as attributes.
                    # this line just deletes positional information.
                    G.node[node][attrib] = 0
        newFileName = f[:f.rfind('.')] + ".graphml"
        nx.write_graphml(G, newFileName)


def get_graph():

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, "out_1.graphml")

    if not os.path.exists(graph_path):
        __download__(data_dir)
        __prepare__(data_dir)


    return igraph.load(graph_path)



def main(args):
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
