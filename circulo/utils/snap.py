import os
import subprocess
import tempfile
import sys
import igraph
from  igraph.clustering import VertexCover
from collections import OrderedDict

import circulo


__author__="""Paul M"""

__all__ = []


ENV_SNAPPATH_VAR = "SNAPHOME"


def read_communities_by_community(f_name, G):
    '''
    Reads a community file in the format where each line represents a community where the line is a list of nodes separated by white space
    '''

    comm_list = list()

    with open(f_name, 'r') as community_file:

        for line in community_file:
            if line.startswith('#'):
                continue
            try:
                comm_list.append(map(int, line.split()))
            except ValueError as e:
                print("Node type is unclear for line: {}".format(line))
                return

    return VertexCover(G, comm_list)


def read_communities_by_node(f_name, G):
    '''
    Reads a community file where each line is a node and the community to which it belongs
    For example
    0   1
    0   4
    0   0
    1   3
    1   4
    2   5
    '''

    #dict with keys as community_id and values are a list of nodes
    community_dict = dict()

    with open(f_name, 'r') as community_file:
        for line in community_file:
            if line.startswith('#'):
                continue

            node_id, community_id = (int(x) for x in line.split())

            if community_id not in community_dict:
                community_dict[community_id] = []

            community_dict[community_id].append(node_id)

    return VertexCover(G,  [v for v in community_dict.values()])



def divisive(G, algo_id, output):

    snap_home, graph_file  = setup(G)

    if graph_file is None:
        return

    path_girvan_newman = os.path.join(snap_home, "examples", "community", "community")


    try:
        out = subprocess.Popen([path_girvan_newman, "-i:"+graph_file, "-o:"+output, "-a:"+algo_id])
    except TypeError as e:
        print("Error occurred: {}".format(e))
        return

    out.wait()

    os.remove(graph_file)
    return read_communities_by_node(output, G)




def setup(G):

    snap_home = os.path.join(os.path.dirname(circulo.__file__), "..", "lib","snap")

    if not os.path.exists(os.path.join(snap_home,"examples","bigclam","bigclam")):
        raise Exception("SNAP must be downloaded and built prior to using the snap algorithms")

    f = tempfile.mkstemp()
    filename = f[1]

    try:

        #some snap algos can't handle single space edge delimiters, and igraph can't output
        #tab delimited edgelist, so we always convert the single spaced output to a tabbed output
        with open(filename, 'w') as out:
            for u,v in G.get_edgelist():
                out.write("{}\t{}\n".format(u, v))

    except:
        print("Error writing edgelist")
        return None

    return (snap_home, filename)
