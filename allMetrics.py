__author__ = 'aganesh'

import networkx as nx
import sys
import numpy as np
import matplotlib.pyplot as plt


#Using undirected graph as model
#Assuming nodes are ints but can easily be extended


def main(argv):

    with open(argv[0], 'rb') as edgelist_file:

        #Creating graph in networkX
        graph = nx.read_edgelist(edgelist_file, comments='#', nodetype=int, edgetype=int)

    #Collecting statistics on entire graph
    num_nodes = len(graph)
    num_edges = nx.number_of_edges(graph)
    graph_degree = graph.degree(graph.nodes_iter())
    median_degree = np.median(list(graph_degree.values()))

    #Demo sample metrics collected for visualization
    cond_list = []
    cut_list = []
    flake_list = []
    fomd_list = []
    tpr_list = []
    sep_list = []
    num_comm = 0

    with open(argv[1]) as community_file:

        #Iterating through community file
        for line in community_file:
            num_comm += 1

            #Store nodes in each community and equates each community as a sub-graph 's'
            comm_line = map(int, line.split())
            comm_subgraph = graph.subgraph(comm_line)

            #Dictionary with nodes as keys and internal degree (Only edges within S) as values for all nodes in community S
            internal_degree = comm_subgraph.degree()

            #Dictionary with nodes as keys and degree (Includes edges both inside and outside of S) as values
            degree = graph.degree(comm_subgraph)

            #Dictionary with nodes as keys and external degree (edges on the boundary of S) as values
            external_degree = {key: degree[key] - internal_degree[key] for key in internal_degree.keys()}

            #Number of nodes,edges and boundary edges in community
            num_nodes_s = float(nx.number_of_nodes(comm_subgraph))
            num_edges_s = float(nx.number_of_edges(comm_subgraph))
            num_boundary_edges_s = float(sum(external_degree.values()))

            #Graph metrics against goodness metric of separability
            cond_list.append(conductance_metric(num_edges_s, num_boundary_edges_s))
            cut_list.append(cut_ratio_metric(num_boundary_edges_s, num_nodes_s, num_nodes))
            flake_list.append(flake_metric(num_nodes_s, external_degree, internal_degree, degree))
            fomd_list.append(fomd_metric(num_nodes_s, median_degree, internal_degree))
            tpr_list.append(tpr_metric(num_nodes_s, comm_subgraph))
            sep_list.append(separability_metric(num_edges_s, num_boundary_edges_s))

            #Clear dictionaries
            #internal_degree.clear()
            #degree.clear()
            #external_degree.clear()

    #Sort the lists
    cond_list, cond_sep_list = (list(x) for x in zip(*sorted(zip(cond_list, sep_list), reverse=True)))
    cut_list, cut_sep_list = (list(x) for x in zip(*sorted(zip(cut_list, sep_list), reverse=True)))
    flake_list, flake_sep_list = (list(x) for x in zip(*sorted(zip(flake_list, sep_list), reverse=True)))
    fomd_list, fomd_sep_list = (list(x) for x in zip(*sorted(zip(fomd_list, sep_list), reverse=True)))
    tpr_list, tpr_sep_list = (list(x) for x in zip(*sorted(zip(tpr_list, sep_list), reverse=True)))

    #Rank numbering for graph
    x = np.linspace(1, len(sep_list), len(sep_list))

    #plot all the metrics against goodness
    plt.plot(x, cond_sep_list, label="conductance")
    plt.plot(x, cut_sep_list, label="cut ratio")
    plt.plot(x, flake_sep_list, label="flake ODF")
    plt.plot(x, fomd_sep_list, label="FOMD")
    plt.plot(x, tpr_sep_list, label="TPR")
    plt.legend(loc='best')

    #show the plot
    plt.xlabel("Rank")
    plt.ylabel("Separability")
    plt.show()


# *Internal Connectivity Metrics*

