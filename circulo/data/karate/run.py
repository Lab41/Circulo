import igraph
from igraph import VertexCover
import os
import sys
import urllib.request
from circulo.utils.downloader import download_with_notes
import shutil
from circulo.data.databot import *


GRAPH_NAME = 'karate'
DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/karate.zip'
GRAPH_TYPE = '.gml'
KARATE_RAW = "karate.gml"

class KarateData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL, download_file=KARATE_RAW)

    def __prepare__(self):

        G = igraph.load(os.path.join(self.raw_data_path, KARATE_RAW))
        del G.vs['id']
        G.write_graphml(self.graph_path)

    def get_ground_truth(self, G=None):
        """
        returns a VertexClustering object of the
        ground truth of the graph G.
        """
        if G is None:
            G = self.get_graph()

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

        clusters_list = [[],[]]

        for idx, k_id in enumerate(G.vs['id']):
            str_lbl = str(int(k_id))
            clusters_list[groups[str_lbl]].append(idx)

        return VertexCover(G, clusters_list)

def main():
    databot = KarateData("karate")
    databot.get_ground_truth()

if __name__ == "__main__":
    main()
