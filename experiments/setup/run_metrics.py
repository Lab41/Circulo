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

output_dir = "metrics"

def main():

    DEFAULT_NUM_WORKERS = 5
    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
    parser.add_argument('input_path', type=str, help='file or directory containing results')
    parser.add_argument('--workers', type=int, default=DEFAULT_NUM_WORKERS, help='Number of workers to process')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_q = []

    if os.path.isdir(args.input_path):
        for f in glob.glob(os.path.join(args.input_path, '*.json')):
            file_q.append(f)
    else:
        file_q.append(args.input_path)

    pool = multiprocessing.Pool(processes = args.workers)
    pool.map_async(analyze_json, file_q)
    pool.close()
    pool.join()

class TimeoutError(Exception):
    pass

def __handle_timeout(signum, frame):
    raise TimeoutError(os.strerror(errno.ETIME))

import signal
import os
import errno
import traceback
import sys
TIMEOUT = 3600

def analyze_json(json_path):

    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
    t0 = time.time()


    data = None

    with open(json_path) as f:
        data = json.load(f)

    if(data is None):
        return

    print("###### Running metrics against " + data['job_name'])
    #load the graph and ground truth in
    data_mod =  importlib.import_module('data.'+data['dataset']+'.run')
    G = data_mod.get_graph()

    weights = 'weight' if G.is_weighted() else None

    #some datasets might not have ground truth
    try:
        vc = data_mod.get_ground_truth(G)
        ground_truth_cover = cover_from_membership( vc.membership, G)
    except Exception as e:
        print("\t++NOTE for ", data['dataset'], ": Ground Truth Not Available")
        ground_truth_cover = None

    results_cover = cover_from_membership(data['membership'], G)

    try:
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
        "metrics": results_cover.metrics
        }

    try:
        full_path = os.path.join(output_dir,data['job_name'] + ".json")
        with open(full_path, 'w') as outfile:
            json.dump(out_dict, outfile)
    except Exception as e:
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
