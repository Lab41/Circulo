import importlib
import igraph 
import time
import pickle
from functools import partial
from circulo import metrics
from circulo.wrappers import community
import argparse
from circulo.algorithms.overlap import CrispOverlap

def to_cover(result):
    cover = None
    if isinstance(result, igraph.VertexClustering):
        cover = result.as_cover()
    elif isinstance(result, igraph.VertexDendrogram):
        cover = result.as_clustering().as_cover()
    elif isinstance(result,CrispOverlap):
        cover = result.as_cover()
    elif isinstance(result, igraph.VertexCover):
        cover = result
    else:
        raise Exception("Algorithm output type not recognized")
    return cover


# Parse user input
parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
parser.add_argument('dataset', type=str, nargs=1, 
                          help='dataset name')

comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
parser.add_argument('algo', nargs=1,
        choices=comm_choices,
        help='Which community detection to run.')
parser.add_argument('--output', nargs=1, default='./', help='Base output directory')
parser.add_argument('--samples', type=int, nargs=1, default=10, help='Number of samples for stochastic algos')

args = parser.parse_args()


# Get dataset and run cd algorithm
data_set_name = args.dataset[0]
algo_name = args.algo[0]
data_mod = importlib.import_module(data_set_name+'.run')

# Get community covers
cc, stochastic = getattr(community, 'comm_'+algo_name)(data_mod)

vc_name = data_set_name + '-' + algo_name
vc = []
elapsed = []
Ns = args.samples # number of times to run stochastic algorithm
for i in range(Ns*stochastic + 1):
    t0 = time.time()
    vc += [to_cover(cc())]
    t_diff = time.time() - t0
    elapsed = [t_diff]
    print('size of clusters = ',sorted(vc[i].sizes(),reverse=True))

# Save results
results = {}
results['vc_name'] = vc_name
results['elapsed'] = elapsed
results['vc'] = vc

# Output results to pickle
output = open(args.output[0] + '/' + vc_name + '.pickle', 'wb')
pickle.dump(results, output)
output.close()

