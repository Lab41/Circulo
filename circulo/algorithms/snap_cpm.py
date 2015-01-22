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

def clique_percolation(G, data_prefix='snap_'):

    '''
    Parameters
    -----------
    G:                  An iGraph or edge list file
    '''

    snap_home, graph_file = snap.setup(G)

    if graph_file is None:
        return

    path_cpm = os.path.join(snap_home, "examples", "cliques", "cliquesmain")

    try:
        FNULL = open(os.devnull, 'w')
        out = subprocess.Popen([path_cpm,"-o:"+data_prefix,"-i:"+graph_file], stdout=FNULL).wait()


    except TypeError as e:
        print("Error occurred: {}".format(e))
        return

    os.remove(graph_file)

    return snap.read_communities_by_community("cpm-" + data_prefix + ".txt", G, delete_file=True)



def main():

    G = igraph.load('/Users/ytesfaye/tmp/GRAPHS/flights.graphml')
    #snap_home, filename = setup(G)

    vc = cesna(G)
    print(vc)


if __name__ == "__main__":
    main()