#Internal edge density of the node set S
def internal_density_metric(num_nodes_s, num_edges_s):
    return float(num_edges_s / ((num_nodes_s*(num_nodes_s - 1)) / 2))


#Number of edges between the members of S
def edges_inside_metric(num_edges_s):
    return num_edges_s


#Average internal degree of the members of S
def avg_degree_metric(num_edges_s, num_nodes_s):
    return (2 * num_edges_s) / num_nodes_s


#Fraction of nodes of S that have internal degree higher than the median degree value of entire set of graph nodes
def fomd_metric(num_nodes_s, median_degree, internal_degree):

    node_greater_median = sum(1 for i in internal_degree.values() if i > median_degree)
    fomd = node_greater_median/num_nodes_s
    return fomd


#Triangle Participation Ratio (TPR) is the fraction of nodes in S that belong to a triad
def tpr_metric(num_nodes_s, comm_subgraph):

    #Dictionary where nodes are the keys and values are the number of triangles that include the node as a vertex
    triangles = nx.triangles(comm_subgraph)

    tri_count = sum(x > 0 for x in triangles.values())
    tpr = tri_count / num_nodes_s
    return tpr

# *External Connectivity Measures*


#Measures the number of edges per node that point outside the cluster
def expansion_metric(num_nodes_s, num_boundary_edges_s):
    return num_boundary_edges_s/num_nodes_s


#Fraction of existing edges leaving the cluster
def cut_ratio_metric(num_boundary_edges_s, num_nodes_s, num_nodes):
    return num_boundary_edges_s / (num_nodes_s * (num_nodes - num_nodes_s))

# *External and Internal Connectivity Measures*


#Measures the fraction of total edge volume that points outside the cluster
def conductance_metric(num_edges_s, num_boundary_edges_s):
    return num_boundary_edges_s / ((2 * num_edges_s) + num_boundary_edges_s)


def norm_cut_metric(num_edges_s, num_boundary_edges_s, num_edges):
    return conductance_metric(num_edges_s, num_boundary_edges_s) + num_boundary_edges_s / ((2*(num_edges - num_edges_s)) + num_boundary_edges_s)


def odf_metric(num_nodes_s, external_degree, internal_degree, degree):

    max_val = -1
    sum_val = 0.0
    few_count = 0.0
    odf_list = []

    for k, v in external_degree.items():
        div = float(external_degree[k]) / degree[k]
        sum_val += div
        if div > max_val:
            max_val = div
        if external_degree[k] > internal_degree[k]:
            few_count += 1

    flake_odf = few_count/num_nodes_s
    max_odf = max_val
    avg_odf = sum_val / num_nodes_s

    odf_list.extend([flake_odf, max_odf, avg_odf])

    return odf_list


#Max fraction of edges of a node in S that points outside S
def max_odf_metric(num_nodes_s, external_degree, internal_degree, degree):
    temp_list = odf_metric(num_nodes_s, external_degree, internal_degree, degree)
    return temp_list[1]


#Avg fraction of edges of nodes in S that point out of S
def avg_odf_metric(num_nodes_s, external_degree, internal_degree, degree):
    temp_list = odf_metric(num_nodes_s, external_degree, internal_degree, degree)
    return temp_list[2]


#Fraction of nodes in S that have fewer edges pointing inside than to the outside of the cluster
def flake_metric(num_nodes_s, external_degree, internal_degree, degree):
    temp_list = odf_metric(num_nodes_s, external_degree, internal_degree, degree)
    return temp_list[0]

# *Goodness Metrics*


#Measure ratio between the internal and the external number of edges of S
def separability_metric(num_edges_s, num_boundary_edges_s):
    return num_edges_s/num_boundary_edges_s


#Measures fraction of the edges that appear between the nodes in S
def density_metric(num_nodes_s, num_edges_s):
    return num_edges_s / ((num_nodes_s * (num_nodes_s - 1)) / 2)


if __name__ == "__main__":
    main(sys.argv[1:])
