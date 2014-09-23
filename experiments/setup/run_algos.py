import importlib
import igraph
import time
import pickle
from functools import partial
from circulo import metrics
from circulo.wrappers import community
from circulo.wrappers.community import stochastic_algos
import argparse
import os
from circulo.algorithms.overlap import CrispOverlap
import circulo.utils.stochastic_selector as selector
import datetime
import multiprocessing
import traceback
import sys
import json
from collections import namedtuple
from scipy.cluster.hierarchy import average,fcluster
from sklearn import metrics as skmetrics
from scipy.spatial.distance import squareform
from scipy.cluster.hierarchy import average,fcluster
import shutil


Worker = namedtuple('Worker', 'job_name algo dataset out_dir iteration timeout ctx')

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

def get_largest_component(G, descript="not specified"):
    """
    Given a graph, returns the subgraph containing only its largest component".
    """
    components = G.components(mode=igraph.WEAK)
    if len(components) == 1:
        return G
    print("[Graph Prep -",descript,"]... Disconnected Graph Detected. Using largest component.")
    print("[Graph Prep -",descript,"]... Original graph: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    G = G.subgraph(max(components, key=len))
    print("[Graph Prep -",descript,"]... Largest component: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    return G



def create_graph_context(G):
    '''
    graph: Graph
    weight: if G has edge weights the value will be 'weight', else None
    directed: if G is directed, return True, else False
    '''

    return {
            "graph" : G,
            "weight": 'weight' if G.is_weighted() else None,
            "directed": G.is_directed(),
            "simple":G.is_simple()
            }



class TimeoutError(Exception):
    pass



def __handle_timeout(signum, frame):
    raise TimeoutError(os.strerror(errno.ETIME))

import signal
import os
import errno

def run_single(worker):

    print("#### Processing: ", worker.job_name)

    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)
    t0 = time.time()

    func = getattr(community, 'comm_'+worker.algo)(worker.ctx, worker.job_name)

    try:
        r = func()
        vc = to_cover(r)
    except TimeoutError as t:

        print("[ERROR TIMEOUT ", worker.algo, "-",worker.dataset, "] total time: ", time.time() - t0)
        #signal.alarm(0)
        return
    except Exception as e:
        print("Exception using parameters ",worker,  e)
        traceback.print_exc(file=sys.stdout)
        return

    results = {
            'job_name': worker.job_name,
            'elapsed' : time.time() - t0,
            'membership' : vc.membership,
            'algo' : worker.algo,
            'dataset' : worker.dataset,
            'iteration' : worker.iteration
            }

    #write to json
    with open(os.path.join(worker.out_dir, "json", worker.job_name+'.json'), "w") as f:
        json.dump(results, f)

    #write to a pickle
    #with open(os.path.join(worker.out_dir, "pickle",worker.job_name + '.pickle'), 'wb') as f:
    #    pickle.dump(results, f)

    print("\t[Info - ", worker.job_name,"] Finished in ", results['elapsed'])



def run(algos, datasets, output_dir, iterations, workers, timeout):

    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    map_inputs = []

    graph_dir = os.path.join(output_dir, "graphs")
    json_dir = os.path.join(output_dir, "json")
    #pickle_dir = os.path.join(output_dir, "pickle")

    if not os.path.exists(graph_dir):
        os.mkdir(graph_dir)

    if not os.path.exists(json_dir):
        os.mkdir(json_dir)

    #if not os.path.exists(pickle_dir):
    #    os.mkdir(pickle_dir)

    for dataset in datasets:

        #load the dataset
        data_mod = importlib.import_module('data.'+dataset+'.run')

        print("[Graph Prep -",dataset,"]... Initiated")
        G = data_mod.get_graph()
        G = get_largest_component(G, dataset)

        try:
            G.write_graphml(os.path.join(output_dir, "graphs", dataset+".graphml"))
        except Exception as e:
            print("Unable to serialize graph for dataset ", dataset)
            continue

        #save both the ground truth and the graph
        try:

            with open(os.path.join(output_dir, "graphs", dataset+'__ground_truth.json'), "w") as f:
                json.dump( data_mod.get_ground_truth(G).membership, f)

            job_name = dataset + "--groundtruth--0"

            results = {
                'job_name': job_name,
                'elapsed' : 0,
                'membership' : data_mod.get_ground_truth(G).membership,
                'algo' : "groundtruth",
                'dataset' : dataset,
                'iteration' : 0
            }

            #write to json
            with open(os.path.join(output_dir, "json", job_name+".json"), "w") as f:
                json.dump(results, f)


        except Exception as e:
            print("Unable to find Ground Truth partition for ", dataset, ": ", e)


        #keep this out of the loop just in case the operations in it take a long time. The graph context should rarely change
        ctx = create_graph_context(G)

        for algo in algos:

            iterations = 1 if algo not in stochastic_algos else iterations
            for i in range(iterations):
                job_name = dataset+"--"+algo+"--"+str(i)
                map_inputs.append(Worker(job_name, algo, dataset, output_dir, i, timeout, ctx))


    pool = multiprocessing.Pool(processes=workers)
    pool.map_async(run_single, map_inputs)
    pool.close()
    pool.join()


    #NOTE: cannot timeout becaue it blocks. leaving code here just to show that I tried
    #try:
    #    res.get(timeout=timeout)
    #except multiprocessing.context.TimeoutError as e:
    #    print("[IMPORTANT - ", w.job_name, "] Stopping execution due to timeout of ", timeout)

def main():

    DEFAULT_STOCHASTIC_REPETITIONS = 1
    DEFAULT_NUM_WORKERS = 10
    DEFAULT_TIMEOUT=3600

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    data_choices = ['scotus', 'school', 'revolution', 'pgp', 'amazon', 'football', 'flights', 'congress_voting', 'karate', 'malaria', 'nba_schedule', 'netscience']

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('dataset', nargs=1,choices=['ALL']+data_choices,help='dataset name. ALL will use all datasets')
    parser.add_argument('algo', nargs=1,choices=['ALL']+comm_choices, help='Which community detection to run.')
    parser.add_argument('--output', type=str, nargs=1, default=[OUTPUT_DIR], help='Base output directory')
    parser.add_argument('--samples', type=int, default=DEFAULT_STOCHASTIC_REPETITIONS, help='Number of times to run stochastic algos')
    parser.add_argument('--workers', type=int, default=DEFAULT_NUM_WORKERS, help='Number of workers to process')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout applied to algo execution on a dataset')
    args = parser.parse_args()

    algos = comm_choices if 'ALL' in args.algo else args.algo
    datasets = data_choices if 'ALL' in args.dataset else args.dataset

    overall_start_time = datetime.datetime.now()
    run(algos, datasets, args.output[0], args.samples, args.workers, args.timeout)
    overall_end_time = datetime.datetime.now()
    print("Time elapsed:", (overall_end_time - overall_start_time))

if __name__ == "__main__":
    main()
