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
import os
import subprocess
from circulo.utils import snap
import shutil

def cesna(G, attributes_to_include, data_prefix='snap_', node_filepath='', detect_comm=100, min_comm=5, max_comm=100, trials=5, threads=4, alpha=.3, beta=0.3):

    '''
    Parameters
    -----------
    G:                  An iGraph or edge list file
    f_attributes:       Input node attribute file name (Required)
    f_attribute_names:  Input file name for node attribute names (Required)
    nodes:              Input file name for node names (Node ID, Node label)
    detect_comm:         The number of communities to detect (-1: detect automatically) (default:10)
    min_comm:           Minimum number of communities to try (default:3)
    max_comm:           Maximum number of communities to try (default:20)
    trials:             How many trials for the number of communities (default:5)
    threads:            Number of threads for parallelization (default:4)
    aw:                 We maximize (1 - aw) P(Network) + aw * P(Attributes) (default:0.5)
    lw:                 Weight for l-1 regularization on learning the logistic model parameters (default:1)
    alpha:              Alpha for backtracking line search (default:0.05)
    beta:               Beta for backtracking line search (default:0.3)
    mf                  if the fraction of nodes with positive values for an attribute is smaller than this, we ignore that attribute (default:0)
    '''

    snap_home, graph_file = snap.setup(G)

    f_attribute_names, f_attributes = snap.attribute_setup(G, attributes_to_include)
    shutil.copyfile(f_attribute_names, 'attribute_names.txt')
    shutil.copyfile(f_attributes, 'attribute.txt')
    print(f_attributes, f_attribute_names)
    if graph_file is None:
        return

    path_cesna = os.path.join(snap_home, "examples", "cesna", "cesna")

    try:
        FNULL = open(os.devnull, 'w')
        out = subprocess.Popen([path_cesna,"-o:"+data_prefix,"-i:"+graph_file,"-l:"+node_filepath, "-c:-1", "-mc:"+str(min_comm), "-xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-sa:"+str(alpha), "-sb:"+str(beta),  "-a:"+f_attributes, "-n:"+f_attribute_names]).wait()


    except TypeError as e:
        print("Error occurred: {}".format(e))
        return

    os.remove(graph_file)

    return snap.read_communities_by_community(data_prefix + "cmtyvv.txt", G)



def main():

    G = igraph.load('/Users/ytesfaye/tmp/GRAPHS/flights.graphml')
    #snap_home, filename = setup(G)

    vc = cesna(G)
    print(vc)


if __name__ == "__main__":
    main()