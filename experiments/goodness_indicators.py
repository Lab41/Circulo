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
from scipy.cluster.vq import kmeans2, whiten



metric_names = [
    "Separability",
    "Conductance",
    "Triangle Participation Ratio",
    "Cohesiveness",
    "Average Out Degree Fraction",
    "Cut Ratio",
    "Density",
    "Expansion",
    "Flake Out Degree Fraction",
        ]

#enables a single legend for all graphs rather
#than a legend for each graph
global_lines = list()


def analyze_metric_file(metrics_path, out_path):
    '''
    Analyzes a given metrics results file

    Args:
        metrics_path: path to metrics file
        out_path: directory where to store the results

    Return:
        array of rates of which metric is the most correlated
    '''

    job_name = os.path.splitext(os.path.basename(metrics_path))[0]

    #read in metrics file
    json_f = open(metrics_path)
    j = json.load(json_f)
    json_f.close()
    metrics = j['metrics']

    #we select nine of the metrics that we wish to test
    l = list(zip(
            metrics[metric_names[0]]['results'],
            metrics[metric_names[1]]['results'],
            metrics[metric_names[2]]['results'],
            metrics[metric_names[3]]['results'],
            metrics[metric_names[4]]['results'],
            metrics[metric_names[5]]['results'],
            metrics[metric_names[6]]['results'],
            metrics[metric_names[7]]['results'],
            metrics[metric_names[8]]['results'],
            ))

    #we are only interested in no more than the top 100 communities
    k = min(100, len(l))

    fig = figure(figsize=(16, 10))
    fig.suptitle('Goodness Metrics Indicators: '+ job_name)

    #iterate over each metric, treating it as the comparator
    #aggregate result is a list of rates
    rates = [run(l, feature_idx, k) for feature_idx in range(len(metric_names))]

    #plot the results
    global global_lines
    fig.legend(global_lines, ('S', 'C', 'tpr', 'Coh', 'ODF', 'CutR', 'Den', 'Exp', 'FODF'), loc='right')
    plt.savefig(os.path.join(out_path, job_name + ".png"), format='png')


    return rates




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




def get_rankings(running_avgs, feature_idx):
    '''
    Args:
        running_avgs: a list of running averages, one for each metric
        feature_idx: the primary metric index

    Returns:
        list of top correlating indices for the feature index
    '''

    totals = np.zeros(len(running_avgs))

    for cross_section in list(zip(*running_avgs)):
        #this will always be the feature
        m = max(cross_section)
        diffs = [m-x for x in cross_section]
        for i, diff in enumerate(diffs):
            totals[i]+=diff

    total_max = max(totals)

    if total_max == 0:
        return totals

    #normalize
    totals = totals / float(max(totals))

    matches = [i for i, v in enumerate(totals) if v < .15 and i != feature_idx]

    #we need to get the corresponding total diff for each match so we can sort them
    l = list(zip(matches, [totals[i] for i in matches]))

    #return the sorted list of top correlated metric for primary metric
    return  [i  for i,_ in  sorted(l, key = itemgetter(1))]




def run(metrics_list, feature_idx, k):
    '''
    Creates graph depicting metrics relative to a single metrics specified by
    the feature_idx

    Args:
        metrics_list: List of lists of metrics
        feature_idx: Index of the metric being tested. Refer to the zipped list in main
        k: max size of num of communities we are examining
        metric_name: name of the metric being tested
    '''

    global global_lines

    x_values = range(k)
    num_features = len(metrics_list[0])

    plt.subplot(331+feature_idx)

    vertical = list()

    #basically iterate through features, plotting each one
    for i in range(num_features):
        s = sorted(metrics_list, key = itemgetter(i), reverse=True)[:k]

        #now get the running average for the main metric
        running_avgs = running_avg([v[feature_idx] for v in s])
        vertical.append(running_avgs)
        #to keep colors consistent, we need to use a global list of 2D lines
        if len(global_lines) < num_features:
            line, = plt.plot(x_values, running_avgs)
            global_lines.append(line)
        else:
            plt.plot(x_values, running_avgs, color=global_lines[i].get_color())

    plt.ylabel(metric_names[feature_idx])
    plt.xlabel("Rank")

    return get_rankings(vertical, feature_idx)


def create_pies(M, num_possible):
    '''
    Plots the pie charts that rank top correlated metrics

    Args:
        M: matrix of number of times a metric was top correlated
            m(i, j) = number of times metric j was top correlated to metric i
        num_possible: number of opportunties to be top ranked (i.e. #datasets)
    '''
    #since we are adding a column, let's make a copy
    M_copy = M.copy()
    new_col = num_possible -  np.sum(M_copy, axis=1)
    new_col =  np.reshape(new_col, (np.shape(M_copy)[0], 1))

    M_copy = np.append(M_copy, new_col, 1)

    fig = figure(figsize=(16, 10))
    fig.suptitle('Indicators',fontsize=20)

    for i in range(len(metric_names)):
        axis =  plt.subplot(331 + i)
        axis.set_title("Primary: " + metric_names[i], bbox={'facecolor':'0.8', 'pad':5})
        names = metric_names + ["None"]

        #add labels to each slice of the pie, but only if it had a ranking value
        labels = [names[idx] for idx, x in enumerate(M_copy[i]) if x > 0]
        slices = [v for v in M_copy[i] if v > 0]
        plt.pie(slices, labels = labels, autopct="%1.1f%%")

    plt.savefig(os.path.join("indicators_results","pie.png"), format='png')



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


    rates_agg = list()

    num_files = 0
    for i, f in enumerate(glob.glob(args.metrics_path+"/*--groundtruth--*.json")):
        results = analyze_metric_file(f, args.out_path)
        rates_agg.append(results)
        num_files+=1

    m = np.zeros((len(metric_names), len(metric_names)), dtype=int)


    for i, dataset in enumerate(rates_agg):
        for f_base_idx, rankings in enumerate(dataset):
            if rankings is None or len(rankings) is 0:
                #no indicator
                pass
            else:
                best_match = rankings[0]
                m[f_base_idx][best_match] +=1

    create_pies(m, num_files)


if __name__ == "__main__":
    main()
