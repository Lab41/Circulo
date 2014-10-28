# This template should be copied and modified as necessary to become the
# `run.py` in each directory.
#
# Do not modify this file unless the template needs changing -- modify
# its copies in each data directory.

import igraph
import os
import csv
from subprocess import call

from circulo.data.databot import CirculoData

GIT_URL = 'https://github.com/kjhealy/revere.git'
CSV_FILE = 'data/PaulRevereAppD.csv'

class RevolutionData(CirculoData):

    def __download__(self):
        try:
            call(["git", "clone", GIT_URL, self.raw_data_path])
        except Exception as e:
            print("Git clone failed to retrieve data. Please try again.")
            raise(e)

    def __prepare__(self):

        csv_path = os.path.join(self.raw_data_path, CSV_FILE)

        g = igraph.Graph()

        with open(csv_path) as f:

            reader = csv.DictReader(f)
            clubs = reader.fieldnames[:]
            clubs.remove('')

            for club in clubs:
                g.add_vertex(name=club)

            for patriot in reader:
                g.add_vertex(name=patriot[''])
                for club in clubs:
                    if(patriot[club] == '1'):
                        g.add_edge(patriot[''], club)

        g.write_graphml(self.graph_path)

    def get_ground_truth(self):
        raise(NotImplementedError)


def main():
    RevolutionData("revolution").get_graph()

if __name__ == "__main__":
    main()
