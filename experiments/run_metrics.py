# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
import numpy as np
import pickle
import argparse

parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
parser.add_argument('cover', type=str, nargs=1, 
                          help='pickle file for first cover')
args = parser.parse_args()

results = pickle.load(open(args.cover[0], 'rb'))

# Compute cover metrics
print('Calculating cover metrics... ')
for cover in results['vc']:
    weights = 'weight' if cover.graph.is_weighted() else None
    cover.compute_metrics(weights=weights) 

# Output results to pickle
output = open(args.cover[0], 'wb')
pickle.dump(results, output)
output.close()
