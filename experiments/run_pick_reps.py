import igraph
import argparse
import pickle
from scipy.cluster.hierarchy import average,fcluster

def argmax(array):
    return max(zip(array, range(len(array))))[1]

def pick_representatives(results):
    print('mega clusters!.......')
    if 'metrics.linkage' not in results:
        return
    mega_clusters = fcluster(results['metrics.linkage'],.5)
    results['metrics.mega_clusters'] = mega_clusters
    print(mega_clusters)

    dist_matrix = results['metrics.distance_matrix']
    
    G = igraph.Graph.Adjacency((dist_matrix < 1).tolist(), 'UNDIRECTED')
    G.vs()['vc'] = results['vc.orig']  if 'vc.original' in results else results['vc']
    for e in G.es(): 
        e['weight'] = 1-dist_matrix[e.source, e.target]

    mega_clusters -= 1
    cluster = igraph.VertexClustering(G, mega_clusters.tolist())

    reps = []
    for s in cluster.subgraphs():
        rep_id = argmax(s.strength(weights='weight'))
        reps += [ s.vs()[rep_id]['vc'] ]

    results['vc.orig'] = results['vc']
    results['vc'] = reps


parser = argparse.ArgumentParser(description='Picks representatives from stochastic clustering algorithms.')
parser.add_argument('cover', type=str, nargs=1, help='pickle file for first cover')
args = parser.parse_args()

results = pickle.load(open(args.cover[0], 'rb'))

pick_representatives(results)

# Output results to pickle
output = open(args.cover[0], 'wb')
pickle.dump(results, output)
output.close()
