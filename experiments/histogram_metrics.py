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
import argparse
import os
import glob
import json
import sys
import numpy as np
import matplotlib.pyplot as plt


def analyze_metrics(dataset, output_dir, file_names, metrics_to_evaluate):
    """
        Creates histograms of specific metrics across algorithms

        Args:
           dataset (string): dataset being processed [used for naming output file]
           output_dir (string): output path
           file_names (list of strings): Input metrics json files
           metrics_to_evaluate (list of strings): Metrics to be histogramed
        Return:
            None
    """
    num_files = len(file_names)
    # Load metrics into memory
    metrics = []
    for json_path in file_names:
        with open(json_path) as f:
            metrics.append(json.load(f))

    # Get min/max for each metric across all datasets
    metric_min_max = {}
    for column, metric_to_evaluate in enumerate(metrics_to_evaluate):
        mins = []
        maxes = []
        for i, data in enumerate(metrics):
            mins.append(min(data['metrics'][metric_to_evaluate]['results']))
            maxes.append(max(data['metrics'][metric_to_evaluate]['results']))

        metric_min_max[metric_to_evaluate] = (min(mins), max(maxes))

    # Create Plots
    plt.clf()
    for column, metric_to_evaluate in enumerate(metrics_to_evaluate):
        for i, data in enumerate(metrics):
            (dataset, algorithm, number) = data['name'].split('--')
            print('Processing: ', dataset, algorithm)

            # Create subplot
            ax = plt.subplot(num_files, len(metrics_to_evaluate), i*(len(metrics_to_evaluate)) + 1 + column)
            plt.hist(data['metrics'][metric_to_evaluate]['results'], bins=20, range=metric_min_max[metric_to_evaluate])
            plt.yticks(ax.get_ylim(), fontsize=8)

            # Set algorithm name on left hand side
            if column == 0:
                plt.ylabel(algorithm, rotation='horizontal', fontsize=8)

            # Set metric name on top of coluns
            if i == 0:
                print('Printing Title: ', metric_to_evaluate)
                plt.title(metric_to_evaluate, fontsize=8)

            # Only print x axis ticks at bottom of the columns
            if i != len(metrics)-1:
                plt.xticks(fontsize=0)
            else:
                plt.xticks(rotation='vertical', fontsize=8)

    plt.savefig(os.path.join(output_dir, '%s.png'%dataset))

def main():

    parser = argparse.ArgumentParser(description=
                                     'Create side by side histograms for various metrics across algorithms for a given dataset')
    parser.add_argument('input_path', type=str, help='file or directory containing  metric json files')
    parser.add_argument('dataset', type=str, help='Dataset desired (i.e. football)')
    parser.add_argument('--metrics', type=str,
                        default=','.join(['Separability', 'Cohesiveness', 'Density', 'Triangle Participation Ratio', 'Conductance']),
                        help='Metrics to Compare (comma separated)')
    parser.add_argument('--output', type=str, default=os.getcwd(), help='Base output directory')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return


    if os.path.isdir(args.input_path):
        file_names = glob.glob(os.path.join(args.input_path, '*%s*.json'%args.dataset))
        analyze_metrics(args.dataset, args.output, file_names, args.metrics.split(','))
    else:
        analyze_metrics(args.dataset, args.output, [args.input_path], args.metrics.split(','))

if __name__ == "__main__":
    main()
