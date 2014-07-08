import networkx as nx
from subprocess import call
import os
import shutil
import igraph as ig
import sys
import glob
import getopt
from circulo import metrics


def download(path="data"):
    """
    Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
    and saves them in a directory data. If data already exists, it will not redownload
    the files
    """
    if os.path.exists(path):
        return

    try:
        call(["curl", "--create-dirs","-o", os.path.join(path,"out_#1.gexf.gz"),"http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz"])
    except Exception as e:
        print("cURL failed -- make sure you have cURL, and make sure the site still has the graph data.")
        raise(e)
    for filename in glob.glob(os.path.join(path,"*.gz")):
        call(["gunzip", filename])



def prepare(path="data"):
    """
    Takes each file in .gexf format and converts it into the igraph-readable graphml.
    """

    """
    Takes a list of files in .gexf format, and converts each to GraphML.
    """

    for f in glob.glob(os.path.join(path, "*.gexf")):

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


    return os.path.join(path,"out_1.graphml")


def main(args):

    download()
    prepare()

if __name__ == "__main__":
    main(sys.argv[1:])
