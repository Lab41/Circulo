import importlib
import igraph
import time
import pickle
from functools import partial
from circulo import metrics
from circulo.wrappers import community
import argparse
import os
from circulo.algorithms.overlap import CrispOverlap

OUTPUT_DIR = "outputs"

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

algos = [
    "infomap",
    "fastgreedy",
    ]

datasets = [
    "football",
    "congress_voting"
    ]

def run_all_parallel(algos=algos, datasets=datasets, output_dir=OUTPUT_DIR, iterations=10):
    #
    # Try using multiprocessing here
    pass


def run_all(algos=algos, datasets=datasets, output_dir=OUTPUT_DIR, iterations=10):

    for algo in algos:
        print ("Analyzing algorithm: \"{}\"".format(algo))
        for dataset in datasets:
            print("\t+ Dataset: {}".format(dataset))
            run(algo, dataset, output_dir, iterations)



def run(algo_name, dataset_name, output_dir, iterations):

    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get dataset and run cd algorithm
    data_mod = importlib.import_module('data.'+dataset_name+'.run')

    # Get community covers
    cc, stochastic = getattr(community, 'comm_'+algo_name)(data_mod)

    vc_name = dataset_name + '-' + algo_name
    vc = []
    elapsed = []

    for i in range(iterations*stochastic + 1):
        t0 = time.time()
        vc += [to_cover(cc())]
        t_diff = time.time() - t0
        elapsed = [t_diff]
        print('size of clusters = {0}'.format(sorted(vc[i].sizes(),reverse=True)))

    # Save results
    results = {}
    results['vc_name'] = vc_name
    results['elapsed'] = elapsed
    results['vc'] = vc

    with open(os.path.join(output_dir, vc_name + '.pickle'), 'wb') as f:
        pickle.dump(results, f)


def main():

    run_all()

    sys.exit(0)

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('dataset', type=str, nargs=1,help='dataset name')

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    parser.add_argument('algo', nargs=1,choices=comm_choices,help='Which community detection to run.')
    parser.add_argument('--output', type=str, nargs=1, default=[OUTPUT_DIR], help='Base output directory')
    parser.add_argument('--samples', type=int, nargs=1, default=[10], help='Number of samples for stochastic algos')

    args = parser.parse_args()

    run(args.algo[0], args.dataset[0], args.output[0], args.samples[0])


if __name__ == "__main__":
    main()
