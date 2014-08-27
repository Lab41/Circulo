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
import datetime
import multiprocessing
import traceback
import sys

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

#def run_single(algo, dataset, output_dir, iterations):
def run_single(tup):

    dataset_name = tup[0]
    algo = tup[1]
    dataset = tup[2]
    output_dir = tup[3]
    iterations = tup[4]

    # Get dataset and run cd algorithm
    data_mod = importlib.import_module('data.'+dataset+'.run')

    # Get community covers
    cc, stochastic = getattr(community, 'comm_'+algo)(data_mod)

    vc_name = dataset + '-' + algo
    vc = []
    elapsed = []

    try:

        for i in range(iterations*stochastic + 1):
            t0 = time.time()
            vc += [to_cover(cc())]
            t_diff = time.time() - t0
            elapsed = [t_diff]

    except Exception as e:
        print("Exception using parameters ",tup,  e)
        traceback.print_exc(file=sys.stdout)
        return
    # Save results
    results = {}
    results['vc_name'] = vc_name
    results['elapsed'] = elapsed
    results['vc'] = vc

    with open(os.path.join(output_dir, vc_name + '.pickle'), 'wb') as f:
        pickle.dump(results, f)

    print("Finished", algo, "algorithm with", dataset, "dataset at", datetime.datetime.now())



def run(algos, datasets, output_dir, iterations):

    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    map_inputs = []
    for algo in algos:
        for dataset in datasets:
            map_inputs.append((algo + ' - ' + dataset, algo, dataset, output_dir, iterations))

    p = multiprocessing.Pool(10)
    p.map(run_single, map_inputs)
    p.close()
    p.join()

def main():

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    data_choices = ['football', 'congress_voting', 'karate', 'malaria', 'nba_schedule', 'netscience', 'flights']
    #data_choices = ['football', 'congress_voting']

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('dataset', nargs=1,choices=['ALL']+data_choices,help='dataset name. ALL will use all datasets')
    parser.add_argument('algo', nargs=1,choices=['ALL']+comm_choices, help='Which community detection to run.')
    parser.add_argument('--output', type=str, nargs=1, default=[OUTPUT_DIR], help='Base output directory')
    parser.add_argument('--samples', type=int, nargs=1, default=[10], help='Number of samples for stochastic algos')

    args = parser.parse_args()

    algos = comm_choices if 'ALL' in args.algo else args.algo
    datasets = data_choices if 'ALL' in args.dataset else args.dataset

    overall_start_time = datetime.datetime.now()
    run(algos, datasets, args.output[0], args.samples[0])
    overall_end_time = datetime.datetime.now()
    print("Time elapsed:", (overall_end_time - overall_start_time))

if __name__ == "__main__":
    main()
