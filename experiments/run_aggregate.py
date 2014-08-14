import importlib
import igraph 
import pickle
import argparse
import glob

from circulo import metrics

parser = argparse.ArgumentParser(description='Compare covers of given dataset.')
parser.add_argument('dataset', type=str, nargs=1, 
                          help='dataset name')
parser.add_argument('--output', nargs=1, default='./', help='Base output directory')
args = parser.parse_args()

final = { 'vc': [] }
for alg_file in glob.glob(args.dataset[0] + '-*'):
    res = pickle.load(open(alg_file, 'rb'))
    for (i, vc) in enumerate(res['vc']):
        vc.alg_name = res['vc_name'] + '_' + str(i)
    final['vc'] += res['vc'] 

output = open(args.output[0] + '/' + args.dataset[0] + '.pickle', 'wb')
pickle.dump(final, output)
output.close()
