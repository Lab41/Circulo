# coding: utf-8
__author__ = 'aganesh, paulm'

import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import igraph
from itertools import izip


#TODO Items:
#1. Implement Cohesiveness
#2. Implement TPR
#3. Enable overlapping community metrics
#4. Unit Tests
#5. Integrate omega index scoring

def f1(communities, ground_truth, out):

    out.write("Evaluating F1 score\n")
    out.write("{} Communities in ground truth\n".format(len(ground_truth)))
    out.write("{} Communities in results\n".format(len(communities)))

    f1_sum_0 = sum([get_highest_f1(x, communities) for x in ground_truth])
    f1_sum_1 = sum([get_highest_f1(x, ground_truth) for x in communities])

    final_score = .5 * (  1.0/float(len(ground_truth)) * f1_sum_0 + 1.0/float(len(communities)) * f1_sum_1)

    print out.write("F1 Score: {}\n".format(final_score))




def get_highest_f1(src_community, community_list):
    """
    Find the best matching community in the list using f1, then return highest score

    :param src_community:   community to base search on
    :param community_list:  list of communities to search in
    """

    max_f1 = 0.0

    for matchee in community_list:
        score = f1_score(src_community, matchee)
        if score > max_f1:
            max_f1 = score

    return max_f1



def f1_score(community_a, community_b):
    """
    according to http://en.wikipedia.org/wiki/F1_score

    F_1 = 2 * (precision * recall) / (precision + recall)

    where precision = #matched / len (set_a)
          recall = #matched / len(set_b)
    """

    intersect_set = set(community_a).intersection(community_b)
    overlap_len = len(intersect_set)

    if overlap_len > 0:
        precision = float(overlap_len) / float(len(community_a))
        recall = float(overlap_len) / float(len(community_b))
        return 2.0 * (precision * recall) /  (precision + recall)
    else:
        return 0.0





def graph_goodness_v2(comm_metrics):
    '''
    Graphs the change in the specified metric across communities relative to conductance
    '''

    metrics = [(c.conductance, c.density, c.degree_avg, c.fomd, c.degree_boundary_avg, c.cut_ratio, c.normalized_cut) for c in comm_metrics]

    metrics_sorted = metrics.sort(key=lambda x: x[0], reverse=True)

    c, d, a, f, e, cr, n  = zip(*metrics)

    plt.subplot(331)
    plt.plot(c)
    plt.title("Conductance")
    plt.subplot(332)
    plt.plot(d)
    plt.title("Density")
    plt.subplot(333)
    plt.plot(a)
    plt.title("Average Degree")
    plt.subplot(334)
    plt.plot(f)
    plt.title("FOMD")
    plt.subplot(336)
    plt.plot(e)
    plt.title("Expansion")
    plt.subplot(337)
    plt.plot(cr)
    plt.title("Cut Ratio")
    plt.subplot(338)
    plt.plot(n)
    plt.title("Normalized Cut")


    plt.show()





def graph_goodness(comm_metrics):
    '''
    Graphs the change in the specified metric across communities
    '''

    plt.subplot(331)
    plt.plot(sorted([c.density for c in comm_metrics ], reverse=True))
    plt.ylabel("Density")

    plt.subplot(332)
    plt.plot(sorted([c.degree_avg for c in comm_metrics ], reverse=True))
    plt.ylabel("Average Degree")

    plt.title("Each graph is sorted highest to lowest y-value")
    plt.subplot(333)
    plt.plot(sorted([c.fomd for c in comm_metrics ], reverse=True))
    plt.ylabel("FOMD")

    plt.subplot(334)
    plt.plot(sorted([c.tpr[1] for c in comm_metrics ], reverse=True))
    plt.ylabel("TPR")

    plt.subplot(335)
    plt.plot(sorted([c.degree_boundary_avg for c in comm_metrics ], reverse=True))
    plt.ylabel("Expansion")

    plt.subplot(336)
    plt.plot(sorted([c.cut_ratio for c in comm_metrics ], reverse=True))
    plt.ylabel("Cut-Ratio")

    plt.subplot(337)
    plt.plot(sorted([c.conductance for c in comm_metrics ], reverse=True))
    plt.ylabel("Conductance")

    plt.subplot(338)
    plt.plot(sorted([c.normalized_cut for c in comm_metrics ], reverse=True))
    plt.ylabel("Normalized Cut")

    plt.subplot(339)
    plt.plot(sorted([c.separability for c in comm_metrics ], reverse=True))
    plt.ylabel("Separability")

    plt.show()



