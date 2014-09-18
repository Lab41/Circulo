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
import importlib
import circulo.metrics.cover


def main():
    parser = argparse.ArgumentParser(description='Compute metrics for given cover.')

    parser.add_argument('input_path', type=str, help='file or directory containing results')
    parser.add_argument('output_path', type=str, default='metrics_output', help='Output directory for metrics')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    if not os.path.exists(args.output_path):
        os.makedirs(args.output_path)

    if os.path.isdir(args.input_path):
        for f in glob.glob(os.path.join(args.input_path, '*.json')):
            analyze_json(f, args.output_path)
    else:
        analyze_json(f, args.output_path)


def analyze_json(json_path, output_path):

    data = None

    with open(json_path) as f:
        data = json.load(f)

    if(data is None):
        return

    #load the graph and ground truth in
    data_mod =  importlib.import_module('data.'+data['dataset']+'.run')
    G = data_mod.get_graph()

    weights = 'weight' if G.is_weighted() else None

    #some datasets might not have ground truth
    try:
        vc = data_mod.get_ground_truth(G)
        ground_truth_cover = cover_from_membership( vc.membership, G)
    except Exception as e:
        print(data['dataset'], " does not have ground truth so unable to produce scoring for that")
        ground_truth_cover = None

    results_cover = cover_from_membership(data['membership'], G)

    print("Running metrics against " + data['job_name'])

    #results are currently stored within the cover object
    results_cover.compute_metrics(weights=weights, ground_truth_cover=ground_truth_cover )

    out_dict = {
        "name" : data['job_name'],
        "elapsed" :data['elapsed'],
        "membership" : data['membership'],
        "metrics": results_cover.metrics
        }

    output_file = data['job_name'] + ".json"

    with open(os.path.join(output_path, output_file), 'w') as outfile:
        json.dump(out_dict, outfile)



def cover_from_membership(membership, G):

    if(membership is None):
        return None

    cluster_dict = {}

    for vertex_id, cluster_id_list in enumerate(membership):
        for cluster_id in cluster_id_list:
            if(cluster_id not in cluster_dict):
                cluster_dict[cluster_id] = []
            cluster_dict[cluster_id].append(vertex_id)

    return VertexCover(G, [v for v in cluster_dict.values()])


if __name__ == "__main__":
    main()
