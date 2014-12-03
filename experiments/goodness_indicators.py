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
            ))


    k = min(100, len(l))

    fig = figure(figsize=(16, 10))
    fig.suptitle('Goodness Metrics Indicators: '+ job_name)

    rates = list()

    #we select nine of the metrics that we wish to test
    for feature_idx in range(len(metric_names)):
        r = run(l, feature_idx, k)
        rates.append(r)



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




def quantify2(running_avgs, feature_idx):

    totals = np.zeros(len(running_avgs))
    comp = list(zip(*running_avgs))

    for a in comp:
        m = max(a)
        r = [m-x for x in a]
        for i, v in enumerate(r):
            totals[i]+=v

    totals_norm = whiten(totals)
    centroid, label = kmeans2(totals_norm, k = 4)

    feature_label = label[feature_idx]

    matches = [i for i, v in enumerate(label) if v == feature_label and i != feature_idx]

    l = list(zip(matches, [x for i, x in enumerate(totals) if i in matches]))

    r = sorted(l, key = itemgetter(1))


    match_names = [i  for i, v in r]
    return match_names



global_lines = None

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

    #first sort by separability and truncate
    lines = list()

    plt.subplot(331+feature_idx)

    vertical = list()

    for i in range(num_features):
        if i == feature_idx:
            #we must truncate to the main feature
            s = sorted(metrics_list, key = itemgetter(feature_idx), reverse=True)[:k]
        else:
            #use the untruncated list here
            s = sorted(metrics_list, key = itemgetter(i), reverse=True)

        running_avgs = running_avg([v[feature_idx] for v in s])
        vertical.append(running_avgs)
        #to keep colors consistent, we need to use a global list of 2D lines
        if global_lines is not None:
            plt.plot(x_values, running_avgs, color=global_lines[i].get_color())
        else:
            line, = plt.plot(x_values, running_avgs)
            lines.append(line)

    if global_lines is None: global_lines = lines

    plt.ylabel(metric_names[feature_idx])
    plt.xlabel("Rank")

    return quantify2(vertical, feature_idx)



from matplotlib.gridspec import GridSpec

def create_pies(m, num_possible):


    new_col = num_possible -  np.sum(m, axis=1)
    new_col =  np.reshape(new_col, (np.shape(m)[0], 1))

    m = np.append(m, new_col, 1)

    fig = figure(figsize=(16, 10))
    fig.suptitle('Indicators',fontsize=20)


    the_grid = GridSpec(3,3)


    print(m[0])

    for i in range(9):
        axis =  plt.subplot(331 + i)
        axis.set_title("Primary: " + metric_names[i], bbox={'facecolor':'0.8', 'pad':5})
        names = metric_names + ["None"]
        labels = [names[idx] if x > 0 else '' for idx, x in enumerate(m[i])]


        plt.pie(m[i], labels = labels)

    plt.savefig(os.path.join("indicators_results","pie.png"), format='png')



    #figure(1, figsize=(6,6))
    #ax = axes([0.1, 0.1, 0.8, 0.8])

    # The slices will be ordered and plotted counter-clockwise.
    #labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'


    #fracs = [15, 30, 45, 10]
    #explode=(0, 0.05, 0, 0)

    #pie(fracs, explode=explode, labels=labels,

    #autopct='%1.1f%%', shadow=True, startangle=90)
    # The default startangle is 0, which would start
    # the Frogs slice on the x-axis.  With startangle=90,
    # everything is rotated counter-clockwise by 90 degrees,
    # so the plotting starts on the positive y-axis.

    #title('Raining Hogs and Dogs', bbox={'facecolor':'0.8', 'pad':5})
    #show()

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
        for f_base_idx, v in enumerate(dataset):
            if v is None or len(v) is 0:
                #no indicator
                pass
            else:
                best_match = v[0]
                m[f_base_idx][best_match] +=1


    create_pies(m, num_files)

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



if __name__ == "__main__":
    main()
