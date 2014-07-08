
from subprocess import call
import os
import shutil
import igraph as ig
import sys
import glob

#from circulo.algorithms.conga import conga

def download():
    """
    Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
    and saves them in a directory schoolData. If schoolData already exists, it will not redownload
    the files
    """
    if os.path.exists("football.zip"):
        return

    try:
        call(["curl","-o", "football.zip","http://www-personal.umich.edu/~mejn/netdata/football.zip"])
    except Exception as e:
        print("cURL failed -- make sure you have cURL, and make sure the site still has the graph data.")
        raise(e)

    call(["unzip","-d","data","football.zip"])


def prepare():
    """
    prepare the dataset
    """


def example():
    """
    Performs the example outlined in the README. Draws the graph of one dataset.
    """
    G = ig.load("data/football.gml")
    r = conga(G)

    #optimal count
    optimal_cover = r[r.optimal_count]

    for comm in optimal_cover:
        for n in comm:
            print(G.vs[n]['label'])
        print("\n")


def main():
    download()
    prepare()
    example()


if __name__ == "__main__":
    main()
