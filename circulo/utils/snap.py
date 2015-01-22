import os
import subprocess
import tempfile
import sys
import igraph
from  igraph.clustering import VertexCover
from collections import OrderedDict

from sklearn.feature_extraction import DictVectorizer
import numpy as np

import circulo

__author__="""Paul M"""

__all__ = []


ENV_SNAPPATH_VAR = "SNAPHOME"


def read_communities_by_community(f_name, G, delete_file=False):
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

    if delete_file:
        os.remove(f_name)

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
    max_node_id = len(G.vs)
    with open(f_name, 'r') as community_file:
        for line in community_file:
            if line.startswith('#'):
                continue

            node_id, community_id = (int(x) for x in line.split())
            if node_id <= max_node_id:
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


def attribute_setup(G, attrs_of_interest):
    """
    Create node name and node attribute files. Uses DictVectorizer to encode free form attribute input into set of
    binary classes. node_attribute_name_file contains the mapping of binary classes to names
    """
    f = tempfile.mkstemp()
    node_attribute_name_file = f[1]

    f2 = tempfile.mkstemp()
    node_attribute_file = f2[1]

    # Create an array of attributes of interest
    attr_array = []
    for node in G.vs:
        node_attributes_dict = {}
        for attr_name, attr_val in node.attributes().items():
            if attr_name in attrs_of_interest:
                node_attributes_dict[attr_name] = attr_val
        attr_array.append(node_attributes_dict)

    # TODO: Don't make dense array for sparse input
    vec = DictVectorizer(dtype=np.int32)
    vectorized_array = vec.fit_transform(attr_array).toarray()
    try:
        with open(node_attribute_name_file, 'w') as out:
            for i, name in enumerate(vec.get_feature_names()):
                out.write("{}\t{}\n".format(i, name))

        with open(node_attribute_file, 'w') as out:
            for node_num, bool_feature_array in enumerate(vectorized_array):
                for attr_num, val in enumerate(bool_feature_array):
                    if val != 0:
                        out.write("{}\t{}\n".format(node_num, attr_num))
    except:
        print("Error writing attribute info")
        return None

    return (node_attribute_name_file, node_attribute_file)


def setup(G, include_header=True):
    snap_home = os.path.join(os.path.dirname(circulo.__path__._path[0]), "lib","snap")

    if not os.path.exists(os.path.join(snap_home,"examples","bigclam","bigclam")):
        raise Exception("SNAP must be downloaded and built prior to using the snap algorithms")

    f = tempfile.mkstemp()
    filename = f[1]

    try:

        #some snap algos can't handle single space edge delimiters, and igraph can't output
        #tab delimited edgelist, so we always convert the single spaced output to a tabbed output
        with open(filename, 'w') as out:
            if include_header:
                out.write("# Directed Node Graph\n")
                out.write("# Descriptions\n")
                out.write("# Nodes: {}\tEdges: {}\n".format(len(G.vs), len(G.es)))
                out.write("# SrcNId\tDstNId\n")
            for src in G.vs:
                for dst in src.neighbors(mode=igraph.ALL):
                    out.write("{}\t{}\n".format(src.index, dst.index))
                #print(node.neighbors())
            #for u,v in G.get_edgelist():
            #    out.write("{}\t{}\n".format(u, v))
            #    out.write("{}\t{}\n".format(v, u))

    except:
        print("Error writing edgelist")
        return None

    return (snap_home, filename)
