import igraph
from igraph import VertexCover
import os
import sys
import urllib.request
from circulo.utils.downloader import download_with_notes
import shutil
from circulo.data.databot import *


DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/karate.zip'
KARATE_RAW = "karate.gml"

class KarateData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL)

    def __prepare__(self):

        G = igraph.load(os.path.join(self.raw_data_path, KARATE_RAW))
        del G.vs['id']
        G.write_graphml(self.graph_path)

    def get_ground_truth(self, G):
        """
        returns a VertexClustering object of the
        ground truth of the graph G.
        """

        clusters_list = [
                [0,1,2,3,4,5,6,7,10,11,12,13, 16,17,19, 20, 22,23,24,25,26,27,28,29,30,31,32,33],
                [8,9,14, 15, 18,21]
                ]

        return VertexCover(G, clusters_list)

def main():
    databot = KarateData("karate")
    databot.get_ground_truth(databot.get_graph())

if __name__ == "__main__":
    main()
