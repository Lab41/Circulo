import igraph
import os
import urllib.request

from circulo.data.databot import CirculoData



GRAPH_NAME = 'PGPgiantcompo.net'
DOWNLOAD_URL = 'http://deim.urv.cat/~aarenas/data/xarxes/PGP.zip'


class PGPData(CirculoData):

    def __download__(self):
        self.download_with_notes(DOWNLOAD_URL)

    def __prepare__(self):

        data_path = os.path.join(self.raw_data_path, GRAPH_NAME)
        G = igraph.load(data_path)
        del G.vs['id'] #graphml uses the id field
        G.write_graphml(self.graph_path)

    def get_ground_truth(self):
        raise(NotImplementedError)


def main():
    PGPData("pgp").get_graph()

if __name__ == "__main__":
    main()
