import os
import subprocess
import tempfile
import sys
import igraph
from  igraph.clustering import VertexCover
from collections import OrderedDict

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
    node_dict = dict()

    with open(f_name, 'r') as community_file:
        for line in community_file:
            if line.startswith('#'):
                continue

            node_id, community_id = (int(x) for x in line.split())

            if node_id not in node_dict:
                node_dict[node_id] = set()

            node_dict[node_id].add(community_id)

    sorted_list=sorted(node_dict.items(), key=lambda x: x[0])

    return VertexCover(G,  [list(v) for k,v in sorted_list])



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

    try:
        snap_home = os.environ[ENV_SNAPPATH_VAR]
    except KeyError as e:
        print("Be sure to set your snap base path in the environment variable \"{}\"".format(ENV_SNAPPATH_VAR))
        return None, None

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
