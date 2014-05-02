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

SENATE_THRES = .8
HOUSE_THRES = .9

def main(argv):

    do_filter = False

    if len(argv) > 0 and argv[0] == 'Filter':
        do_filter = True

    # get list of json files
    files_list = glob.glob("2014/*/*.json")
    #files_list = ['2014/h12/data.json']

    if os.path.exists("senate"):
        shutil.rmtree("senate")
    if os.path.exists("house"):
        shutil.rmtree("house")

    os.makedirs("senate")
    os.makedirs("house")

    #just creates the nodes
    G_senate, G_house = load_congress("legislators-current.csv")

    #now create the edges
    for fname in files_list:
            with open(fname,'r') as inputfile:
                    data = json.load(inputfile)
                   
                    if data["chamber"] == "s":
                        G = G_senate
                    else:
                        G = G_house

                    for vt in data['votes']:
                            
                        node_ids = [n['id'] for n in data['votes'][vt]]
                        
                        pairs = itertools.permutations(node_ids,2)
                        
                        #assumes lists are always alphabetical so that pairs will only occur in one direction
                        for u, v in pairs:
                           
                            if G.has_edge(u, v):
                                G[u][v]['weight']+=1
                            else:
                                G.add_edge(u, v, weight=1)

    if do_filter:
        for u, v, d in G_senate.edges(data=True):
            if d['weight'] < 160:
                print "removing edge"
                G.remove_edge(u,v)


    nx.write_graphml(G_senate, "senate/senate.graphml")
    nx.write_graphml(G_house, "house/house.graphml") 
    write_node_list(G_senate, "senate/senate_nodes.txt")
    write_node_list(G_house, "house/house_nodes.txt")
    

def write_node_list(G, out):
    with open(out, 'w') as f:
        
        csvwriter = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_ALL)
        for n,d in G.nodes(data=True):
            if 'party' in d and 'name' in d:
                csvwriter.writerow((n, d['name'].encode('utf-8'), d['party']))
             

def load_congress(congress_file):
 
    G_senate = nx.Graph()
    G_house = nx.Graph()

    with open(congress_file, 'r') as f:
    
        csvreader = csv.reader(f,delimiter=',',quotechar='"')
        #skip the headers
        next(csvreader, None)  # skip the headers
        for row in csvreader:
            
          
            if row[4] == "sen":
                node_id = row[20]
                G = G_senate
            elif row[4] == "rep":
                node_id = row[17]
                G = G_house
            else:
                continue
            
            G.add_node(node_id, name="{} {}".format(row[1],row[0]).decode('utf-8'), party=row[6], state=row[5])

    return G_senate, G_house


if __name__ == "__main__":
        main(sys.argv[1:])
