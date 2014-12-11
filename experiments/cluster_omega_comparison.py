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
import os
import glob


def run_distance_matrix_clustering(fname):
    """
    Take a given input file (output of run_comparison.py which is a distance matrix of the results where Omega score
     is the distance metric) and use spectral clustering to figure out which algorithms are most similar in the results.
     This is done by running spectral clustering for varying number of clusters and seeing how often two algorithms end
      up in the same clsuter

    Args:
        fname: Input csv file. It
    """

    # Read in csv file. Parse header row and keep the rest for processing
    lines = open(fname).read().strip().split('\n')
    headerRow = lines[0].split(',')
    lines = lines[1:]

    # Create a list of lists of the distance matrix
    pyMatrix = []
    size = len(lines)  # Assume square for now
    for line in lines:
        pyMatrix.append([float(val) for val in line.split(',')])  # Assume comma delimited

    # Turn into numpy array
    npMatrix = np.matrix(pyMatrix)

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
    pairs = {}
    print('------------------------------------')
    print("Cluster Results for: ", os.path.basename(fname))
    # Run clustering algorithms for various number of clusters
    for n in range(3, size-1):
        result = spectral_clustering(npMatrix, n_clusters=n)

        # result is a list of
        for i in range(max(result)):
            algorithms = []
            for j, val in enumerate(result):
                if val == i:
                    algorithms.append(headerRow[j])

            if len(algorithms) > 1:
                algorithms.sort()
                for x in range(len(algorithms)):
                    for y in range(x+1,len(algorithms) ):
                        pairName = algorithms[x] + '--' + algorithms[y]
                        if pairName in pairs:
                            pairs[pairName] += 1
                        else:
                            pairs[pairName] = 1

    # Sort on frequency and print
    tuples = []
    for pair in pairs:
        tuples.append((pairs[pair], pair))

    tuples.sort()
    for (count, pair) in tuples:
        # TODO: This should do something better than just printing to the screen
        print(pair, count)


def main():
    parser = argparse.ArgumentParser(description=
                                     'Use Relative Omega Scores to determine similarity of algorithms')
    parser.add_argument('input_path', type=str, help='file or directory containing  metric json files')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return


    if os.path.isdir(args.input_path):
        file_names = glob.glob(os.path.join(args.input_path, '*.csv'))
        for file_name in file_names:
            run_distance_matrix_clustering(file_name)
    else:
        print("Path \"{}\" is not a directory".format(args.input_path))
        return

if __name__ == "__main__":
    main()