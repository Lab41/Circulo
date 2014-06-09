import os
import subprocess
import tempfile
import sys
import igraph
from  igraph.clustering import VertexClustering, VertexCover


__author__="""Paul M"""

__all__ = []


def read_communities_by_community(f_name, G):
    '''
    Reads a community file in the format where each line represents a community where the line is a list of nodes separated by white space
    '''

    print "Reading communities from file {}".format(f_name)
    comm_list = list()

    with open(f_name, 'rb') as community_file:

        for line in community_file:
            if line.startswith('#'):
                continue
            try:
                comm_list.append(map(int, line.split()))
            except ValueError as e:
                print "Node type is unclear for line: {}".format(line)
                return

    return VertexCover(G, comm_list)


def read_communities_by_node(f_name, G):
    '''
    Reads a community file where each line is a node and the community to which it belongs
    '''

    #dict with keys as community_id and values are a list of nodes
    node_dict = {}
    comm_dict = {}
    comm_list = list()

    highest_cmty_id = -1
    with open(f_name, 'rb') as community_file:
        for line in community_file:
            if line.startswith('#'):
                continue
            node_id, community_id = line.split()
            node_id = int(node_id)
            community_id = int(community_id)

            if node_dict.has_key(node_id):
                print "Error: iGraph standard output does not support overlapping communities"
                return None

            node_dict[node_id] = community_id
            if community_id > highest_cmty_id:
                highest_cmty_id = community_id

    next_node_id = 0

    cmty_list = list()
    for k, v in sorted(node_dict.items()):
        while next_node_id < k:
            highest_cmty_id +=1
            cmty_list.append(highest_cmty_id)
            next_node_id+=1
        cmty_list.append(v)
        next_node_id+=1

    #currently snap will omit nodes that our disconnected from the graph, rather than treat those nodes
    #as 1 node communities. Since every node must be accounted for in iGraph, we must reinsert nodes
    #into s that were omitted by snap. A quick len check below will alert us of this issue

    clustering = None

    try:
        clustering =  VertexClustering(G, cmty_list)
    except ValueError as e:
        print "Error {}".format(e)
        return

    return clustering



def divisive(G, algo_id, output):

    snap_home, graph_file  = setup(G)

    if graph_file is None:
        return

    path_girvan_newman = os.path.join(snap_home, "examples", "community", "community")


    try:
        out = subprocess.Popen([path_girvan_newman, "-i:"+graph_file, "-o:"+output, "-a:"+algo_id])
    except TypeError as e:
        print "Error occurred: {}".format(e)
        return

    out.wait()

    os.remove(graph_file)
    return read_communities_by_node(output, G)

def display_communities(comms, G):
    from random import random
    import matplotlib.pyplot as plt

    print "Displaying"


    pos = nx.fruchterman_reingold_layout(G, k=2)

    #pos=nx.spring_layout(G) # positions for all nodes

    colors = [(random(), random(), random()) for _i in range(len(comms))]

    comm_id = 0
    for c in comms:
        nx.draw_networkx_nodes(G, pos, c.nodes(), node_color=colors[comm_id], node_size=60, alpha=0.8)
        comm_id+=1
    nx.draw_networkx_edges(G, pos, G.edges(), width=1, alplha=0.5, edge_color='grey')

    plt.show()

def main():

    #G = igraph.Graph()
    #G.add_vertices(10)
    #G.add_edges([(1,2)])

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = coda(G)
    print vc

def clauset_newman_moore(G, output="communities.txt"):
    return divisive(G, "2", output)


def girvan_newman(G, output="communities.txt"):
    return divisive(G, "1", output)


def infomap(G, output="communities"):
    return divisive(G, "3", output)


