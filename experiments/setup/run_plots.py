import glob
import sys
import networkx as nx
import matplotlib.pyplot as plt
from circulo.wrappers import community
from circulo.metrics import omega
import argparse
import os
import json
import datetime
import multiprocessing

def runGraphs(graphml_path, algos, datasets, cover_path, plot_dir, num_workers):
    print('Checking path: %s'%graphml_path)
    graphml_files_potential = glob.glob(os.path.join(graphml_path, '*.graphml'))
    
    # Only pull out graphs from datasets we are interested in
    graphml_files = []
    for graphml_file in graphml_files_potential:
        for dataset in datasets:
            if dataset in graphml_file:
                graphml_files.append(graphml_file)
    
    print(' Found: %s' %str(graphml_files))

    # Only plot algorithm resuts we are interested in plotting
    inputs = []
    for graphml_file in graphml_files:
        graphml_file_base = os.path.basename(graphml_file)[:-len('.graphml')]
        cover_files = glob.glob(os.path.join(cover_path, '%s*'%graphml_file_base))
        for cover_file in cover_files:
            useData = False
            for algo in algos:
                if algo in cover_file:
                    useData = True
            if useData:
                inputs.append((graphml_file, cover_file, plot_dir))

    # Use multiprocessing to run in parallel
    pool = multiprocessing.Pool(processes=num_workers)
    r = pool.map_async(plotSingleGraph, inputs)
    #need the "get" call to be able to retrieve exceptions in the child processes
    r.get()
    pool.close()
    pool.join()

def plotSingleGraph (input_data):
    (graphml_file, cover_file, plot_dir) = input_data
    print ('Processing file: %s with community file %s'%(graphml_file, cover_file))
    
    # Reading raw graph data
    G = nx.read_graphml(graphml_file)
    label_dict = {}
    for node in G:
        try:
            label_dict[node] = G.node[node]['label']
            
        except KeyError:
            label_dict[node] = ''

    # Read cover
    cover_dict = json.load(open(cover_file))
    
    community_dict = {} # Dictionary of sets
    color_array = []
    for node in G:
        # Get cover Array
        # TODO: Fix this hacky way to turn node id (i.e. n1) into node index
        try:
            community_array = cover_dict['membership'][int(node[1:])]
        except IndexError:
            community_array= []
        
        # Making a dictionary of sets
        community_dict[node] = set(community_array)

        # Add +1 to make 0 a unique group
        if len(community_array)==0:
            color_array.append(0)
        else:    
            color_array.append(community_array[0]+1)

    # # Experiment to determine if changing edge weights makes sense (10x if both nodes are in the same community)
    # weight = 10
    # # iterate through edges
    # for (src,dst, info) in G.edges(data=True): #G.edges_iter():

    #     intersection_size = len(community_dict[src].union(community_dict[dst]) )
    #     #print(intersection_size, src, dst)
    #     if intersection_size > 0:
    #         if 'weight' in info:
    #             original_weight = float(info['weight'])
    #         else:
    #             original_weight = 1.0
    #         G[src][dst]['weight'] = intersection_size*original_weight*weight


    #nx.draw_spring(G, with_labels=True, labels=label_dict, node_color=color_array, font_size=12, alpha=.8)
    nx.draw_spring(G, with_labels=False, labels=label_dict, node_color=color_array, font_size=12, alpha=.8)
    #nx.draw_spectral(G, with_labels=True, labels=label_dict, node_color=color_array, font_size=12, alpha=.8)
    outputPath = os.path.join(plot_dir, '%s.pdf'%os.path.basename(cover_file)[:-len('.json')])
    print('Saving figure %s'%outputPath)
    plt.savefig(outputPath)
    #nx.write_dot(G, '%s.dot'%os.path.basename(cover_file)[:-len('.json')])
    plt.close()


def main():
    OUTPUT_DIR = "outputs"
    DEFAULT_STOCHASTIC_REPETITIONS = 1
    DEFAULT_NUM_WORKERS = multiprocessing.cpu_count()
    DEFAULT_TIMEOUT=3600

    comm_choices = [ a.replace('comm_', '') for a in dir(community) if a.startswith('comm_')]
    data_choices = ['amazon', 'flights', 'football', 'house_voting', 'karate', 'malaria', 'nba_schedule', 'netscience', 'pgp', 'revolution', 'school', 'scotus', 'senate_voting', 'southernwomen']

    # Parse user input
    parser = argparse.ArgumentParser(description='Run community detection on a dataset.')
    parser.add_argument('graphml', help='Location of the graphml files produced by the run_algos.py')
    parser.add_argument('dataset', nargs=1,choices=['ALL']+data_choices,help='Which datasets to plot')
    parser.add_argument('algo', nargs=1,choices=['ALL']+comm_choices, help='Which community detection algo results to plot.')
    parser.add_argument('--results', type=str, default=OUTPUT_DIR, help='Directory containing JSON results of community detection')
    parser.add_argument('--output', type=str, default=OUTPUT_DIR, help='Output Directory for plots')
    parser.add_argument('--workers', type=int, default=DEFAULT_NUM_WORKERS, help='Number of workers to process (DEFAUT: num processors[%d])'%DEFAULT_NUM_WORKERS)
    args = parser.parse_args()

    # Create output directory if it does not exists
    if not os.path.isdir(args.output):
        os.mkdir(args.output)
    #if ALL is specified for either choice, then use the entire respective array
    algos = comm_choices if 'ALL' in args.algo else args.algo
    datasets = data_choices if 'ALL' in args.dataset else args.dataset

    overall_start_time = datetime.datetime.now()
    #run(args.graphml, datasets, args.output[0], args.samples, args.workers, args.timeout)
    #runGraphs(graphml_path, cover_path)
    runGraphs(args.graphml, algos, datasets, args.results, args.output, args.workers)
    overall_end_time = datetime.datetime.now()
    print("Time elapsed:", (overall_end_time - overall_start_time))


if __name__ == "__main__":
    main()