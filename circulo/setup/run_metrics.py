# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
import numpy as np
import pickle
import argparse
import os
import glob
import json
from igraph import VertexCover
import importlib
import circulo.metrics.cover
import multiprocessing
import time
import signal
import os
import errno
import traceback
import sys
from collections import namedtuple
import inspect
from circulo.data.databot import CirculoData


Worker = namedtuple('Worker', 'json_path output_path timeout')

def main():

    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
    parser.add_argument('input_path', type=str, help='file or directory containing results')
    parser.add_argument('output_path', type=str, help='output directory to write metric files')
    parser.add_argument('--workers', type=int, default=None, help='Number of workers to process (DEFAULT: number of processors)')
    parser.add_argument('--timeout', type=int, default=3600, help="timeout for a work item in seconds (DEFAULT: 3600)")
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    workers = []

    if os.path.isdir(args.input_path):
        for f in glob.glob(os.path.join(args.input_path, '*.json')):
            workers.append(Worker(f, args.output_path, args.timeout))
    else:
        workers.append(Worker(args.input_path, args.output_path, args.timeout))

    if args.workers is not None:
        pool = multiprocessing.Pool(processes = args.workers)
    else:
        pool = multiprocessing.Pool()

    r = pool.map_async(analyze_json, workers)
    r.get() #must call in order to get error from inside the child processes
    pool.close()
    pool.join()

class TimeoutError(Exception):
    pass

def __handle_timeout(signum, frame):
    raise TimeoutError(os.strerror(errno.ETIME))


def analyze_json(worker):

    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)
    t0 = time.time()


    data = None

    with open(worker.json_path) as f:
        data = json.load(f)

    if(data is None):
        print("No data found for ", worker.json_path)
        return

    print("###### Running metrics against " + data['job_name'])
    #load the graph and ground truth in
    data_mod =  importlib.import_module('circulo.data.'+data['dataset']+'.run')

    instance = None

    for name,cls in inspect.getmembers(data_mod):
        if inspect.isclass(cls) and issubclass(cls, CirculoData) and name != "CirculoData":
            instance = cls(data['dataset'])

    if instance == None:
        print("Unable to find data module for ", data['dataset'])
        return

    G = instance.get_graph()

    weights = 'weight' if G.is_weighted() else None
    #some datasets might not have ground truth
    try:
        vc = instance.get_ground_truth(G)
        ground_truth_cover = cover_from_membership( vc.membership, G)
    except Exception as e:
        print("\t++NOTE for ", data['dataset'], ": Ground Truth Not Available")
        ground_truth_cover = None

    results_cover = cover_from_membership(data['membership'], G)

    try:
        t0 = time.time()
        #results are currently stored within the cover object
        results_cover.compute_metrics(weights=weights, ground_truth_cover=ground_truth_cover )
    except TimeoutError as t:
        print("\t+Timeout ERROR: was analyzing: ", data['job_name'])
        signal.alarm(0)
        return
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        return
    out_dict = {
        "name" : data['job_name'],
        "elapsed" :data['elapsed'],
        "membership" : data['membership'],
        "omega": results_cover.compare_omega(ground_truth_cover),
        "metrics": results_cover.metrics,
        "metrics_elapsed": (time.time() - t0)
        }


    try:

        full_path = os.path.join(worker.output_path,data['job_name'] + ".json")
        with open(full_path, 'w') as outfile:
            json.dump(out_dict, outfile)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        print(e)

def cover_from_membership(membership, G):

    if(membership is None):
        return None

    cluster_dict = {}

    for vertex_id, cluster_id_list in enumerate(membership):
        for cluster_id in cluster_id_list:
            if(cluster_id not in cluster_dict):
                cluster_dict[cluster_id] = []
            cluster_dict[cluster_id].append(vertex_id)

    return VertexCover(G, [v for v in cluster_dict.values()])


if __name__ == "__main__":
    main()
