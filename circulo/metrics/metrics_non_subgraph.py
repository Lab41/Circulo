# coding: utf-8
__author__ = 'aganesh, paulm'

import sys
import numpy as np
import matplotlib.pyplot as plt
import os
import igraph
from circulo.algorithms import spectral
from circulo.algorithms import overlap
from collections import namedtuple
import numpy as np
import sklearn.metrics
import json
import statistics

'''
TODO:

    - Integrate omega index scoring
    - Verify/modify for overlapping communities
    - Enable weights
    - Unit tests
    - Enable direction
'''


def f1(communities, ground_truth, out=None):
    '''
    Evaluates an input communities clustering to a ground truth clustering
    '''

    return sklearn.metrics.f1_score(ground_truth.membership, communities.membership)




class ClusterMetric:
    '''
    Internal Connectivity Metrics
    '''

    def __init__(self):
        self.cover = None
        self.cover_id = None
        self.community = None
        self.G = None
        self.edge_in_count = None
        self.edge_boundary_count = None

        #degree caches
        self.median_degree_G = None
        self.degree_sum = None
        self.median_degree_G = None
        self.degree_in_dict = None
        self.degree_boundary_dict = None
        self.degree_avg = None
        self.degree_boundary_avg = None

        #metrics
        self.num_nodes = None
        self.num_internal_edges = None
        self.num_external_edges = None
        self.density = None
        self.fomd = None
        self.cut_ratio = None
        self.conductance = None
        self.normalized_cut = None
        self.odf_dict = None
        self.separability = None
        self.cohesiveness = None
        self.clustering_coefficient = None
        self.tpr = None

    def generateMetric(cover_id, cover, median_degree_G=None):

        m = ClusterMetric()
        m.cover = cover
        m.cover_id = cover_id
        m.community = cover[cover_id]
        m.G = cover.graph
        m.median_degree_G = median_degree_G
        m.edge_in_count = 0.0
        m.edge_boundary_count = 0.0
        m.degree_in_dict = {}
        m.degree_boundary_dict = {}

        #for efficiency pruposes we allow the caller to send in the median
        #however, if not provided we must calculate it
        if m.median_degree_G is None:
            m.median_degree_G = statistics.median(m.G.degree())

        #set all values to 0 by default
        for v in m.community:
            m.degree_in_dict[v] = 0
            m.degree_boundary_dict[v] = 0

        for v in m.community:
            for neighbor in m.G.neighbors(v):
                #if the neighbor is in the cluster
                if cover_id in m.cover.membership[neighbor]:
                    m.degree_in_dict[v]+=1
                    if neighbor != v:
                        m.edge_in_count+=.5
                    else:  #m edge only is counted once
                        m.edge_in_count+= 1.0
                else:
                    m.edge_boundary_count+=1.0
                    m.degree_boundary_dict[v]+=1

        m.degree_in_sum = sum(m.degree_in_dict.values())
        m.degree_boundary_sum = sum(m.degree_boundary_dict.values())
        m.degree_sum = sum(m.G.degree(m.community))
        m.density = m.do_density()
        m.degree_in_avg = m.do_degree_in_avg()
        m.degree_avg = m.do_degree_avg()
        m.fomd = m.do_fomd()

        m.degree_boundary_avg = m.do_degree_boundary_avg()
        m.cut_ratio = m.do_cut_ratio()
        m.conductance = m.do_conductance()
        m.normalized_cut = m.do_normalized_cut(m.conductance)
        m.odf_dict = m.do_odf()
        m.separability = m.do_separability()
        m.cohesiveness = m.do_cohesiveness()
        m.clustering_coefficient = m.do_clustering_coefficient()
        m.tpr = m.do_tpr()

        return m

    def to_dict(self):

        return {
                    'density': self.density,
                    'degree_avg': self.degree_avg,
                    'fomd':self.fomd,
                    'expansion': self.degree_boundary_avg
                }



    def __str__(self):

        #print self(G.summary(verbosity=verbosity))
        report =  """
             Cluster ID: {cover_id}

             Nodes:               {nodes}
             Internal Edges:      {internal_edges}
             External Edges:      {external_edges}
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
        """.format(cover_id = self.cover_id,
                    density=self.density,
                    nodes=self.num_nodes,
                    internal_edges=self.num_internal_edges,
                    external_edges=self.num_external_edges,
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

        if len(self.community) <= 1:
            return 1.0

        return  self.edge_in_count/(len(self.community) * (len(self.community) -1 ) / 2.0)


    def do_degree_in_avg(self):
        '''
        Calculates the average internal degree of the nodes in the community

        Equation: sum(degrees indegree of each node) / n
        '''

        return self.degree_in_sum/float(len(self.community))


    def do_degree_boundary_avg(self):
        '''
        Calculated the average boundary edge degree of the nodes in the community as the total number of
        boundary edges divided by the number of nodes. This is also known as expansion
        '''

        return self.degree_boundary_sum/float(len(self.community))


    def do_fomd(self):
        '''
        Fraction of nodes of subgraph that have internal degree higher than the median degree value of entire set of graph nodes
        '''
        
        return sum(1 for v in self.degree_in_dict.values() if v > self.median_degree_G)/float(len(self.community))


    def do_tpr(self):
        '''
        Triangle Participation Ratio (TPR) is the fraction of nodes in S that belong to a triad
        Dictionary where nodes are the keys and values are the number of triangles that include the node as a vertex

        For more information on the triad_census function in iGraph, help(igraph.datatypes.TriadCensus)

        Current Triangles we are identifying
        - C{201} -- C{A <-> B <-> C}
        '''

        node_dict = dict()

        for v in self.community:
            node_dict[v] = 0

        for i in self.community:
            for j in self.G.neighbors(i):
                if j != i and j in node_dict:
                    for k in self.G.neighbors(j):
                        if k != j and k != i and  k in self.G.neighbors(i) and k in node_dict:
                            node_dict[i]+=1


        node_count = 0

        for k, v in node_dict.items():
            if v > 0:
                node_count+=1

        return node_dict, node_count/float(len(self.community))



    def do_cut_ratio(self):
        '''
        Fraction of existing edges (out of all possible edges) leaving the community

        '''
        return self.degree_boundary_sum / float(  len(self.community) * (self.G.vcount() - len(self.community)))


    def do_conductance(self):
        '''
        Measures the fraction of total edge volume that points outside the community

        Equation: boundary_edges / num_directed_edges_originating_from_community
        '''

        return self.degree_boundary_sum / float((2 * self.edge_in_count) + self.degree_boundary_sum)


    def do_normalized_cut(self, conductance):
        '''
        Normalized Cut Metric

        Equation: conductance + ( num_boundary_edges / ( 2 * (|parent_E| - m) + num_boundary_edges)
        '''

        #for now we consider a lone vertex community to have a normalized cut of 1
        if len(self.community) == 1:
            return 1.0

        return conductance + self.degree_boundary_sum / (2 * (self.G.ecount() - self.edge_in_count) + self.degree_boundary_sum)


    def do_degree_avg(self):
        '''
        Calculates the average degree
        '''

        return (2*self.edge_in_count)/float(len(self.community))


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

        for node_idx, degree in zip(self.community, self.G.degree(self.community)):
            if degree <=0:
                continue
            num_boundary_edges = self.degree_boundary_dict[node_idx]
            odf = num_boundary_edges / float(degree)
            sum_odf += odf

            if odf > max_odf:
                 max_odf = odf
            if num_boundary_edges > degree - num_boundary_edges:
                 few_count += 1

        flake_odf = few_count / float(len(self.community))
        avg_odf = sum_odf / float(len(self.community))

        return {"average":avg_odf, "flake":flake_odf, "max":max_odf}


    def do_separability(self):
        '''
        Measure ratio between the internal and the external number of edges of S
        '''

        if self.degree_boundary_sum == 0:
            return 0
        return self.edge_in_count/float(self.degree_boundary_sum)



    def do_cohesiveness(self):
        '''
        Equation: g(S) = maxS′⊂S φ(S′) where φ(S′) is the conductance of S′ measured in the induced subgraph by S.
        To iterate over all possible subgraphs of a community would be too inefficient 2^n, therefore we approximate
        the best subgraph (which would have the lowest conductance) by using Local Spectral communitying to find the best
        cut
        (cite: http://cs.stanford.edu/people/jure/pubs/comscore-icdm12.pdf)
        '''

        #first we must induce a graph from the community. A manageable size is 100 nodes, so if the community has fewer than
        #100 nodes, then just induce the graph using all nodes, otherwise induce the graph from a random 100 nodes
        #if len(self.community) < 100:
        #    G_i = self.G.induced_subgraph(self.community)
        #else:
            #pick a random 100 from the community, for now just the top 100
        #     G_i = self.G.induced_subgraph(self.community[:100])
        G_i = self.G.induced_subgraph(self.community)
        # We decided that a single or two-node community can't be divided further
        if G_i.vcount() <= 2:
            val = 1
        else:
            #TODO: Consider using G_i.mincut() instead.
            val, vc = spectral.min_conductance(G_i)

        return val


    def do_clustering_coefficient(self):
        '''
        The clustering coefficient of a community is the average of the local clustering coefficients of each of the vertices
        in the community
        '''

        running_sum = 0.0
        for v in self.community:
            edge_count = 0
            neighbors = self.G.neighbors(v)
            neighbors_dict = dict()

            #Assumes that 2 neighbors are required to calculate this metric, otherwise, returns zero
            if len(neighbors) <= 1:
                continue

            for n in neighbors:
                if self.cover_id in self.cover.membership[n]:
                    neighbors_dict[n] = n
            if len(neighbors_dict) <= 1 :
                 continue
                
            for n in neighbors:
                if n in neighbors_dict:
                    for n2 in self.G.neighbors(n):
                        if n2 in neighbors_dict:
                            edge_count+=1

            denom =   float( len(neighbors_dict) * ( len(neighbors_dict) - 1) )
            local_coeff =  float(edge_count/denom)
            running_sum += local_coeff

        return running_sum / float(len(self.community))



class VertexCoverMetric:

    def __init__(self):
        self.cover = None
        self.comm_metrics = list()
        self.modularity = None

    def run_analysis(cover, weights="weight"):
        '''
        :cover: the vertex cover representing the communities
        '''

        #create the instance
        coverMetric = VertexCoverMetric()

        num_comms = len(cover)

        #calculate metrics
        coverMetric.comm_metrics = [ClusterMetric.generateMetric(cover_id, cover) for cover_id in range(num_comms)]
        coverMetric.cover = cover

        get_sigmas( (c.density for c in coverMetric.comm_metrics), num_comms )
        get_sigmas( (c.separability for c in coverMetric.comm_metrics), num_comms )
        get_sigmas( (c.cohesiveness for c in coverMetric.comm_metrics), num_comms )
        get_sigmas( (c.clustering_coefficient for c in coverMetric.comm_metrics), num_comms )


        coverMetric.modularity = overlap.lazar_modularity(cover.graph, cover)

        return coverMetric

    def report(self, f=sys.stdout):

        G = self.cover.graph
        print("Degrees") 
        print(G.degree())

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
        #could also use the igrpah modularity function too
        f.write("Modularity.............{}".format(self.modularity))

        num_comms = len(self.comm_metrics)

        #TODO: Ratio Cut for the network
        f.write("\n\n")
        f.write("========= Community Centric Averages ===\n")
        f.write("Density..................{}\n".format(sum(c.density for c in self.comm_metrics)/num_comms))
        f.write("Avg_degree.............. {}\n".format(sum(c.degree_avg for c in self.comm_metrics)/num_comms))
        f.write("FOMD.................... {}\n".format(sum(c.fomd for c in self.comm_metrics)/num_comms))
        f.write("TPR......................{}\n".format(sum(c.tpr[1] for c in self.comm_metrics)/num_comms))
        f.write("Avg Boundary Edge Count..{}\n".format(sum(c.degree_boundary_avg for c in self.comm_metrics)/num_comms))
        f.write("Cut-Ratio................{}\n".format(sum(c.cut_ratio for c in self.comm_metrics)/num_comms))
        f.write("Conductance..............{}\n".format(sum(c.conductance for c in self.comm_metrics)/num_comms))
        f.write("Normalized Cut...........{}\n".format(sum(c.normalized_cut for c in self.comm_metrics)/num_comms))
        #f.write("ODF......................{}".format(sum(c.odf for c in comm_metrics)/len(comm_metrics)))
        f.write("Separability.............{}\n".format(sum(c.separability for c in self.comm_metrics)/num_comms))
        f.write("Cohesiveness.............{}\n".format(sum(c.cohesiveness for c in self.comm_metrics)/num_comms))
        f.write("Clustering Coefficent....{}\n".format(sum(c.clustering_coefficient for c in self.comm_metrics)/num_comms))
        f.write("\n\n")


        for m in self.comm_metrics:
            f.write("{}".format(m))

        f.write("\n\n")


    def to_json(self, out="metrics.json"):

        ret = json.dumps(
                    {'metrcs':
                        {'moduarity':self.modularity,
                         'communities': [ m.to_dict() for m in self.comm_metrics]
                         }
                    }
                    )

        with open(out, "w") as f:
            f.write(ret)



def ground_truth_metrics(comms, ground_truth, G, out):
   f1(comms, ground_truth, out)



def get_sigmas(generator, num_comms):
    '''
    given a generator and the number of communities, this will return the sorted differences from the mean
    as tuples (difference, cluster_id) and the std deviation.
    '''
    arr = np.empty([num_comms], dtype='float')

    for idx, item in enumerate(generator):
        arr[idx] = item

    mean = np.mean(arr)
    std = np.mean((arr - mean) ** 2) **.5

    diffs = list()

    for cluster_id, item in enumerate(arr):
        diffs.append( (abs(item - mean), cluster_id) )

    #sort in place
    diffs.sort(key=lambda t: t[0])

    return diffs, std

def unit_tests():

    #TODO: write unit tests

    pass

