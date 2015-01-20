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
import multiprocessing
import time
import signal
import os
import errno
import traceback
from collections import namedtuple
import glob
import sys
import igraph
import matplotlib.pyplot as plt
from circulo.wrappers import community
from circulo.metrics import omega
import argparse
import os
import json
import datetime
import multiprocessing

Worker = namedtuple('Worker', 'json_path raw_graph_path output_path pick_least_frequent pick_most_frequent timeout')


def main():
    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
    parser.add_argument('input_path', type=str, help='file or directory containing results')
    parser.add_argument('raw_graph_path', type=str, help='File or directory graphml files [typically circulo/data/GRAPHS/]')
    parser.add_argument('output_path', type=str, help='output directory to write metric files')
    parser.add_argument('--least', action="store_true", help='If you add this flag only keep least frequent community for a given node is kept (useful for plotting)')
    parser.add_argument('--most', action="store_true", help='If you add this flag only keep most frequent community for a given node is kept (useful for plotting)')
    parser.add_argument('--workers', type=int, default=multiprocessing.cpu_count(), help='Number of workers to process (DEFAULT: number of processors)')
    parser.add_argument('--timeout', type=int, default=3600, help="timeout for a work item in seconds (DEFAULT: 3600)")
    args = parser.parse_args()

    if args.least and args.most:
        print('Cannot select both least and most common community')
        return

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    workers = []
    json_groups = {}
    json_files = glob.glob(os.path.join(args.input_path, '*.json'))
    for json_file in json_files:
        dataset = os.path.basename(json_file).split('--')[0]
        if dataset in json_groups:
            json_groups[dataset].append(json_file)
        else:
            json_groups[dataset] = [json_file]

    raw_graph_files = glob.glob(os.path.join(args.raw_graph_path, '*.graphml'))
    for (dataset, json_files) in json_groups.items():
        raw_graph_file_path = None
        for raw_graph_file in raw_graph_files:
            if os.path.basename(raw_graph_file).startswith(dataset):
                raw_graph_file_path = raw_graph_file
        workers.append(Worker(json_files, raw_graph_file_path, args.output_path, args.least, args.most, args.timeout))

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


def __get_least_frequent_community(community_array, community_counts, reverse):
    counts = []
    for community in community_array:
        counts.append((community_counts[community], community))

    counts.sort()
    if reverse:
        counts.reverse()

    for i, (count,community) in enumerate(counts):
        if count != 1 or i == len(counts)-1:
            return community


def analyze_json(worker):
    """
    Take in a set of json community detection results files and a graphml file representing the raw graph and output a
    graphml file that contains, as attributes, the results of the algorithms

    Args:
    worker: Named tuple of json_path raw_graph_path output_path timeout
    """
    signal.signal(signal.SIGALRM, __handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, worker.timeout)

    print('Loading raw Graphml file truth file: %s'%worker.raw_graph_path)
    if worker.raw_graph_path is not None:
        G = igraph.load(worker.raw_graph_path)
    else:
        print("ERROR: Not able to load graph")
        return

    try:
        for json_path in worker.json_path:
            with open(json_path) as f:
                data = json.load(f)
                (name, algorithm) = data['job_name'].split('--')[:2]

                algo_name = 'algo_%s'%algorithm

                # Only if we are pulling least frequent
                if worker.pick_least_frequent or worker.pick_most_frequent:
                    # Calculate number of nodes in each community
                    community_counts = {}
                    for node in data['membership']:
                        for community in node:
                            if community in community_counts:
                                community_counts[community] += 1
                            else:
                                community_counts[community] = 1

                # Add property to graph
                for node in G.vs():
                    # Get cover Array
                    # TODO: Fix this hacky way to turn node id (i.e. "n1") into node index (i.e. 1)
                    try:
                        community_array = data['membership'][int(node['id'][1:])]
                    except IndexError:
                        community_array= []

                    if worker.pick_least_frequent:
                        least_frequent_community = __get_least_frequent_community(community_array, community_counts, reverse=False)
                        if least_frequent_community is None:
                            least_frequent_community = -1
                        G.vs[node.index][algo_name] = str(least_frequent_community)
                    elif worker.pick_most_frequent:
                        least_frequent_community = __get_least_frequent_community(community_array, community_counts, reverse=True)
                        if least_frequent_community is None:
                            least_frequent_community = -1
                        G.vs[node.index][algo_name] = str(least_frequent_community)
                    else:
                        G.vs[node.index][algo_name] = ','.join([str(x) for x in community_array])

    except TimeoutError as t:
        print("\t+Timeout ERROR: was analyzing: ", data['job_name'])
        signal.alarm(0)
        return
    except Exception as e:
        print(e)
        traceback.print_exc(file=sys.stdout)
        return

    graphml_file_output = os.path.join(worker.output_path, "%s.graphml"% name)
    print("Writing Graph: %s"%graphml_file_output )
    igraph.write(G, graphml_file_output)


if __name__ == "__main__":
    main()