# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import average,fcluster

import numpy as np
import pickle
 
import argparse

def to_crisp_membership(ovp_membership):
    return [ a[0] for a in ovp_membership ]


def compute_distance_matrix(results):
    # Compute stochastic clusters
    num_results = len(results['vc'])
    distance_matrix= np.zeros((num_results,num_results))
    print('Calculating distance matrix ... ')
    for i in range(num_results):
        for j in range(i+1,num_results):
            #score = metrics.omega_index(results['vc'][i].membership,results['vc'][j].membership)
            #score = skmetrics.f1_score(to_crisp_membership(results['vc'][i].membership),
            #                           to_crisp_membership(results['vc'][j].membership))
            score = skmetrics.adjusted_rand_score(to_crisp_membership(results['vc'][i].membership),
                                                  to_crisp_membership(results['vc'][j].membership))
            distance_matrix[i,j] = 1-score
            distance_matrix[j,i] = 1-score
    distance_matrix = np.matrix(distance_matrix)
    results['metrics.distance_matrix'] = distance_matrix
    print(distance_matrix)

    y = squareform(distance_matrix)
    Z = average(y)
    results['metrics.linkage'] = Z

parser = argparse.ArgumentParser(description='Compute self-distance for given cover set.')
parser.add_argument('cover', type=str, nargs=1, help='pickle file for first cover')
args = parser.parse_args()

results = pickle.load(open(args.cover[0], 'rb'))

compute_distance_matrix(results)

# Output results to pickle
output = open(args.cover[0], 'wb')
pickle.dump(results, output)
output.close()
