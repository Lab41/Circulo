import igraph
from igraph import VertexCover
import os
import sys
import urllib.request
import shutil
from circulo.data.databot import *

DOWNLOAD_URL = "http://www-personal.umich.edu/~mejn/netdata/football.zip"

class FootballData(CirculoData):

    def __download__(self):
        """
        downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
        """
        self.download_with_notes(DOWNLOAD_URL)

    def __prepare__(self):
        """
        """
        #convert gml to graphml
        G = igraph.load( os.path.join(self.raw_data_path, "football.gml"))
        #must delete the id attribute since graphml uses it as a reserved attribute and gml does not
        del G.vs['id']
        G.write_graphml(self.graph_path)


    def get_ground_truth(self, G=None):
        """
        Returns a VertexClustering object of the
        ground truth of the graph G. The ground truth for this
        football data is the conference to which each team belongs.
        """

        if G is None:
            G = get_graph()

        if G is None:
            print("Unable to get graph")
            sys.exit(0)

        #by default conferences are identified by a float number
        float_membership = G.vs['value']
        conf_map = {}
        for vertex_id, conference_id in enumerate(float_membership):
            if conference_id not in conf_map:
                conf_map[conference_id] = []
            conf_map[conference_id].append(vertex_id)


        cluster_list = [v for k,v in conf_map.items()]

        return VertexCover(G, cluster_list)


def main():
    FootballData("football").get_ground_truth()

if __name__ == "__main__":
    main()
