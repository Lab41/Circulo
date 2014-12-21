import os
import igraph
import argparse


def get_community_counts(G, algo_name, labels_to_count):
    # TODO: Consider estimating cardinality of columns before counting
    community_counts = {}  # {community:{label:{label_val:count}}}
    # Iterate through nodes
    for node in G.vs:
        attributes = node.attributes()
        community = attributes[algo_name]

        # If this our first time seeing community then add
        if community not in community_counts:
            community_counts[community] = {}
            for label in labels_to_count:
                community_counts[community][label] = {}

        # Keep count for each community of the count of each value
        for label in labels_to_count:
            attribute_val = attributes[label]
            if attribute_val in community_counts[community][label]:
                community_counts[community][label][attribute_val] +=1
            else:
                community_counts[community][label][attribute_val] =1
    return community_counts


def get_graph_counts(community_counts, labels_to_count):
    """
    Aggregate community counts across communities

    """
    # Initialize graph counts
    graph_counts = {}
    for label in labels_to_count:
        graph_counts[label] = {}

    # Aggregate counts across graph
    for community in community_counts:
        for label in community_counts[community]:
            for (label_val, label_val_count) in community_counts[community][label].items():

                if label_val in graph_counts[label]:
                    graph_counts[label][label_val] += label_val_count
                else:
                    graph_counts[label][label_val] = label_val_count
    return graph_counts


def label_communities(input_file, algorithm):
    """
    Attempt to label communities in the graph by looking at common attributes
    Attribute frequency is normalized by frequency in the graph
    """
    G = igraph.load(input_file)
    # iterate through verticies, collect labels we are interested in
    graph_keys = G.vs[0].attribute_names()
    labels_to_count = []
    algo_names_possible = set([])
    for graph_key in graph_keys:
        if not graph_key.startswith('algo') and not graph_key.startswith('id'):
            labels_to_count.append(graph_key)

        if graph_key.startswith('algo'):
            algo_names_possible.add(graph_key)
    print(labels_to_count)

    algo_name = 'algo_' + algorithm
    if algo_name not in algo_names_possible:
        raise ValueError('%s not in possible algorithms %s' % (algo_name, str(list(algo_names_possible))))

    # Get Attribute counts by community
    print('Getting Community Counts')
    community_counts = get_community_counts(G, algo_name, labels_to_count)

    print('Getting Graph Counts')
    graph_counts = get_graph_counts(community_counts, labels_to_count)

    print('Displaying Community Labels')
    for community in community_counts:
        print('------------------------------------------------')
        print('Displaying Community', community)
        for label in labels_to_count:
            total_count = 0
            max_label_val_count = -1
            max_label_val = None
            for (label_val, label_val_count) in community_counts[community][label].items():
                if label_val_count > max_label_val_count:
                    max_label_val = label_val
                    max_label_val_count = label_val_count

                total_count += label_val_count

            # TODO: Consider showing for singleton communities?
            if label_val_count > 1:
                tfidf = max_label_val_count/graph_counts[label][max_label_val]
                print('%s %s: %s of %s for tf-idf %s'%(label, max_label_val, max_label_val_count, total_count, tfidf))


def main():
    parser = argparse.ArgumentParser(description=
                                     'Attempt to label communities based on common attributes')
    parser.add_argument('input_path', type=str, help='file or directory containing  graphml files with results')
    parser.add_argument('algorithm', type=str, help='Algorithm desired (i.e. infomap)')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return


    # if os.path.isdir(args.input_path):
    #     file_names = glob.glob(os.path.join(args.input_path, '*%s*.json'%args.dataset))
    #     print(file_names)
    #     files_to_process = []
    #     for file_name in file_names:
    #         if 'info'  in file_name or 'ground' in file_name:
    #             files_to_process.append(file_name)
    #     analyze_metrics(args.dataset, args.output, files_to_process, args.metrics.split(','))
    # else:
    label_communities(args.input_path, args.algorithm)

if __name__ == "__main__":
    main()
