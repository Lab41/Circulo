#!/usr/local/bin/python


import networkx as nx
import sys
import numpy as np
import scipy
import matplotlib.pyplot as plt

#Most variable names follow naming conventions of leskovec/yang papers


def main(argv):
    
    #File IO Handling/Reading in Graph
    f_edge = open(argv[0], 'rb')
    f_comm = open(argv[1])
    G = nx.read_edgelist(f_edge,comments='#',nodetype=int,edgetype=int)
    f_edge.close()
    
    
    #Initializing Important Var
    num_nodes = len(G)
    num_edges = nx.number_of_edges(G)
    comm_set = set()
    degree_dict = G.degree(G.nodes_iter())
    d_m = np.median(list(degree_dict.values()))
    
    
    #Iterating through community file
    for line in f_comm:

        comm_line = map(int, line.split())
        comm_line.sort()
        S = G.subgraph(comm_line)


        int_deg_dict = S.degree()
        t_ext_deg_dict = G.degree(comm_line)
        ext_deg_dict = {key:t_ext_deg_dict[key] - int_deg_dict[key] for key in int_deg_dict.keys()}
        
        
        n_s = float(nx.number_of_nodes(S))
        m_s = float(nx.number_of_edges(S))
        c_s = float(sum(ext_deg_dict.values()))
        
        intConnectMetrics(n_s,m_s,int_deg_dict,S, d_m)
        extConnectMetrics(n_s,c_s, num_nodes)
        intExtMetrics(n_s,m_s,c_s,ext_deg_dict,t_ext_deg_dict,num_edges,int_deg_dict)
        goodnessMetrics(n_s,m_s,c_s)

        
        #Clear dictionaries
        int_deg_dict.clear()
        t_ext_deg_dict.clear()
        ext_deg_dict.clear()
        


def intConnectMetrics(n_s,m_s,int_deg_dict,S, d_m) :
    internal_density = float(m_s / ((n_s*(n_s - 1)) / 2))        
    edges_inside = m_s
    avg_degree = (2 * m_s) / n_s

    #FOMD
    node_greater_dm = sum(1 for i in int_deg_dict.values() if i > d_m)
    fomd = node_greater_dm/n_s 
        
    #TPR
    tri_dict = nx.triangles(S)
    tri_count = np.count_nonzero(tri_dict.values())
    tpr = tri_count / n_s
    tri_dict.clear()


def extConnectMetrics(n_s,c_s,num_nodes):
    expansion = c_s/n_s
    cut_ratio = c_s / (n_s * (num_nodes - n_s))


def intExtMetrics(n_s,m_s,c_s,ext_deg_dict,t_ext_deg_dict,num_edges,int_deg_dict):
    conductance = c_s / ((2 * m_s) + c_s)
    norm_cut = conductance + c_s /((2*(num_edges - m_s)) + c_s)

    #Max-ODF, avgODF, flakeODF
    maxVal = -1
    sumVal = 0.0
    few_count = 0.0

    for k,v in ext_deg_dict.items():
        div = float(ext_deg_dict[k]) / t_ext_deg_dict[k]
        sumVal = sumVal + div
        if(div > maxVal):
            maxVal = div
        if(ext_deg_dict[k] > int_deg_dict[k]):
            few_count += 1

    maxOdf = maxVal
    avgOdf = sumVal / n_s
    flakeOdf = few_count/ n_s



def goodnessMetrics(n_s,m_s,c_s):
    separability = m_s/c_s
    density = m_s / ((n_s * (n_s - 1 )) / 2)


if __name__ == "__main__":
    main(sys.argv[1:])
