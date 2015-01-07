import os
import shutil
from circulo.data.databot import *

DOWNLOAD_URL = "http://nexus.igraph.org/api/dataset?id=23&format=GraphML"
DATA_ID = "southernwomen"
DOWNLOAD_FILE="Davis.GraphML"

class SouthernWomenData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL, progressbar=False, download_file=DOWNLOAD_FILE)

    def __prepare__(self):
        shutil.copyfile(os.path.join(self.raw_data_path, DOWNLOAD_FILE), self.graph_path)

    def get_ground_truth(self, G):
        raise(NotImplementedError)

    def get_context(self):
        return {
                CirculoData.CONTEXT_OPTIMAL_PARTITIONS:10
                }


def main():
    SouthernWomenData(DATA_ID).get_graph()

if __name__ == "__main__":
    main()
