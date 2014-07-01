import networkx as nx
from subprocess import call
import os
import shutil
import igraph as ig
import sys
import glob

def download():
    """
    Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
    and saves them in a directory schoolData. If schoolData already exists, it will not redownload
    the files
    """
    if os.path.exists("schoolData"):
        return

    try:
        call(["curl", "--create-dirs","-o", "schoolData/out_#1.gexf.gz","http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz"])
    except Exception as e:
        print("cURL failed -- make sure you have cURL, and make sure the site still has the graph data.")
        raise(e)
    for filename in glob.glob("schoolData/*.gz"):
        call(["gunzip", filename])



def prepare():
    """
    Takes each file in .gexf format and converts it into the igraph-readable graphml.
    """

    """
    Takes a list of files in .gexf format, and converts each to GraphML.
    """
    files =  glob.glob("schoolData/*.gexf")

    for f in files:
        G = nx.read_gexf(f)
        for node in G.node:
            for attrib in G.node[node]:
                if type(G.node[node][attrib]) == dict:
                    # graphML doesn't play nice with dictionaries as attributes.
                    # this line just deletes positional information.
                    G.node[node][attrib] = 0
        newFileName = f[:f.rfind('.')] + ".graphml"
        nx.write_graphml(G, newFileName)



def example():
    """
    Performs the example outlined in the README. Draws the graph of one dataset.
    """
    g = ig.load("schoolData/out_1.graphml") # whichever file you would like

    # Assigning colors to genders for plotting
    colorDict = {"M": "blue", "F": "pink", "Unknown": "black"}

    for vertex in g.vs:
        # each vertex is labeled as its classname and colored as its gender.
        vertex["label"] = vertex["classname"]
        vertex["color"] = colorDict[vertex["gender"]]


    layout = g.layout("fr") # Fruchterman-Reingold layout

    # If Cairo is improperly installed, raises TypeError: plotting not available
    try:
        ig.plot(g, layout=layout)
    except TypeError as e:
        print("It looks like Cairo isn't properly installed. Refer to the wiki.")
        exit(1)

def main():
    download()
    prepare()
    example()


if __name__ == "__main__":
    main()