def cesna(G,  f_attributes, f_attribute_names, data_prefix='snap_', nodes='', detect_comm=10, min_comm=3, max_comm=5, trials=5, threads=4, aw=0.5,lw=1, alpha=0.05, beta=0.3, mf=0):

    '''
    Parameters
    -----------
    G:                  A NetworkX graph or edge list file
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

    if graph_file is None:
        return

    path_cesna = os.path.join(snap_home, "examples", "cesna", "cesna")

    try:
        out = subprocess.Popen([path_cesna, "-o:"+data_prefix, "-i:"+graph_file, "-l:"+nodes, "-a:"+f_attributes, "-n:"+f_attribute_names,  "-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-aw:"+str(aw), "-lw:"+str(lw), "-sa:"+str(alpha), "-sb:"+str(beta), "-mf:"+str(mf)]).wait()


    except TypeError as e:
        print "Error occurred: {}".format(e)
        return


    os.remove(graph_file)

    return read_communities(data_prefix + "cmtyvv.txt", G)




def coda(G, data_prefix='snap_', node_filepath='', graph_type=0, detect_comm=100, min_comm=5, max_comm=100, trials=10, threads=4, alpha=0.05, beta=0.3):
    '''
    Coda from Snap

    Parameters
    ----------
    G :                 A NetworkX graph or edge list file
    node_file_path:     Input file name for node names (Node ID, Node label)
    graph_type:         0=directed, 1=undirected (default: 0)
    detect_comm:        The number of communities to detect (-1: detect automatically) (Default: 100)
    min_comm:           Minimum number of communities to try (Default = 5)
    max_comm:           Maximum number of communities to try (Default = 100)
    trials:             How many trials for the number of communities (Default = 10)
    threads:            Number of threads for parallelization (Default = 4)
    alpha:              Alpha for backtracking line search (Default = 0.05)
    beta:               Beta for backtracking line search (Default = 0.3)


    '''

    snap_home, graph_file = setup(G)
    path_coda = os.path.join(snap_home, "examples", "coda", "coda")

    try:

        out = subprocess.Popen([path_coda,"-o:"+data_prefix,"-i:"+graph_file,"-l:"+node_filepath,"-g:"+str(graph_type),"-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-sa:"+str(alpha), "-sb:"+str(beta)]).wait()

    except TypeError as e:
        print "Error occurred: {}".format(e)
        return


    os.remove(graph_file)

    return read_communities_by_community(data_prefix + "cmtyvv.txt", G)



def bigclam(G, data_prefix='snap_', node_filepath='', detect_comm=100, min_comm=5, max_comm=100, trials=10, threads=4, alpha=0.05, beta=0.3):
    '''
    BigClam from Snap

    Parameters
    ----------
    G :                 A NetworkX graph or edge list file
    data_prefix:        Output file for communitities (data_prefix + cmtyvv.txt)
    node_file_path:     Input file name for node names (Node ID, Node label)
    detect_comm:        The number of communities to detect (-1: detect automatically) (Default: 100)
    min_comm:           Minimum number of communities to try (Default = 5)
    max_comm:           Maximum number of communities to try (Default = 100)
    trials:             How many trials for the number of communities (Default = 10)
    threads:            Number of threads for parallelization (Default = 4)
    alpha:              Alpha for backtracking line search (Default = 0.05)
    beta:               Beta for backtracking line search (Default = 0.3)

    Returns:  List of SubGraphs representing the communities.  The SubGraphs are automatically serialized to disk as file data_prefix+'cmtyvv.txt'

    '''

    snap_home, graph_file = setup(G)


    if graph_file is None:
        return

    path_bigclam = os.path.join(snap_home, "examples", "bigclam", "bigclam")

    try:

        out = subprocess.Popen([path_bigclam,"-o:"+data_prefix,"-i:"+graph_file,"-l:"+node_filepath,"-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-sa:"+str(alpha), "-sb:"+str(beta)]).wait()

    except TypeError as e:
        print "Error occurred: {}".format(e)
        return


    os.remove(graph_file)

    return read_communities_by_community(data_prefix + "cmtyvv.txt", G)




ENV_SNAPPATH_VAR = "SNAPHOME"


def setup(G):

    try:
        snap_home = os.environ[ENV_SNAPPATH_VAR]
    except KeyError as e:
        print "Be sure to set your snap base path in the environment variable \"{}\"".format(ENV_SNAPPATH_VAR)
        return None,None

    f = tempfile.mkstemp()
    filename = f[1]

    try:

        #some snap algos can't handle single space edge delimiters, and igraph can't output
        #tab delimited edgelist, so we always convert the single spaced output to a tabbed output
        with open(filename, 'w') as out:
            for u,v in G.get_edgelist():
                out.write("{}\t{}\n".format(u, v))

    except:
        print "Error writing edgelist"
        return None

    return snap_home, filename



if __name__ == "__main__":
    main()
