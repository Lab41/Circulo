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

import numpy as np
from sklearn.cluster import spectral_clustering
import argparse
from math import floor, sqrt
from operator import itemgetter
from itertools import combinations
import os
import glob
import json
import operator

from circulo.utils.general import run_comparison

THRESHOLD = .7

def main():
    parser = argparse.ArgumentParser(description= 'Use Relative Omega Scores to determine similarity of algorithms')
    parser.add_argument('results_path', type=str, help='directory containing  algorithm results')
    args = parser.parse_args()

    if not os.path.exists(args.results_path):
        print("Path \"{}\" does not exist".format(args.results_path))
        return

    dataset_groups = {}
    algos = set()

    #sets the list of json files to a Key (dataset name)
    #Allows us to quickly iterate over all result files for each dataset
    #At the same time, we collect the list of algos from the results
    for fname in glob.glob(os.path.join(args.results_path, '*.json')):
        dataset = os.path.basename(fname).split('--')[0]
        algos.add(os.path.basename(fname).split('--')[1])
        if dataset in dataset_groups:
            dataset_groups[dataset].append(fname)
        else:
            dataset_groups[dataset] = [fname]

    #create count dict for all possible pairs of algos (includes groundtruth)
    counts=dict.fromkeys(combinations(sorted([a for a in algos]),2),0)

    #now iterate over each dataset name (there json files) and update the
    #counts accordingly
    for dataset_name, json_files in dataset_groups.items():
        memberships = []
        algo_names = []
        for fjson in json_files:

            algo_names.append(os.path.basename(fjson).split("--")[1])

            with open(fjson) as f:
                memberships.append(json.load(f)['membership'])

        coords = np.argwhere(run_comparison(memberships) > THRESHOLD)

        for v in coords:
            x,y = v.flatten()
            if x != y and algo_names[x] < algo_names[y]:
                counts[(algo_names[x], algo_names[y])]+=1

    sorted_counts = sorted(counts.items(), key=operator.itemgetter(1), reverse=True)

    print("Total Datasets: ", len(dataset_groups))

    for s in sorted_counts:
        print(s)


if __name__ == "__main__":
    main()