def do_modularity(comm_metrics, G):
    '''
    Wrote another implementation of modularity for fun
    '''

    res = 0

    for metric in comm_metrics:
        res += (metric.edge_in_count / G.ecount()) - (metric.degree_sum / (G.ecount() * 2.))**2

    return res





class ClusterMetric:
    '''
    Internal Connectivity Metrics
    '''

    def __init__(self, cluster_id, clustering, median_degree_G=None):

        self.clustering = clustering
        self.cluster_id = cluster_id
        self.cluster = clustering.__getitem__(cluster_id)
        self.G = clustering.graph
        self.median_degree_G = median_degree_G

        self.edge_in_count = 0.0
        self.edge_boundary_count = 0.0

        self.degree_in_dict = {}
        self.degree_boundary_dict = {}


        #for efficiency pruposes we allow the caller to send in the median
        if self.median_degree_G is None:
            self.median_degree_G = sum(self.G.degree())/self.G.vcount()


        for v in self.cluster:
            self.degree_in_dict[v] = 0
            self.degree_boundary_dict[v] = 0


        for v in self.cluster:
            for neighbor in self.G.neighbors(v):
                #if the neighbor is in the cluster
                if clustering.membership[neighbor] == cluster_id:
                    self.degree_in_dict[v]+=1
                    if neighbor != v:
                        self.edge_in_count+=.5
                    else:  #self edge only is counted once
                        self.edge_in_count+= 1.0
                else:
                    self.edge_boundary_count+=1.0
                    self.degree_boundary_dict[v]+=1

        self.degree_in_sum = sum(self.degree_in_dict.values())
        self.degree_boundary_sum = sum(self.degree_boundary_dict.values())
        self.degree_sum = sum(self.G.degree(self.cluster))
        self.density = self.do_density()
        self.degree_in_avg = self.do_degree_in_avg()
        self.degree_avg = self.do_degree_avg()
        self.fomd = self.do_fomd()

        self.degree_boundary_avg = self.do_degree_boundary_avg()
        self.cut_ratio = self.do_cut_ratio()
        self.conductance = self.do_conductance()
        self.normalized_cut = self.do_normalized_cut(self.conductance)
        self.odf_dict = self.do_odf()
        self.separability = self.do_separability()
        self.cohesiveness = self.do_cohesiveness()
        self.clustering_coefficient = self.do_clustering_coefficient()
        self.tpr = self.do_tpr()

    def __str__(self):

        #print self(G.summary(verbosity=verbosity))
        report =  """
             Cluster ID: {cluster_id}

             Density:             {density}
             Average Degree:      {avg_degree}
             Frac Over Med Deg:   {fomd}
             Expansion:           {expansion}
             Cut Ratio:           {cut_ratio}
             Conductance:         {conductance}
             Normalized Cut:      {normalized_cut}
             TPR:                 {tpr}
             Out Degree Frac:     {odf}
             Separability:        {separability}
             Cohesiveness:        {cohesiveness}
             Clustering Coeff.:   {clustering_coefficient}
        """.format(cluster_id = self.cluster_id,
                    density=self.density,
                     avg_degree=self.degree_avg,
                     fomd=self.fomd,
                     expansion=self.degree_boundary_avg,
                     cut_ratio=self.cut_ratio,
                     conductance=self.conductance,
                     normalized_cut=self.normalized_cut,
                     tpr=self.tpr[1],
                     odf=self.odf_dict,
                     separability=self.separability,
                     cohesiveness=self.cohesiveness,
                     clustering_coefficient=self.clustering_coefficient)
        return report

    def do_density(self):
        '''
        Calculates the density of a community as the ratio of internal edges to the total possible edges

        '''

        if len(self.cluster) <= 1:
            return 1.0

        return  self.edge_in_count/(len(self.cluster) * (len(self.cluster) -1 ) / 2.0)


    def do_degree_in_avg(self):
        '''
        Calculates the average internal degree of the nodes in the community

        Equation: sum(degrees indegree of each node) / n
        '''

        return self.degree_in_sum/float(len(self.cluster))


    def do_degree_boundary_avg(self):
        '''
        Calculated the average boundary edge degree of the nodes in the community as the total number of
        boundary edges divided by the number of nodes. This is also known as expansion
        '''

        return self.degree_boundary_sum/float(len(self.cluster))


    def do_fomd(self):
        '''
        Fraction of nodes of subgraph that have internal degree higher than the median degree value of entire set of graph nodes
        '''

        return sum(1 for v in self.degree_in_dict.values() if v > self.median_degree_G)/float(self.G.vcount())


    def do_tpr(self):
        '''
        Triangle Participation Ratio (TPR) is the fraction of nodes in S that belong to a triad
        Dictionary where nodes are the keys and values are the number of triangles that include the node as a vertex

        For more information on the triad_census function in iGraph, help(igraph.datatypes.TriadCensus)

        Current Triangles we are identifying
        - C{201} -- C{A <-> B <-> C}
        '''

        node_dict = dict()

        for v in self.cluster:
            node_dict[v] = 0

        for i in self.cluster:
            for j in self.G.neighbors(i):
                if j != i and node_dict.has_key(j):
                    for k in self.G.neighbors(j):
                        if k != j and node_dict.has_key(k):
                            node_dict[i]+=1
                            node_dict[j]+=1
                            node_dict[k]+-1


        node_count = 0

        for k, v in node_dict.iteritems():
            node_dict[k] = v/3
            if v > 0:
                node_count+=1

        return node_dict, node_count/float(len(self.cluster))



    def do_cut_ratio(self):
        '''
        Fraction of existing edges (out of all possible edges) leaving the cluster

        '''
        return self.degree_boundary_sum / float(  len(self.cluster) * (self.G.vcount() - len(self.cluster)))


    def do_conductance(self):
        '''
        Measures the fraction of total edge volume that points outside the cluster

        Equation: boundary_edges / num_directed_edges_originating_from_community
        '''

        return self.degree_boundary_sum / float((2 * self.G.ecount()) + self.degree_boundary_sum)


    def do_normalized_cut(self, conductance):
        '''
        Normalized Cut Metric

        Equation: conductance + ( num_boundary_edges / ( 2 * (|parent_E| - m) + num_boundary_edges)
        '''


        return conductance + self.degree_boundary_sum / (2 * (self.G.ecount() - self.edge_in_count) + self.degree_boundary_sum)


    def do_degree_avg(self):
        '''
        Calculates the average degree
        '''

        return sum(self.G.degree(self.cluster))/float(len(self.cluster))


    def do_odf(self):
        '''
        Out Degree Fraction

        Calculates the out degree fraction (ODF) of each node in a community. The ODF is the fraction of
        edges from a node that that point outside the community

        returns ODF output
        '''

        max_odf = -1
        sum_odf = 0.0
        few_count = 0.0

        for node_idx, degree in zip(self.cluster, self.G.degree(self.cluster)):
            if degree <=0:
                continue
            num_boundary_edges = self.degree_boundary_dict[node_idx]
            odf = num_boundary_edges / float(degree)
            sum_odf += odf

            if odf > max_odf:
                 max_odf = odf
            if num_boundary_edges > degree - num_boundary_edges:
                 few_count += 1

        flake_odf = few_count / float(len(self.cluster))
        avg_odf = sum_odf / float(len(self.cluster))

        return {"average":avg_odf, "flake":flake_odf, "max":max_odf}


    def do_separability(self):
        '''
        Measure ratio between the internal and the external number of edges of S
        '''

        if self.degree_boundary_sum == 0:
            return 0
        return self.degree_in_sum/float(self.degree_boundary_sum)



    def do_cohesiveness(self):
        '''
        Equation: g(S) = minS′⊂S φ(S′) where φ(S′) is the conductance of S′ measured in the induced subgraph by S.
        (cite: http://cs.stanford.edu/people/jure/pubs/comscore-icdm12.pdf)
        '''

        #TODO: Implement cohesiveness. The idea here is to find the smallest conductance score among all subsets of nodes
        #in the community.  To test every possible subset of communities would be a fairly expensive operation 2**n,
        #therefore, we use Local Spectral Clustering  to appoximate the minimum conductance


        #first we must induce a graph from the cluster. A manageable size is 100 nodes, so if the cluster has fewer than
        #100 nodes, then just induce the graph using all nodes, otherwise induce the graph from a random 100 nodes

        if len(self.cluster) < 100:
            G_i = self.G.induced_subgraph(self.cluster)
        else:
            #pick a random 100 from the cluster, for now just the top 100
            G_i = self.G.induced_subgraph(self.cluster[:100])


        #next we need to efficienty approximate the best sub cluster in the current cluster.  The conductance score of the
        #best cluster should be the lowest among all sub clusters. This value will be our cohesiveness. To approximate the
        #best cluster, we will use local spatial clustering

        #TODO Local Spatial Clustering

        return "Not Yet Implemented"


    def do_clustering_coefficient(self):
        '''
        The clustering coefficient of a community is the average of the local clustering coefficients of each of the vertices
        in the community
        '''

        running_sum = 0.0
        for v in self.cluster:
            edge_count = 0
            neighbors = self.G.neighbors(v)
            neighbors_dict = dict()

            #not quite sure how to deal with this case yet, but for now we will assume that 1 neighbor is a complete graph
            if len(neighbors) <= 1:
                running_sum+=1
                continue

            for n in neighbors:
                if self.clustering.membership[n] == self.cluster_id:
                    neighbors_dict[n] = n

            for n in neighbors:
                if neighbors_dict.has_key(n):
                    for n2 in self.G.neighbors(n):
                        if neighbors_dict.has_key(n2):
                            edge_count+=1

            edge_count = edge_count / 2.0

            running_sum += (edge_count / float( len(neighbors) * ( len(neighbors) - 1) ))

        return running_sum / float(len(self.cluster))



