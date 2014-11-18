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


Worker = namedtuple('Worker', 'json_path ground_truth_path output_path timeout')

def main():

    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
    parser.add_argument('input_path', type=str, help='file or directory containing results')
    parser.add_argument('ground_truth_path', type=str, help='file or directory containing ground truth')
    parser.add_argument('output_path', type=str, help='output directory to write metric files')
    parser.add_argument('--workers', type=int, default=multiprocessing.cpu_count(), help='Number of workers to process (DEFAULT: number of processors)')
    parser.add_argument('--timeout', type=int, default=3600, help="timeout for a work item in seconds (DEFAULT: 3600)")
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    workers = []

    json_groups = {}
    json_files = glob.glob(os.path.join(args.input_path, '*.json'))
    for json_file in json_files:
        prefix = json_file[:json_file.find('--')]

        if prefix in json_groups:
            json_groups[prefix].append(json_file)
        else:
            json_groups[prefix] = [json_file]

    ground_truth_files = glob.glob(os.path.join(args.ground_truth_path, '*groundtruth.json'))
    for prefix in json_groups:
        ground_truth_file_path = None
        for ground_truth_file in ground_truth_files:
            #print(ground_truth_file, os.path.basename(ground_truth_file), prefix)
            if os.path.basename(ground_truth_file).startswith(os.path.basename(prefix)):
                ground_truth_file_path = ground_truth_file
        workers.append(Worker(json_groups[prefix], ground_truth_file_path, args.output_path, args.timeout))
    # if os.path.isdir(args.input_path):
    #     for f in glob.glob(os.path.join(args.input_path, '*.json')):
    #         workers.append(Worker(f, args.output_path, args.timeout))
    # else:
    #     workers.append(Worker(args.input_path, args.output_path, args.timeout))

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


    data = []

    for json_path in worker.json_path:
        with open(json_path) as f:
            data.append(json.load(f))

    print('Loading Ground truth file: %s'%worker.ground_truth_path)
    if worker.ground_truth_path is not None:
        with open(worker.ground_truth_path) as f:

            ground_truth = json.load(f)
    else:
        ground_truth = None

    if(len(data) == 0):
        print("No data found for ", worker.json_path)
        return

    print("###### Running metrics against " + data[0]['job_name'])
    #load the graph and ground truth in
    #data_mod =  importlib.import_module('circulo.data.'+data[0]['dataset']+'.run')

    # instance = None

    # for name,cls in inspect.getmembers(data_mod):
    #     if inspect.isclass(cls) and issubclass(cls, CirculoData) and name != "CirculoData":
    #         instance = cls(data[0]['dataset'])

    # if instance == None:
    #     print("Unable to find data module for ", data[0]['dataset'])
    #     return

    # G = instance.get_graph()

    # weights = 'weight' if G.is_weighted() else None
    # #some datasets might not have ground truth
    # try:
    #     vc = instance.get_ground_truth(G)
    #     ground_truth_cover = cover_from_membership( vc.membership, G)
    # except Exception as e:
    #     print("\t++NOTE for ", data[0]['dataset'], ": Ground Truth Not Available")
    #     ground_truth_cover = None

    # results_covers = []
    # for i in range(len(data)):
    #     results_covers.append(cover_from_membership(data['membership'], G))

    try:
        # N2 cover
        metrics_matrix = np.zeros((len(data), len(data)))
        for i in range(len(data)-1):
            for j in range(i, len(data)):
                # Diagonal is a comparison against ground truth
                if (i == j):
                    if ground_truth is not None:
                        results = metrics.omega.omega_index(data[i]['membership'], ground_truth['membership'])
                    else:
                        results = 0
                else:
                    #metrics_matrix[i][j] = metrics.omega.omega_index(data[i]['membership'], data[j]['membership'])
                    results = (metrics.omega.omega_index(data[i]['membership'], data[j]['membership']))

                if type(results) == int or type(results) == float or type(results) == np.float64:
                    metrics_matrix[i][j]  = results
                    metrics_matrix[j][i]  = results
                else:
                    print(type(results), results)
                    
                
        
        algorithms = []
        name = None
        for filename in data:
            print(filename['job_name'].split('--'))
            (name, algorithm) = filename['job_name'].split('--')[:2]
            algorithms.append(algorithm)
        print("###### Running metrics against " + name) 
        np.savetxt(os.path.join(worker.output_path, "%s.csv"% name), metrics_matrix, delimiter=",", header=','.join(algorithms))
    except TimeoutError as t:
        print("\t+Timeout ERROR: was analyzing: ", data['job_name'])
        signal.alarm(0)
        return
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        return


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
