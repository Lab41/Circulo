import os
import urllib.request
import igraph as ig
import gzip
import pickle
import shutil
import sys
from circulo.utils.downloader import download_with_notes, _unzip
import csv

from circulo.data.databot import *

## First pass at downloading SNAP data.
# 1. SNAP uses gzip for compression
# 2. There are overlapping communities, but graphml attributes cannot be lists so stored as string
# 3. Uses pickle file instead to store graph object (keeping groundtruth as list)
# 4. igraph wants to keep vertex ids sequential but SNAP data is not, so some empty nodes are created
# 5. after deleting these isolate nodes, the ids are remapped to remain sequetial, so have to also remap ground truth

DOWNLOAD_URL = 'http://snap.stanford.edu/data/bigdata/communities/com-amazon.ungraph.txt.gz'
DATA_NAME = 'com-amazon.ungraph.txt'
GRAPH_NAME = 'amazon.graphml'

#ground truth of the top 5000 copurchasing items
DOWNLOAD_URL_GROUNDTRUTH = 'http://snap.stanford.edu/data/bigdata/communities/com-amazon.top5000.cmty.txt.gz'
#DOWNLOAD_URL_GROUNDTRUTH = 'http://snap.stanford.edu/data/bigdata/communities/com-amazon.all.cmty.txt.gz'
GROUNDTRUTH_NAME = 'com-amazon.top5000.cmty.txt'

PICKLE_NAME = 'amazon-graph.pickle'


class AmazonData(CirculoData):

    def __download__(self):
        '''
        downloads graph from SNAP website
        '''
        #download the graph as an edgelist
        self.download_with_notes(DOWNLOAD_URL)

        #download ground truth
        self.download_with_notes(DOWNLOAD_URL_GROUNDTRUTH)

    def __prepare__(self):

        data_path_old = os.path.join(self.raw_data_path, DATA_NAME + ".old")
        data_path = os.path.join(self.raw_data_path, DATA_NAME)

        #remove non edge data from edgelist
        shutil.move(data_path, data_path_old)

        with open(data_path_old, "r") as f:
            with open(data_path, "w") as out:
                for line in f:
                    if(line.startswith('#') == False):
                        out.write(line)

        groundtruth_path = os.path.join(self.raw_data_path,GROUNDTRUTH_NAME)

        # Read in Edgelist. Note that igraph creates extra nodes
        # with no edges for ids missing in sequential order
        # from the graph. We will delete these isolates later
        g = ig.Graph.Read_Edgelist(data_path,directed=False)

        # Assign communities as node attributes
        with open(groundtruth_path,'r') as gtp:
                csvreader = csv.reader(gtp,delimiter='\t')
                # note that converting to graphml, attributes cannot be lists
                # only boolean,int,long,float,double,or string
                #
                # storing groundtruth communities as both arrays and strings
                # so that graphml file can retain attribute
                g.vs()['groundtruth_str'] = ''

                count = 0
                for line in csvreader:
                    for v in line:
                        v = int(v)
                        if g.vs[v]['groundtruth_str']:
                                g.vs[v]['groundtruth_str'] += ',' + str(count)
                        else:
                            g.vs[v]['groundtruth_str'] = str(count)
                    count += 1
                    max_clusters = count

        # remove isolates - this changes node ids!
        g.delete_vertices(g.vs.select(_degree=0))

        # Write out graphml file
        g.write_graphml(self.graph_path)


    def get_ground_truth(self, G):

        cluster_dict = {}

        for idx, cluster_str in enumerate(G.vs()['groundtruth_str']):
            for c in  cluster_str.split():
                if c not in cluster_dict:
                    cluster_dict[c] = []

                #have to re-do this since id's likely changed by removing isolates
                cluster_dict[c].append(idx)

        return  ig.VertexCover(G,[v for v in cluster_dict.values()])


def main():
    databot = AmazonData("amazon")
    databot.get_ground_truth(databot.get_graph())

if __name__ == '__main__':
    main()
