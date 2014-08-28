# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
import numpy as np
import pickle
import argparse
import os
import glob
import json
from igraph import VertexCover

def main():
    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')
    parser.add_argument('path', type=str, nargs=1,
                              help='pickle file or directory containing pickles for first cover')
    parser.add_argument('output_dir', type=str, default=['metrics_output'], nargs=1, help='Output directory for metrics')

    args = parser.parse_args()

    out_dir = args.output_dir[0]

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for path in args.path:

        if not os.path.exists(path):
            print("Path \"{}\" does not exist".format(path))
            continue

        if os.path.isdir(path):
            for f in glob.glob(os.path.join(path,'*.pickle')):
                analyze_pickle(f, out_dir)
        else:
            analyze_pickle(f, out_dir)

import circulo.metrics.cover

def analyze_pickle(pickle_file, output_dir):

    results = pickle.load(open(pickle_file, 'rb'))

    #see if there is a ground truth file available
    repo = os.path.dirname(pickle_file)
    ground_truth = os.path.join(repo, results['dataset']+".ground_truth")

    # Compute cover metrics
    print('Calculating cover metrics... ')
    for cover in results['vc']:
        weights = 'weight' if cover.graph.is_weighted() else None

        ground_truth_cover = None

        if(os.path.exists(ground_truth)):
            with open(ground_truth, "r") as f:
                truth_membership = json.load(f)
                cluster_dict = {}
                for vertex_id, cluster_id_list in enumerate(truth_membership):
                    for cluster_id in cluster_id_list:
                        if(cluster_id not in cluster_dict):
                            cluster_dict[cluster_id] = []
                        cluster_dict[cluster_id].append(vertex_id)

                ground_truth_cover = VertexCover(cover.graph, [v for v in cluster_dict.values()])


        print("Running metrics against " + results['vc_name'])

        #results are currently stored within the cover object
        cover.compute_metrics(weights=weights, ground_truth_cover=ground_truth_cover )

        vc = None

        d = {
            "name" : results['vc_name'],
            "elapsed" :results['elapsed'],
            "membership" : cover.membership,
            "metrics": cover.metrics
            }

        output_file = results['vc_name'] + ".json"

        with open(os.path.join(output_dir, output_file), 'w') as outfile:
            json.dump(d, outfile)



if __name__ == "__main__":
    main()
