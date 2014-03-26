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

# Generates a graphml file and an edge list from json files of congress voting

import json
import sys
import glob
import csv
import itertools
import networkx as nx



def main(argv):

    # get list of json files
    files_list = glob.glob("2014/*/*.json")
    #files_list = ['2014/h12/data.json']

    link_data = {}

    for fname in files_list:
            with open(fname,'r') as inputfile:
                    data = json.load(inputfile)

                    for vt in data['votes']:
                            
                            node_ids = [n['id'] for n in data['votes'][vt]]

                            pairs = itertools.permutations(node_ids,2)
                            for rep0, rep1 in pairs:
                                if (rep0, rep1) not in link_data:
                                    link_data[(rep0, rep1)] = 1
                                else:
                                    link_data[(rep0, rep1)] +=1


    # Write Edge Data
    with open('edges.csv','w') as edgesoutput:
            csvwriter = csv.writer(edgesoutput,delimiter='\t',quotechar='"',quoting=csv.QUOTE_ALL)
            for (rep0, rep1), count in link_data.iteritems():
                row = [rep0,rep1,count]
                csvwriter.writerow(row)


    G = nx.Graph()
    for(rep0, rep1), count in link_data.iteritems():
        
        G.add_edge(rep0.decode('utf-8'), rep1.decode('utf-8'), weight=count)

    with open('legislators-current.csv', 'r') as f:
        csvreader = csv.reader(f,delimiter=',',quotechar='"')
        #skip the headers
        next(csvreader, None)  # skip the headers
       
        for row in csvreader:
            node_id = row[20]
            
            #if node_id has zero length, then it is not a senator, but a house member, whose id is the 17th row
            if node_id is None or len(node_id) == 0:
                node_id = row[17]

            if node_id in G.node:
                G.node[node_id]['name'] = "{} {}".format(row[1],row[0]).decode('utf-8')
                G.node[node_id]['type'] = row[4]
                G.node[node_id]['party'] = row[6]
                G.node[node_id]['state'] = row[5]
            
    nx.write_graphml(G,'congress_graph.graphml')


if __name__ == "__main__":
        main(sys.argv[1:])
