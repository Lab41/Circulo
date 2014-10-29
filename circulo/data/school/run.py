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


import networkx as nx
from subprocess import call
import igraph
from igraph import VertexCover
import os
import glob

from circulo.data.databot import CirculoData



class SchoolData(CirculoData):

    def __download__(self):
        """
        Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
        and saves them in a directory data. If data already exists, it will not redownload
        the files
        """

        try:
            # Probably shouldn't be starting a subprocess, do this with a library
            # like urllib2
            call(["curl", "--create-dirs","-o", os.path.join(self.raw_data_path, "out_#1.gexf.gz"),"http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz"])
        except Exception as e:
            print("cURL failed -- make sure you have cURL, and make sure the site still has the graph data.")
            raise(e)
        for filename in glob.glob(os.path.join(self.raw_data_path,"*.gz")):
            call(["gunzip", filename])



    def __prepare__(self):

        for f in glob.glob(os.path.join(self.raw_data_path, "*.gexf")):

            G = nx.read_gexf(f)
            for node in G.node:
                for attrib in G.node[node]:
                    if type(G.node[node][attrib]) == dict:
                        # graphML doesn't play nice with dictionaries as attributes.
                        # this line just deletes positional information.
                        G.node[node][attrib] = 0
            #newFileName = f[:f.rfind('.')] + ".graphml"
            nx.write_graphml(G, self.graph_path)


    def get_ground_truth(self, G):

        class_list = G.vs['classname']
        class_dict = dict.fromkeys(class_list)

        #set the indices for lookup purposes. These will be the cluster ids
        for idx, k in enumerate(class_dict):
            class_dict[k] = []

        for student_number, class_id in enumerate(class_list):
            class_dict[class_id].append(student_number)

        cluster_list = []

        for cluster in class_dict.values():
            cluster_list.append(cluster)

        return VertexCover(G, cluster_list)


def main():
    databot = SchoolData("school")
    databot.get_ground_truth(databot.get_graph())

if __name__ == "__main__":
    main()
