# Now cluster the clusters
# from circulo import metrics
# from sklearn import metrics as skmetrics
# import numpy as np
# import pickle
# import argparse
# import os
# import glob
# import json
# from igraph import VertexCover
# import importlib
# import circulo.metrics.cover
import multiprocessing
import time
import signal
import os
import errno
import traceback
# import sys
from collections import namedtuple
# import inspect
# from circulo.data.databot import CirculoData
import glob
import sys
import networkx as nx
import matplotlib.pyplot as plt
from circulo.wrappers import community
from circulo.metrics import omega
import argparse
import os
import json
import datetime
import multiprocessing


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

    ground_truth_files = glob.glob(os.path.join(args.ground_truth_path, '*.graphml'))
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


def __get_least_frequent_community(community_array, community_counts):
    counts = []
    for community in community_array:
        counts.append( (community_counts[community], community))

    counts.sort()

    #print(community_array, counts)
    for i, (count,community) in enumerate(counts):
        #print (i, len(counts), count, counts)
        if count != 1 or i == len(counts):
            #print( "Returning %s for %s"%(community, community_array) )
            return community

def analyze_json(worker):

    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)
    t0 = time.time()


  

    print('Loading raw Graphml file truth file: %s'%worker.ground_truth_path)
    if worker.ground_truth_path is not None:
        G = nx.read_graphml(worker.ground_truth_path)
    else:
        print("ERROR: Not able to load graph")
        return 
        ground_truth = None


    try:
        for json_path in worker.json_path:
            with open(json_path) as f:
                data = json.load(f)
                (name, algorithm) = data['job_name'].split('--')[:2]

                algo_name = 'algo_%s'%algorithm
                # Calculate number of nodes in each community
                community_counts = {}
                for node in data['membership']:
                    for community in node:
                        if community in community_counts:
                            community_counts[community] += 1
                        else:
                            community_counts[community] = 1

                # Add property to graph
                for node in G:
                    # Get cover Array
                    # TODO: Fix this hacky way to turn node id (i.e. n1) into node index
                    try:
                        community_array = data['membership'][int(node[1:])]
                    except IndexError:
                        community_array= []

                    least_frequent_community = __get_least_frequent_community(community_array, community_counts)
                    if least_frequent_community == None:
                        #print('Least Frequent community is null: %s'%community_array)
                        least_frequent_community = -1
                    G.node[node][algo_name] = str(least_frequent_community)
                  

                # for i, node in enumerate(data['membership']):
                #     node_name = "n%d"%i
                #     #print(i, node,node_name, algo_name)
                #     # get least frequent 
                #     G.node[node_name][algo_name] = __get_least_frequent_community(node, community_counts)
            
                

    except TimeoutError as t:
        print("\t+Timeout ERROR: was analyzing: ", data['job_name'])
        signal.alarm(0)
        return
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        return

    #(name, algorithm) = data[0]['job_name'].split('--')[:2]
    graphml_file_output = os.path.join(worker.output_path, "%s.graphml"% name)
    print("Writing Graph: %s"%graphml_file_output )
    nx.write_graphml(G, graphml_file_output)



if __name__ == "__main__":
    main()
