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

circulo_data_list = list()

def run_single(worker):

    print("#### Processing: ", worker.job_name)

    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)
    t0 = time.time()

    func = getattr(community, 'comm_'+worker.algo)(worker.ctx, worker.job_name)

    try:
        r = func()
        #this is where we actuall run the algo against the data
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
    with open(os.path.join(worker.out_dir, worker.job_name+'.json'), "w") as f:
        json.dump(results, f)

    #write to a pickle
    #with open(os.path.join(worker.out_dir, "pickle",worker.job_name + '.pickle'), 'wb') as f:
    #    pickle.dump(results, f)

    print("\t[Info - ", worker.job_name,"] Finished in ", results['elapsed'])


import inspect
from circulo.data.databot import CirculoData


def data_fetcher(databot):
    print("[Graph Generation ETL for ", databot.dataset_name, "]")
    databot.get_graph()

def run(algos, dataset_names, output_dir, iterations, workers, timeout):


    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    map_inputs = []

    json_dir = os.path.join(output_dir, "results")
    ground_truth_dir = os.path.join(output_dir,"ground_truth")

    if not os.path.exists(json_dir):
        os.mkdir(json_dir)
        os.mkdir(ground_truth_dir)

    databots = list()

    for dataset in dataset_names:
        #we are going dynamically load instances of each of the CirculoData subclasses
        data_mod = importlib.import_module('circulo.data.'+dataset+'.run')
        for name,cls in inspect.getmembers(data_mod):
            if inspect.isclass(cls) and issubclass(cls, CirculoData) and name != "CirculoData":
                instance = cls(dataset)
                databots.append(instance)


    #run through each databot in parallel to make sure that the graph exists
    pool = multiprocessing.Pool(processes=workers)
    r = pool.map_async(data_fetcher, databots)
    #need the "get" call to be able to retrieve exceptions in the child processes
    r.get()
    pool.close()
    pool.join()

    for databot in databots:

        print("[INFO - Algorithm Execution for -",databot.dataset_name,"]... Initiated")
        G = databot.get_graph()

        #put in a check for disconnected components. Our framework requires that all graph are connected
        if len(G.components(mode=igraph.WEAK)) is not 1:
            print("Error: ", dataset, " is disconnect. Clean data before proceeding")
            continue

        #write out the ground truth if available. NOTE: sometimes ground truth is not available
        try:

            ground_truth_membership =  databot.get_ground_truth(G).membership

            job_name = databot.dataset_name + "--groundtruth"

            results = {
                'job_name': job_name,
                'elapsed' : 0,
                'membership' : ground_truth_membership,
                'algo' : "groundtruth",
                'dataset' : dataset,
                'iteration' : 0
            }

            #write to json
            with open(os.path.join(ground_truth_dir, job_name+".json"), "w") as f:
                json.dump(results, f)


        except Exception as e:
            print("Unable to find Ground Truth partition for ", databot.dataset_name, ": ", e)


        #keep this out of the loop just in case the operations in it take a long time. The graph context should rarely change
        ctx = create_graph_context(G)
        print(ctx)
        for algo in algos:

            iterations = 1 if algo not in stochastic_algos else iterations
            for i in range(iterations):
                job_name = databot.dataset_name+"--"+algo+"--"+str(i)
                map_inputs.append(Worker(job_name, algo, databot.dataset_name, json_dir, i, timeout, ctx))


    pool = multiprocessing.Pool(processes=workers)
    r = pool.map_async(run_single, map_inputs)
    #need the "get" call to be able to retrieve exceptions in the child processes
    r.get()
    pool.close()
    pool.join()


    #NOTE: cannot timeout becaue it blocks. leaving code here just to show that I tried
    #try:
    #    res.get(timeout=timeout)
    #except multiprocessing.context.TimeoutError as e:
    #    print("[IMPORTANT - ", w.job_name, "] Stopping execution due to timeout of ", timeout)

def main():

    DEFAULT_STOCHASTIC_REPETITIONS = 1
    DEFAULT_NUM_WORKERS = multiprocessing.cpu_count()
    DEFAULT_TIMEOUT=3600

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    data_choices = ['amazon', 'flights', 'football', 'house_voting', 'karate', 'malaria', 'nba_schedule', 'netscience', 'pgp', 'revolution', 'school', 'scotus', 'senate_voting', 'southernwomen']

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('dataset', nargs=1,choices=['ALL']+data_choices,help='dataset name. ALL will use all datasets')
    parser.add_argument('algo', nargs=1,choices=['ALL']+comm_choices, help='Which community detection to run.')
    parser.add_argument('--output', type=str, nargs=1, default=[OUTPUT_DIR], help='Base output directory')
    parser.add_argument('--samples', type=int, default=DEFAULT_STOCHASTIC_REPETITIONS, help='Number of times to run stochastic algos')
    parser.add_argument('--workers', type=int, default=DEFAULT_NUM_WORKERS, help='Number of workers to process (DEFAUT: num processors)')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout in seconds applied to algo execution on a dataset (DEFAULT: 3600)')
    args = parser.parse_args()

    #if ALL is specified for either choice, then use the entire respective array
    algos = comm_choices if 'ALL' in args.algo else args.algo
    datasets = data_choices if 'ALL' in args.dataset else args.dataset

    overall_start_time = datetime.datetime.now()
    run(algos, datasets, args.output[0], args.samples, args.workers, args.timeout)
    overall_end_time = datetime.datetime.now()
    print("Time elapsed:", (overall_end_time - overall_start_time))

if __name__ == "__main__":
    main()
