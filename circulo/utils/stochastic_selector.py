# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import average,fcluster
import igraph
import numpy as np
import pickle


def to_crisp_membership(ovp_membership):
    return [ a[0] for a in ovp_membership ]


def argmax(array):
    return max(zip(array, range(len(array))))[1]


def select(covers):
    #distance_matrix, y, Z = compute_distance_matrix(covers)

    #pick_representatives(covers, distance_matrix, y, Z)

    #for now just return the first cover. TODO: Cluster the covers correctly
    return 0

def pick_representatives(covers, dist_matrix, y, Z):

    mega_clusters = fcluster(Z,.5)

    G = igraph.Graph.Adjacency((dist_matrix < 1).tolist(), 'UNDIRECTED')

    G.vs()['vc'] = covers

    #G.vs()['vc'] = results['vc.orig']  if 'vc.original' in results else results['vc']
    for e in G.es():
        e['weight'] = 1-dist_matrix[e.source, e.target]

    #mega_clusters -= 1
    #cluster = igraph.VertexClustering(G, mega_clusters.tolist())

    #reps = []
    #for s in cluster.subgraphs():
    #    rep_id = argmax(s.strength(weights='weight'))
    #    reps += [ s.vs()[rep_id]['vc'] ]



def compute_distance_matrix(covers):
    # Compute stochastic clusters
    num_results = len(covers)
    distance_matrix= np.zeros((num_results,num_results))
    print('Calculating distance matrix ... ')
    for i in range(num_results):
        for j in range(i+1,num_results):
            #score = metrics.omega_index(results['vc'][i].membership,results['vc'][j].membership)
            #score = skmetrics.f1_score(to_crisp_membership(results['vc'][i].membership),
            #                           to_crisp_membership(results['vc'][j].membership))
            score = skmetrics.adjusted_rand_score(to_crisp_membership(covers[i].membership),
                                                  to_crisp_membership(covers[j].membership))
            distance_matrix[i,j] = 1-score
            distance_matrix[j,i] = 1-score
    distance_matrix = np.matrix(distance_matrix)

    y = squareform(distance_matrix)
    Z = average(y)
    return distance_matrix, y, Z
