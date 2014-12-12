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
import os
import glob


def run_distance_matrix_clustering(fname, n=None):
    """
    Take a given input file (output of run_comparison.py which is a distance matrix of the results where Omega score
     is the distance metric) and use spectral clustering to figure out which algorithms are most similar in the results.

    Args:
        fname: Input csv file. It
    """

    # Read in csv file. Parse header row and keep the rest for processing
    f = open(fname)
    # Read header row before passing to loadtxt
    headerRow = f.readline().split(',')
    npMatrix = np.loadtxt(f, delimiter=',')
    size = len(npMatrix)

    # Set diagonals to 1
    for i in range(size):
        npMatrix[i, i] = 1

    # Spectral clustering doesn't like values less than 0.
    # TODO: Does it make sense to set values < 0 to be the abs(value)??? Seems better than just setting it to 0.
    #       Research meaning of an Omega score < 0
    for i in range(size):
        for j in range(size):
            if npMatrix[i, j] < 0:
                npMatrix[i,j] = abs(npMatrix[i,j])

    # Run spectral clustering for various n_clusters and keep track of how often any two algorithms end up in the same cluster
    print('------------------------------------')
    print("Cluster Results for: ", os.path.basename(fname))

    if n is None:
        # Set default value to sqrt(n)/2 if not specified by user
        n = max(3, floor(sqrt(size)/2))

    if n > size:
        raise ValueError('N=%d is greater than the size (%d)'%(n, size))

    print("N=%d"%n)
    results = []
    result = spectral_clustering(npMatrix, n_clusters=n)
    for i in range(max(result)):
        algorithms = []
        # Map clusters to names
        for j, val in enumerate(result):
            if val == i:
                algorithms.append(headerRow[j])
        # Print Clusters
        print(algorithms)
        results.append(algorithms)
    return results

def print_pairwise_counts(results):
    """
    Print pairwise counts across results sets of how often two algorithms appear in the same cluster
    Args:
     results: list of list of clusters
    """
    pairs = {}
    for clusters in results:
        for cluster in clusters:
            if len(cluster) > 1:
                cluster.sort()
            for x in range(len(cluster)):
                for y in range(x+1,len(cluster) ):
                    pairName = cluster[x] + '--' + cluster[y]
                    if pairName in pairs:
                        pairs[pairName] += 1
                    else:
                        pairs[pairName] = 1

    tuples = []
    for pair in pairs:
        tuples.append([pair, pairs[pair]])

    print("Printing Results Across Datasets")
    for (pair, count) in sorted(tuples, key=itemgetter(1)):
        print(pair, count)


def main():
    parser = argparse.ArgumentParser(description=
                                     'Use Relative Omega Scores to determine similarity of algorithms')
    parser.add_argument('input_path', type=str, help='file or directory containing  csv files')
    parser.add_argument('--n', type=int, help='Number of clusters to look for')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return


    if os.path.isdir(args.input_path):
        file_names = glob.glob(os.path.join(args.input_path, '*.csv'))
        results = []
        for file_name in file_names:
            results.append(run_distance_matrix_clustering(file_name, args.n))

        print_pairwise_counts(results)
    else:
        if os.path.isfile(args.input_path):
            run_distance_matrix_clustering(args.input_path, args.n)
        else:
            print("Invalid Path: %s"%args.input_path)
            return

if __name__ == "__main__":
    main()