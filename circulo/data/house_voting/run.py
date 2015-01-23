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

import json
import glob
import csv
import itertools
import os
import igraph
from igraph import VertexCover
from subprocess import call
from circulo.data.databot import CirculoData


class HouseData(CirculoData):

    def __download__(self):

        try:
            call(["bash", os.path.join(os.path.dirname(__file__), "download.sh"), self.raw_data_path])
        except Exception as e:
            #print("rsync failed to retrieve data")
            raise(e)

    def __prepare__(self):
        '''
        Prepare congress data. NOTE: the vertex lookups should be indexed, however this
        funciton could prob be sped up by just created a dict with all possible congress pairs
        and counting how often they vote together, then at the end creating the edges
        '''

        src_files = os.path.join(self.raw_data_path, "2014", "h*","*.json")
        c_type = "rep"
        G = igraph.Graph()


        #first load the vertices
        with open(os.path.join(self.raw_data_path, "legislators-current.csv"), 'r') as f:

            csvreader = csv.reader(f,delimiter=',',quotechar='"')
            #skip the headers
            next(csvreader, None)  # skip the headers
            for row in csvreader:

                if c_type != row[4]:
                    continue
                elif row[4] == "sen":
                    congress_id = row[21]
                elif row[4] == "rep":
                    congress_id = row[18]
                else:
                    raise("Unidentified congress: {}".format(row[4]))

                G.add_vertex(
                    congress_id,
                    full_name="{} {}".format(row[1],row[0]),
                    party=row[7],
                    state=row[5]
                    )



        missing_ids = set()

        #now create the edges
        for fname in glob.glob(src_files):
            with open(fname,'r') as inputfile:
                data = json.load(inputfile)
                for vt in data['votes']:
                    congress_ids = [n['id'] for n in data['votes'][vt]]
                    pairs = itertools.combinations(congress_ids,2)

                    for congress_id0, congress_id1 in pairs:
                        try:
                            v0 = G.vs.find(congress_id0)
                        except ValueError as e:
                            missing_ids.add(congress_id0)
                            continue

                        try:
                            v1 = G.vs.find(congress_id1)
                        except ValueError as e:
                            missing_ids.add(congress_id1)
                            continue

                        e = G.get_eid(v0.index, v1.index, directed=False, error=False)

                        if e>=0:
                            G.es[e]['weight'] += 1
                        else:
                            G.add_edge(v0, v1, weight=1)

        #the graph is highly connected, so we will prune it
        self.prune(G)

        components = G.components(mode=igraph.WEAK)

        #the dataset by default is diconnected, so we must take the largest component
        if len(components) is not 1:
            G = G.subgraph(max(components, key=len))


        G.write_graphml(self.graph_path)

    def prune(self,G):

        if G.is_weighted() is False:
            print("Error: Unable to prune a graph without edge weights")
            return

        weights = G.es()['weight']
        threshold = .65 * max(weights)
        orig_edge_count = G.ecount()
        edges = G.es.select(weight_lt=threshold)
        G.delete_edges(edges)

    def __party_to_cluster__(self, party):
        if party == "Democrat":
            return 0
        elif party == "Republican":
            return 1
        elif party == "Independent":
            return 2
        else:
            raise("Unknown party affiliation {}".format(party))

    def get_ground_truth(self, G):

        cluster_list = [[],[],[]]

        for vertex_id, party in enumerate(G.vs['party']):
            cluster_list[self.__party_to_cluster__(party)].append(vertex_id)

        return VertexCover(G, cluster_list)


def main():

    databot = HouseData("house_voting")
    G = databot.get_graph()
    databot.get_ground_truth(G)

if __name__ == "__main__":
    main()
