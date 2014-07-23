import importlib
import igraph 
from circulo import metrics
import omega
import pickle
import argparse



# read in the pickle file
# run metric on community cover in the file
# output metric


def run_omega(data_name,ground_name):
    #data_name = 'data.congress_voting-fastgreedy.pickle' 
    #ground_name = 'data.congress_voting-groundtruth.pickle'

    data = pickle.load(open(data_name,'rb'))
    data_ground = pickle.load(open(ground_name,'rb'))

    if len(data['vc']) < len(data_ground['vc']):
        x = data
        data = data_ground
        data_ground = x
    
    rv = []
    for i in range(len(data_ground['vc'])):
        v_ground = data_ground['vc'][i].membership
        for j in range(i, len(data['vc'])):
            rv += [omega.omega_index(data['vc'][j].membership,v_ground,True)]

    return rv

parser = argparse.ArgumentParser(description='Compare covers of given dataset.')
parser.add_argument('cover_a', type=str, nargs=1, 
                          help='pickle file for first cover')
parser.add_argument('cover_b', nargs=1,
        help='pickle file for second cover.')

args = parser.parse_args()

diff = run_omega(args.cover_a[0],args.cover_b[0])

print(diff)

