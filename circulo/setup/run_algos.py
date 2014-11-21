#!/usr/bin/env python
#
# Copyright (c) 2014 In-Q-Tel, Inc/Lab41, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
.. module:: run_algos
    :platform: Unix, OS X
    :synopsis: Runs algorithm/data pairs

.. moduleauthor:: Lab41
'''

import importlib
import igraph
import time
from functools import partial
import argparse
import os
import datetime
import multiprocessing
import traceback
import sys
import json
from collections import namedtuple
import shutil
import signal
import os
import errno
import inspect


from circulo.wrappers import community
from circulo.wrappers.community import stochastic_algos
from circulo.data.databot import CirculoData
from circulo.algorithms.overlap import CrispOverlap


#Named tuple used for passing data into the child processes of the multiprocessing pool
Worker = namedtuple('Worker', 'job_name algo databot out_dir iteration timeout graph')

def to_cover(result):
    '''
    Coverts a VertexClustering, VertexDendrogram, or CrispOverlap to a VertexCover. This function
    is necessary since this framework assumes network partitions are in the VertexCover format

    Args:
        result (VertexClustering | VertexDendrogram | CrispOverlap): A partition of some type

    Returns:
        VertexCover.

    Raises:
        Exception if the input is of an unrecognized type
    '''

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

class TimeoutError(Exception):
    pass

def __handle_timeout(signum, frame):
    raise TimeoutError(os.strerror(errno.ETIME))



def run_single(worker):
    '''
    Runs a single algorithm dataset pair from a mulitprocessing pool. The worker contains the
    information needed to do the work.

    Args:
        worker (Worker namedtuple): A namedtuple containing info for doing the algorithm/data execution
    '''
    print("#### Processing: ", worker.job_name)

    #set the timeout to trigger after worker.timeout time
    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)
    t0 = time.time()

    #fetch the algorithm from the community module
    func = getattr(community, 'comm_'+worker.algo)(worker.graph, worker.databot, worker.job_name)

    try:
        #run the algorithm
        algo_result = func()
        #convert the result to a vertex cover (vc)
        vc = to_cover(algo_result)

    except TimeoutError as t:
        print("[ERROR TIMEOUT ",worker.job_name,"] total time: ", time.time() - t0)
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
            'dataset' : worker.databot.dataset_name,
            'iteration' : worker.iteration
            }

    #write results out to json
    with open(os.path.join(worker.out_dir, worker.job_name+'.json'), "w") as f:
        json.dump(results, f)

    print("\t[Info - ", worker.job_name,"] Finished in ", results['elapsed'])




def data_fetcher(databot):
    '''
    This function is intended to run in a multiprocessing pool. Given a databot, it will
    fetch graph for the databot.

    Args:
        databot (CirculoData subclass): The instance containing info for obtaining a graph
    '''

    print("[Graph Generation ETL for ", databot.dataset_name, "]")
    databot.get_graph()




def run(algos, dataset_names, output_dir, iterations, workers, timeout):
    '''
    Runs every algorithm in algos againsts all datasets in dataset_names. The result
    of each algo/data pair execution is saved in a json file within the output_dir

    Args:
        algos (list of strings): list of algorithms names to execute
        dataset_names (list of strings): list of dataset names to execute
        output_dir (string): output path
        iterations (int): number of times to run the algo against the data
        workers (int): number of concurrent processes to use
        timeout (int): timeout in seconds of any given algo/dataset execution

    '''

    #create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    map_inputs = []
    databots = list()

    for dataset in dataset_names:
        #we are going to dynamically load instances of each of the CirculoData subclasses
        data_mod = importlib.import_module('circulo.data.'+dataset+'.run')
        for name,cls in inspect.getmembers(data_mod):
            if inspect.isclass(cls) and issubclass(cls, CirculoData) and name != "CirculoData":
                instance = cls(dataset)
                databots.append(instance)


    #run through each databot in parallel to make sure that the graph exists
    #this allows the first ETL to run in parallel
    pool = multiprocessing.Pool(processes=workers)
    r = pool.map_async(data_fetcher, databots)

    #need the "get" call to be able to retrieve exceptions in the child processes
    r.get()
    pool.close()
    pool.join()

    #now we should have all the data ETL'd
    for databot in databots:

        job_name = databot.dataset_name + "--groundtruth--0"

        print("[INFO - Algorithm Execution for -",databot.dataset_name,"]... Initiated")
        G = databot.get_graph()

        #put in a check for disconnected components. Our framework requires that all graph are connected
        if len(G.components(mode=igraph.WEAK)) is not 1:
            print("Error: ", dataset, " is disconnected. Skipping datset --> ", databot.dataset_name)
            continue

        #write out the ground truth if available. NOTE: sometimes ground truth is not available
        try:

            ground_truth_membership =  databot.get_ground_truth(G).membership

            results = {
                'job_name': job_name,
                'elapsed' : 0,
                'membership' : ground_truth_membership,
                'algo' : "groundtruth",
                'dataset' : databot.dataset_name,
                'iteration' : 0
            }


            #write to json
            with open(os.path.join(output_dir, databot.dataset_name+"--groundtruth--0.json"), "w") as f:
                json.dump(results, f)

        except Exception as e:
            print("Unable to find Ground Truth partition for ", databot.dataset_name, ": ", e)

        #prepare the inputs for the multiprocessing pool
        for algo_name in algos:

            iterations = 1 if algo_name not in stochastic_algos else iterations
            for i in range(iterations):
                job_name = databot.dataset_name+"--"+algo_name+"--"+str(i)
                map_inputs.append(Worker(job_name, algo_name, databot, output_dir, i, timeout, G))


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
    DEFAULT_OUTPUT_DIR = "results"

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    data_choices = ['amazon', 'flights', 'football', 'house_voting', 'karate', 'malaria', 'nba_schedule', 'netscience', 'pgp', 'revolution', 'school', 'scotus', 'senate_voting', 'southernwomen']

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('dataset', nargs=1,choices=['ALL']+data_choices,help='dataset name. ALL will use all datasets')
    parser.add_argument('algo', nargs=1,choices=['ALL']+comm_choices, help='Which community detection to run.')
    parser.add_argument('--output', type=str, nargs=1, default=[DEFAULT_OUTPUT_DIR], help='Base output directory')
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
