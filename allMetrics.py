__author__ = 'aganesh'

import networkx as nx
import sys
import numpy as np
import scipy
import matplotlib.pyplot as plt


#Only for undirected graphs
#Assuming nodes are ints


def main():

    #File IO Handling/Reading in Graph
    #TO DO error checking with file handles
    edgelist_file = open("edgelist.txt", 'rb')
    community_file = open("comm.txt")

    #Creating graph in networkX
    graph = nx.read_edgelist(edgelist_file, comments='#', nodetype=int, edgetype=int)
    edgelist_file.close()

    #Collecting statistics on entire graph
    num_nodes = len(graph)
    num_edges = nx.number_of_edges(graph)
    graph_degree = graph.degree(graph.nodes_iter())
    median_degree = np.median(list(graph_degree.values()))

    avg_odf_list = []

    #Iterating through community file
    for line in community_file:

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

        #Calculation of internal,external, internal & external connectivity, and goodness measures
        int_metrics(num_nodes_s, num_edges_s, internal_degree, comm_subgraph, median_degree)
        ext_metrics(num_nodes_s, num_boundary_edges_s, num_nodes)
        int_ext_metrics(avg_odf_list, num_nodes_s, num_edges_s, num_boundary_edges_s, external_degree, degree, num_edges, internal_degree)
        good_metrics(num_nodes_s, num_edges_s, num_boundary_edges_s)



        #Clear dictionaries
        internal_degree.clear()
        degree.clear()
        external_degree.clear()

    plt.hist(avg_odf_list, 10)
    plt.show()


def int_metrics(num_nodes_s, num_edges_s, internal_degree, comm_subgraph, median_degree):

    #TO DO: Create functions for each of the calculations with explanation
    #internal edge density of the node set S
    internal_density = float(num_edges_s / ((num_nodes_s*(num_nodes_s - 1)) / 2))

    #Number of edges between the members of S
    edges_inside = num_edges_s

    #Average internal degree of the members of S
    avg_degree = (2 * num_edges_s) / num_nodes_s

    #Fraction over median degree (FOMD)
    #Fraction of nodes of S that have internal degree higher than the median degree value of entire set of graph nodes
    node_greater_median = sum(1 for i in internal_degree.values() if i > median_degree)
    fomd = node_greater_median/num_nodes_s

    #Triangle Participation Ratio (TPR) is the fraction of nodes in S that belong to a triad
    #Dictionary where nodes are the keys and values are the number of triangles that include the node as a vertex
    triangles = nx.triangles(comm_subgraph)
    tri_count = sum(x > 0 for x in triangles.values())
    tpr = tri_count / num_nodes_s
    #print("Internal density, Edges Inside, Average Degree, FOMD, TPR")
    #print(internal_density, edges_inside, avg_degree, fomd, tpr)


def ext_metrics(num_nodes_s, num_boundary_edges_s, num_nodes):
    #Measures the number of edges per node that point outside the cluster
    expansion = num_boundary_edges_s/num_nodes_s

    #Fraction of existing edges leaving the cluster
    cut_ratio = num_boundary_edges_s / (num_nodes_s * (num_nodes - num_nodes_s))


def int_ext_metrics(avg_odf_list, num_nodes_s, num_edges_s, num_boundary_edges_s, external_degree, degree, num_edges, internal_degree):
    #Measures the fraction of total edge volume that points outside the cluster
    conductance = num_boundary_edges_s / ((2 * num_edges_s) + num_boundary_edges_s)

    norm_cut = conductance + num_boundary_edges_s / ((2*(num_edges - num_edges_s)) + num_boundary_edges_s)

    #Max-ODF, avgODF, flakeODF
    max_val = -1
    sum_val = 0.0
    few_count = 0.0

    for k, v in external_degree.items():
        div = float(external_degree[k]) / degree[k]
        sum_val += div
        if div > max_val:
            max_val = div
        if external_degree[k] > internal_degree[k]:
            few_count += 1

    #Max fraction of edges of a node in S that points outside S
    max_odf = max_val

    #Avg fraction of edges of nodes in S that point out of S
    avg_odf = sum_val / num_nodes_s
    avg_odf_list.append(avg_odf)

    #Fraction of nodes in S that have fewer edges pointing inside than to the outside of the cluster
    flake_odf = few_count/num_nodes_s


def good_metrics(num_nodes_s, num_edges_s, num_boundary_edges_s):
    #Measure ratio between the internal and teh external number of edges of S
    separability = num_edges_s/num_boundary_edges_s

    #Measures fraction of the edges that appear between the nodes in S
    density = num_edges_s / ((num_nodes_s * (num_nodes_s - 1)) / 2)


if __name__ == "__main__":
    main()
