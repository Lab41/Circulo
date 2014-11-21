import json
import glob
import os
from collections import Counter
import numpy as np
import argparse

from scipy.stats import itemfreq
from scipy.cluster.vq import kmeans2, whiten



#NOTE: sometimes the error "Matrix is not positive definite" occurs with certain combinations of features
#TODO: figure out how to avoid this
metric_list = [
    "Conductance",
    "Cut Ratio",
    "Degree StatisticsBiased Kurtosis",
    "Density",
     "Expansion",
    "Cohesiveness",
    "Flake Out Degree Fraction",
    ]


NUM_DIMENSIONS = len(metric_list)


def run_experiment(metrics_path, dataset_name):

    num_comms = 0

    files_analyzed = 0
    #go through quickly to determine how many communities you have
    for f in glob.glob(metrics_path+"/"+dataset_name+"--*--*.json"):
        json_f = open(f)
        j = json.load(json_f)
        json_f.close()
        num_comms+=len(j['metrics']['Density']['results'])
        files_analyzed+=1

    if(files_analyzed == 0):
        print("No files to analyze")
        return

    print("Files Analyzed: ", files_analyzed)


    print("Running kmeans on ", num_comms, " communities")

    matrix = np.zeros((num_comms, NUM_DIMENSIONS))
    comm_count = 0
    gt_start = -1
    gt_end = -1


    for i, f in enumerate(glob.glob(metrics_path+"/"+dataset_name+"--*--*.json")):

        print(f)
        json_f = open(f)
        j = json.load(json_f)
        json_f.close()
        metrics = j['metrics']

        #get the number of comms for this file
        add_comms = len(metrics['Density']['results']) + comm_count

        if f == metrics_path+"/"+dataset_name+"--groundtruth--0.json":
             gt_start = comm_count
             gt_end = add_comms

        dim_idx=0
        for metric_name in metric_list:

            results = metrics[metric_name]['results']

            try:
                matrix[comm_count:add_comms,dim_idx] = results
            except Exception as e:
                print(result_dict['results'])
                print("Error: ",e)

            dim_idx+=1
            if dim_idx == NUM_DIMENSIONS:
                break

        comm_count=add_comms

    matrix_norm = whiten(matrix)
    centroid, label = kmeans2(matrix_norm, k=3)

    print(label)

    freq = itemfreq(label[gt_start:gt_end])

    m = max(freq, key=lambda y: y[1])

    ratio = float(m[1])/(gt_end-gt_start)

    print("Groundtruth similarity: ", ratio)

    print("Frequency of groundtruth communities as part of centroids")
    print(freq)

    i = gt_start

    print("GroundTruth Centroids range: ", gt_start, "-> ", gt_end)
    while i < gt_end:
        print(label[i])
        i+=1



def main():
    # Parse user input
    parser = argparse.ArgumentParser(description='Experiment clustering community detection results')
    parser.add_argument('metrics_dir', help="path to metrics dir")
    parser.add_argument('dataset', help='dataset name.')
    args = parser.parse_args()

    run_experiment(args.metrics_dir, args.dataset)


if __name__ == "__main__":
    main()

