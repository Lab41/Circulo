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


import sys
import os
import argparse
import json
from operator import itemgetter
import glob

import numpy as np
from matplotlib.pyplot import *
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description='Experiment of Correlations in Goodness Metrics')
    parser.add_argument('metrics_path', help="path to metrics results")
    parser.add_argument('--out_path', default='indicators_results',  help="path to save results")
    args = parser.parse_args()

    #create output directory if not exists
    if not os.path.exists(args.out_path):
        os.mkdir(args.out_path)


    if not os.path.exists(args.metrics_path) or not os.path.isdir(args.metrics_path):
        print("Error: Metrics path does not exist")
        return



    for i, f in enumerate(glob.glob(args.metrics_path+"/*--groundtruth--*.json")):
        analyze_metric_file(f, args.out_path)



def analyze_metric_file(metrics_file, out_path):
    '''
    Analyzes a given metrics results file

    Args:
        metrics_file: path to metrics file
        out_path: directory where to store the results
    '''

    job_name = os.path.splitext(os.path.basename(metrics_file))[0]

    #read in metrics file
    json_f = open(metrics_file)
    j = json.load(json_f)
    json_f.close()
    metrics = j['metrics']

    l = list(zip(
            metrics['Separability']['results'],
            metrics['Conductance']['results'],
            metrics['Triangle Participation Ratio']['results'],
            metrics['Cohesiveness']['results'],
            metrics['Average Out Degree Fraction']['results'],
            metrics['Cut Ratio']['results'],
            metrics['Density']['results'],
            metrics['Expansion']['results'],
            metrics['Flake Out Degree Fraction']['results'],
            metrics['Fraction over a Median Degree']['results'],
            metrics['Normalized Cut']['results']
            ))

    k = min(100, len(l))

    fig = figure(figsize=(16, 10))
    fig.suptitle('Goodness Metrics Indicators: '+ job_name)

    #we select nine of the metrics that we wish to test
    run(l, 0, k, "Separability")
    run(l, 1, k, "Conductance")
    run(l, 2, k, "TPR")
    run(l, 3, k, "Cohesiveness")
    run(l, 4, k, "Avg ODF")
    run(l, 5, k, "Cut Ratio")
    run(l, 6, k, "Expansion")
    run(l, 7, k, "Normalized Cut")
    lines = run(l, 8, k, "Frac Med Degree")

    fig.legend(lines, ('S', 'C', 'tpr', 'Coh', 'ODF', 'CutR', 'Den', 'Exp', 'FODF', 'FOMD', 'NC'), loc='right')
    plt.savefig(os.path.join(out_path, job_name + ".png"), format='png')


def running_avg(l):
    '''
    Quick hack of a running average function

    Args:
        l: list of numbers to calculate running average on
    Returns:
        list of the running average at each index
    '''

    r = list()

    total_sum = 0.0

    for idx, item  in enumerate(l):
        total_sum += item
        r.append( total_sum/(idx+1.0))

    return r



def run(metrics_list, feature_idx, k, metric_name):
    '''
    Creates graph depicting metrics relative to a single metrics specified by
    the feature_idx

    Args:
        metrics_list: List of lists of metrics
        feature_idx: Index of the metric being tested. Refer to the zipped list in main
        k: max size of num of communities we are examining
        metric_name: name of the metric being tested
    '''

    x_values = range(k)
    num_features = len(metrics_list[0])

    #first sort by separability and truncate
    lines = list()

    plt.subplot(331+feature_idx)

    for i in range(num_features):
        if i == feature_idx:
            #we must truncate to the main feature
            s = sorted(metrics_list, key = itemgetter(feature_idx), reverse=True)[:k]
        else:
            #use the untruncated list here
            s = sorted(metrics_list, key = itemgetter(i), reverse=True)

        line, = plt.plot(x_values, running_avg([v[feature_idx] for v in s]))
        lines.append(line)

    plt.ylabel(metric_name)
    plt.xlabel("Rank, k")

    return lines


if __name__ == "__main__":
    main()