def show_report(comm_metrics, f, clustering):

    f.write("===== Metrics Description =====\n\n")
    f.write("Density\n")
    f.write(ClusterMetric.do_density.__doc__)
    f.write("\n")
    f.write("Average Degree\n")
    f.write(ClusterMetric.do_degree_avg.__doc__)
    f.write("\n")
    f.write("Fraction Over Median Degree (FOMD)")
    f.write(ClusterMetric.do_fomd.__doc__)
    f.write("\n")
    f.write("Triangle Participation Ratio (TPR)")
    f.write(ClusterMetric.do_tpr.__doc__)
    f.write("\n")
    f.write("Average Boundary Edge Count (aka Expansion)")
    f.write(ClusterMetric.do_degree_boundary_avg.__doc__)
    f.write("\n")
    f.write("Cut-Ratio")
    f.write(ClusterMetric.do_cut_ratio.__doc__)
    f.write("\n")
    f.write("Conductance")
    f.write(ClusterMetric.do_conductance.__doc__)
    f.write("\n")
    f.write("Normalized Cut")
    f.write(ClusterMetric.do_normalized_cut.__doc__)
    f.write("\n")
    f.write("Out Degree Fraction (odf)")
    f.write(ClusterMetric.do_odf.__doc__)
    f.write("\n")
    f.write("Separability")
    f.write(ClusterMetric.do_separability.__doc__)
    f.write("\n")
    f.write("Cohesiveness")
    f.write(ClusterMetric.do_cohesiveness.__doc__)
    f.write("\n")
    f.write("Clustering Coefficient")
    f.write(ClusterMetric.do_clustering_coefficient.__doc__)
    f.write("\n")
    f.write("\n\n")

    f.write("####################Metrics Report #########################\n\n")

    #prints adjacency list
    #f.write(clustering.graph.summary(verbosity=1))


    #TODO: make compatible with weights
    weights = None

    f.write("========= Network Centric ==============\n")
    #f.write("Modularity...............{}".format(clustering.graph.modularity(clustering.membership, weights)))
    f.write("Modularity...........{}".format(do_modularity(comm_metrics, clustering.graph)))

    f.write("\n\n")
    f.write("========= Community Centric Averages ===\n")
    f.write("Density..................{}\n".format(sum(c.density for c in comm_metrics)/len(comm_metrics)))
    f.write("Avg_degree.............. {}\n".format(sum(c.degree_avg for c in comm_metrics)/len(comm_metrics)))
    f.write("FOMD.................... {}\n".format(sum(c.fomd for c in comm_metrics)/len(comm_metrics)))
    f.write("TPR......................{}\n".format(sum(c.tpr[1] for c in comm_metrics)/len(comm_metrics)))
    f.write("Avg Boundary Edge Count..{}\n".format(sum(c.degree_boundary_avg for c in comm_metrics)/len(comm_metrics)))
    f.write("Cut-Ratio................{}\n".format(sum(c.cut_ratio for c in comm_metrics)/len(comm_metrics)))
    f.write("Conductance..............{}\n".format(sum(c.conductance for c in comm_metrics)/len(comm_metrics)))
    f.write("Normalized Cut...........{}\n".format(sum(c.normalized_cut for c in comm_metrics)/len(comm_metrics)))
    #f.write("ODF......................{}".format(sum(c.odf for c in comm_metrics)/len(comm_metrics)))
    f.write("Separability.............{}\n".format(sum(c.separability for c in comm_metrics)/len(comm_metrics)))
    f.write("Cohesiveness.............Not Implemented\n")
    f.write("Clustering Coefficent....{}\n".format(sum(c.clustering_coefficient for c in comm_metrics)/len(comm_metrics)))
    f.write("\n\n")


    for m in comm_metrics:
        f.write("{}".format(m))

    f.write("\n\n")




def ground_truth_metrics(comms, ground_truth, G, out):
   f1(comms, ground_truth, out)



def run_analysis(clustering, ground_truth=None, report_file=None):
    '''
    Performs analysis on communities and optionally ground truth

    '''

    print "Running metrics analysis"

    if report_file:
        out = open(report_file, 'w')
    else:
        out = sys.stdout

    G = clustering.graph

    comm_metrics = list()

    for cluster_id in range(len(clustering)):
        comm_metrics.append(ClusterMetric(cluster_id, clustering))

    show_report(comm_metrics, out, clustering)

    #if ground_truth:
    #    f1(communities, ground_truth, out)



    graph_goodness(comm_metrics)


def unit_tests():

    #TODO: write unit tests

    pass


import igraph
from igraph import snap

def main(argv):


    G = igraph.Graph.Erdos_Renyi(n=200, m=300)
    clustering = snap.clauset_newman_moore(G)

    run_analysis(clustering, report_file="report.txt")





if __name__ == "__main__":
    main(sys.argv[1:])
