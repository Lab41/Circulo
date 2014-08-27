# Now cluster the clusters
from circulo import metrics
from sklearn import metrics as skmetrics
import numpy as np
import pickle
import argparse
import os
import glob
import json


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
            print("Found File")
            continue



def analyze_pickle(pickle_file, output_dir):

    results = pickle.load(open(pickle_file, 'rb'))

    # Compute cover metrics
    print('Calculating cover metrics... ')
    for cover in results['vc']:
        weights = 'weight' if cover.graph.is_weighted() else None

        print("Running metrics against " + results['vc_name'])

        #results are currently stored within the cover object
        cover.compute_metrics(weights=weights)

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
