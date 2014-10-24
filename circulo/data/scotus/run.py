import igraph
import os
import csv
from circulo.data.databot import *

DATA_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/judicial.csv'
VERTEX_DATA_FILE = 'judicial.csv'

EDGE_DOWNLOAD_URL = 'http://jhfowler.ucsd.edu/data/allcites.txt'
EDGE_DATA_FILE = 'allcites.txt'


class SCOTUSData(CirculoData):

    def __download__(self):
        self.download_with_notes(DATA_DOWNLOAD_URL)
        self.download_with_notes(EDGE_DOWNLOAD_URL)

    def __prepare__(self):
        vertex_filename = os.path.join(self.raw_data_path, VERTEX_DATA_FILE)
        edge_filename = os.path.join(self.raw_data_path, EDGE_DATA_FILE)

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
        g.write_graphml(self.graph_path)

def main():
    SCOTUSData("scotus").get_graph()

if __name__ == "__main__":
    main()
