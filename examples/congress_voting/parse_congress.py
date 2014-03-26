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
import operator
import os
import shutil

def main(argv):

    # get list of json files
    files_list = glob.glob("2014/*/*.json")
    #files_list = ['2014/h12/data.json']

    if os.path.exists("senate"):
        shutil.rmtree("senate")
    if os.path.exists("house"):
        shutil.rmtree("house")

    os.makedirs("senate")
    os.makedirs("house")

    senate_data = {}
    house_data = {}

    for fname in files_list:
            with open(fname,'r') as inputfile:
                    data = json.load(inputfile)
                   
                    if data["chamber"] == "s":
                        current_dict = senate_data
                    else:
                        current_dict = house_data

                    for vt in data['votes']:
                            
                        node_ids = [n['id'] for n in data['votes'][vt]]
                        
                        pairs = itertools.permutations(node_ids,2)
                        for rep0, rep1 in pairs:
                            if (rep0, rep1) not in current_dict:
                                current_dict[(rep0, rep1)] = 1
                            else:
                                current_dict[(rep0, rep1)] +=1

    max_senate_vote = max(senate_data.iteritems(), key=operator.itemgetter(1))[1]
    max_house_vote = max(house_data.iteritems(), key=operator.itemgetter(1))[1]
    
    print max_senate_vote
    print max_house_vote
    threshold_senate = float(max_senate_vote) * .8
    threshold_house =  float(max_house_vote) * .8

    print "Senate Thres: {}".format(threshold_senate)
    print "House Thres: {}".format(threshold_house)

    write_edge_list(senate_data, threshold_senate, "edges_senate.txt")
    write_edge_list(house_data, threshold_house, "edges_house.txt")

    senators, reps = load_congress("legislators-current.csv")
    create_graph(senate_data, senators, "senate.graphml")
    create_graph(house_data, reps, "house.graphml")
    



def load_congress(congress_file):
    
    with open(congress_file, 'r') as f:
    
        csvreader = csv.reader(f,delimiter=',',quotechar='"')
        #skip the headers
        next(csvreader, None)  # skip the headers
        senators = {}
        reps = {}
        for row in csvreader:
            
            name = "{} {}".format(row[1],row[0]).decode('utf-8')
            state = row[5]
            party = row[6]

            if row[4] == "sen":
                senators[row[20]] = (name, state, party) 
            else:
                reps[row[17]] = (name, state, party)

    return senators, reps



def create_graph(edge_dict, node_dict, out):

    G = nx.Graph()
    for(p0, p1), count in edge_dict.iteritems():
        G.add_edge(p0.decode('utf-8'), p1.decode('utf-8'), weight=count)
    
    for node_id in G.nodes_iter():

        if node_id in node_dict:
            G.node[node_id]['name'] = node_dict[node_id][0] 
            G.node[node_id]['state'] = node_dict[node_id][1]
            G.node[node_id]['party'] = node_dict[node_id][2]
        else:
            print "Node Id: {} not found in node_dict".format(node_id)
    nx.write_graphml(G,out)


def write_edge_list(curr_dict, threshold, filename):
    with open(filename, 'w') as edgesoutput:
        csvwriter = csv.writer(edgesoutput,delimiter='\t')
        for (p0, p1), count in curr_dict.iteritems():
            if count > threshold:
                row = [p0,p1]
                csvwriter.writerow(row)



if __name__ == "__main__":
        main(sys.argv[1:])
