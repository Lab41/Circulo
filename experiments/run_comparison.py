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
    parser = argparse.ArgumentParser(description='Compute the relative distance of various results from each other.')
    parser.add_argument('input_path', type=str, help='file or directory containing results')
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

    # Group results file by dataset (treat ground truth as just another dataset)
    json_groups = {}
    json_files = glob.glob(os.path.join(args.input_path, '*.json'))
    for json_file in json_files:
        prefix = json_file[:json_file.find('--')]
        if prefix in json_groups:
            json_groups[prefix].append(json_file)
        else:
            json_groups[prefix] = [json_file]

    # Associate ground truth files with the dataset they come from
    for prefix in json_groups:
         workers.append(Worker(json_groups[prefix], args.output_path, args.timeout))

    if args.workers is not None:
        pool = multiprocessing.Pool(processes=args.workers)
    else:
        pool = multiprocessing.Pool()

    # Run processing
    r = pool.map_async(analyze_json, workers)
    r.get() #must call in order to get error from inside the child processes
    pool.close()
    pool.join()

class TimeoutError(Exception):
    pass

def __handle_timeout(signum, frame):
    raise TimeoutError(os.strerror(errno.ETIME))

def analyze_json(worker):
    """
    For a given set of json files (covering a single dataset) compare each results set to every other result set.

    Args:
       worker: named tuple containing <list of json files to process> <output direcotry> timeout

    """
    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)

    data = []
    # Load results sets
    for json_path in worker.json_path:
        with open(json_path) as f:
            data.append(json.load(f))

    if len(data) == 0:
        print("No data found for ", worker.json_path)
        return

    print("###### Running metrics against " + data[0]['job_name'])
    try:
        # Perform comparison of each result to every other results set
        metrics_matrix = np.zeros((len(data), len(data)))
        for i in range(len(data)-1):
            for j in range(i, len(data)):
                # Diagonal is a comparison against ground truth
                if i == j:
                    # Omega score of results compared against itself should be 1
                    results = 1
                else:
                    results = (metrics.omega.omega_index(data[i]['membership'], data[j]['membership']))

                if type(results) == int or type(results) == float or type(results) == np.float64:
                    metrics_matrix[i][j] = results
                    metrics_matrix[j][i] = results
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

if __name__ == "__main__":
    main()
