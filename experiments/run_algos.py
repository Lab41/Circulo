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
import json

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

def get_largest_component(G):
    """
    Given a graph, returns the subgraph containing only its largest component".
    """
    components = G.components(mode=igraph.WEAK)
    if len(components) == 1:
        return
    print("This graph is unconnected. Using only largest component.")
    print("Original graph: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    G = G.subgraph(max(components, key=len))
    print("Largest component: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    return G

def create_graph_context(G):
    '''
    weight: if G has edge weights the value will be 'weight', else None
    directed: if G is directed, return True, else False
    '''

    return {
        "weight": 'weight' if G.is_weighted() else None,
        "directed": G.is_directed()
            }



#def run_single(algo, dataset, output_dir, iterations):
def run_single(tup):

    vc_name = tup[0]
    algo = tup[1]
    G = tup[2]
    output_dir = tup[3]
    iterations = tup[4]

    #do stuff to G
    get_largest_component(G)
    print(vc_name)
    cc, stochastic = getattr(community, 'comm_'+algo)(G, create_graph_context(G))

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

    print("Finished", vc_name, "in ", elapsed)



def run(algos, datasets, output_dir, iterations):

    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    map_inputs = []

    for dataset in datasets:

        #load the dataset
        data_mod = importlib.import_module('data.'+dataset+'.run')
        G = data_mod.get_graph()
        G_truth = data_mod.get_ground_truth(G)

        #save the ground truth file for later
        with open(os.path.join(output_dir, dataset+'.ground_truth'), "w") as f:
            json.dump(G_truth.membership, f)

        for algo in algos:
            map_inputs.append((algo + ' - ' + dataset, algo, G, output_dir, iterations))

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
