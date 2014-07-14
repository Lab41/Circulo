import importlib
import igraph
import os
import time
import circulo
from circulo import metrics
from igraph import VertexClustering, VertexDendrogram
from circulo.algorithms import girvan_newman, congo


def eval_data(title, G, ground_truth, algo_list):

    print("\n======== {} ========\n".format(title))
    for algo in algos:

        print("Testing \"{}\"".format(algo.__name__))

        t0 = time.time()
        result = algo(G)
        t_diff = time.time() - t0
        clustering = None

        if isinstance(result, VertexClustering):
            clustering = result
        elif isinstance(result, VertexDendrogram):
            clustering = result.as_clustering()
        else:
            raise Exception("Algorithm output type not recognized")


        f1 = metrics.f1(clustering, ground_truth)

        print("\t[*] Execution time: {}".format(t_diff))
        print("\t[*] F1 Score: {}".format(f1))




#get school related Graph and ground truth
school_mod = importlib.import_module("data.school.run")
nba_mod = importlib.import_module("data.nba_schedule.run")


ground_truth = school_mod.get_ground_truth()
G = ground_truth.graph
G_nba = nba_mod.get_graph()


algos = [igraph.Graph.community_infomap,
        igraph.Graph.community_fastgreedy,
        igraph.Graph.community_leading_eigenvector,
        igraph.Graph.community_walktrap,
        #igraph.Graph.community_edge_betweenness,   #commented because slow
        #girvan_newman.gn                          #commented because slow
        ]


eval_data("School Data",G, ground_truth, algos)
eval_data("NBA Data", G_nba, nba_mod.get_ground_truth(G_nba), algos)



