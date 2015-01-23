#!/usr/bin/env python
#
# Copyright (c) 2014 In-Q-Tel, Inc/Lab41, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import igraph
from igraph import VertexCover
import gzip
import bz2
import os
from operator import itemgetter


from circulo.data.databot import CirculoData

DOWNLOAD_URL = 'http://data.caida.org/datasets/as-relationships/serial-1/20141201.as-rel.txt.bz2'
AS_INFO_URL = 'http://data.caida.org/datasets/as-organizations/20141001.as-org2info.txt.gz'


class ASData(CirculoData):
    @staticmethod
    def __make_asn_mapping(fname):
        """
        Helper function to turn downloaded file into dictionary where key = ASN and values are dictionary of properties
        """
        FORMAT_STRING = '# format'
        ORG_ID_STRING = 'org_id'
        ASN_STRING = 'aut'

        data_by_org_id = {}  # Dictionary of properties by org ID {org_id:{prop_name:prop_value}}
        # Read source file using #format lines to parse fields
        with gzip.open(fname, 'rt') as f:
            for line in f:
                line = line.strip()
                if line.startswith(FORMAT_STRING):
                    # Extract format
                    format_fields = line[len(FORMAT_STRING)+1:].split('|')
                    org_id_index = format_fields.index(ORG_ID_STRING)
                    print(format_fields, org_id_index)
                elif line.startswith("#"):
                    # Ignore comments that aren't format
                    pass
                else:
                    # Decode data and add to data_by_org_id
                    data = line.split('|')
                    org_id = data[org_id_index]
                    if org_id not in data_by_org_id:
                        data_by_org_id[org_id] = {}
                    for i,data_field in enumerate(format_fields):
                        if i != org_id_index:
                            data_by_org_id[org_id][data_field] = data[i]

        # Restructure data to be sorted by asn
        data_by_asn = {}  # {asn:{prop_name:prop_value}}
        for org_id in data_by_org_id:
            asn = data_by_org_id[org_id][ASN_STRING]
            if asn not in data_by_asn:
                data_by_asn[asn] = {}
            for (field_name, field_val) in data_by_org_id[org_id].items():
                if field_name != ASN_STRING:
                    data_by_asn[asn][field_name] = field_val
        return data_by_asn

    def __download__(self):
        print("Downloading")
        self.download_with_notes(DOWNLOAD_URL)
        self.download_with_notes(AS_INFO_URL)

    def __prepare__(self):
        filename = os.path.join(self.raw_data_path, os.path.basename(DOWNLOAD_URL))

        edges = []
        relationships = []
        print("Reading links")
        # Read in raw AS Links
        with bz2.open(filename, 'rt') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('#'):
                    (src, dst, relationship) = line.split('|')
                    src = int(src)
                    dst = int(dst)
                    if src and dst:
                        # TODO: Consider changing to directed graph and duplicating peer links in  both directions?
                        edges.append((src, dst))
                        relationships.append(relationship)

        print("Creating Graph")
        num_nodes = max(max(max(edges, key=itemgetter(0))), max(max(edges, key=itemgetter(1))))
        g = igraph.Graph(directed=False)
        g.add_vertices(num_nodes+1) # Need +1 since ASN are 1 indexed but verticies are 0 indexed
        g.add_edges(edges)

        # Keep AS Names through pruning
        g.vs["ASN"] = [str(as_num) for as_num in range(len(g.vs))]
        # Add relationships before pruning
        g.es["relationship"] = relationships

        # Add other ASN Properties
        asn_filename = os.path.join(self.raw_data_path, os.path.basename(AS_INFO_URL))
        asn_info = self.__make_asn_mapping(asn_filename)
        print("Num Nodes:", num_nodes)
        for asn in asn_info:
            if int(asn) <= num_nodes:
                for field_name, field_val in asn_info[asn].items():
                    g.vs[int(asn)][field_name] = field_val

        print("Checking Graph")
        # Take largest connected component
        components = g.components(mode=igraph.WEAK)
        if len(components) > 1:
            print("[Graph Prep - as_data]... Disconnected Graph Detected. Using largest component.")
            print("[Graph Prep - as_data]... Original graph: {} vertices and {} edges.".format(g.vcount(), g.ecount()))
            g = g.subgraph(max(components, key=len))
            print("[Graph Prep - as_data]... Largest component: {} vertices and {} edges.".format(g.vcount(), g.ecount()))
        g.write_graphml(self.graph_path)

    def prune(self, G):
        # There aren't edge weights so there's no way to prune
        pass

    def get_ground_truth(self, G=None):
        """
        Get a Vertex Cover representing the ground truth for this graph. It's not apparent what the right "ground truth"
        is but a guess is "country". It might be true that "source" (which is the registrar that handled the transaction
        ) is a better guess
        """
        if G is None:
            G = self.get_graph()

        if G is None:
            return

        LABEL_TAG = 'country'

        membership = G.vs[LABEL_TAG]
        # Map community names to integers
        community_name_to_id = {}
        max_community_seen = 0

        cluster_dict = {}
        for vertex_id, community_name in enumerate(membership):
            if community_name not in community_name_to_id:
                community_name_to_id[community_name] = max_community_seen  # Add to dict
                cluster_dict[max_community_seen] = []  # Initialize
                max_community_seen += 1

            community_id = community_name_to_id[community_name]
            cluster_dict[community_id].append(vertex_id)

        cluster_list = [v for v in cluster_dict.values()]
        return VertexCover(G, cluster_list)


def main():
    databot = ASData("as_data")
    G = databot.get_graph()
    databot.get_ground_truth(G)


if __name__ == "__main__":
    main()