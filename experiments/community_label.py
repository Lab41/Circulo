import os
import igraph
import argparse
from operator import itemgetter
import itertools


def get_community_counts(G, algo_name, labels_to_count, count_type="node"):
    count_type = count_type.lower()
    if count_type in ('node', 'vertex'):
        return get_community_counts_by_node(G, algo_name, labels_to_count)
    elif count_type == "edge":
        return get_community_counts_by_edge(G, algo_name, labels_to_count)
    else:
        raise ValueError('%s is not a valid count type. Must be "node" or "edge"' % count_type)


def get_community_counts_by_node(G, algo_name, labels_to_count):
    """
    Using node attributes create an aggregation (by community) of counts for every attribute/attribute value

    """
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
                community_counts[community][label][attribute_val] += 1
            else:
                community_counts[community][label][attribute_val] = 1
    return community_counts


def get_community_counts_by_edge(G, algo_name, labels_to_count):
    """
    Using edge attributes create an aggregation (by community) of counts for every attribute/attribute value

    """
    # Build mapping of node id to community
    node_id_to_community = {}
    for i, node in enumerate(G.vs):
        attributes = node.attributes()
        community = attributes[algo_name]
        node_id_to_community[i] = community

    # Build up community counts where edge is internal to community
    community_counts = {}  # {community:{label:{label_val:count}}}
    for edge in G.es:
        if node_id_to_community[edge.source] == node_id_to_community[edge.target]:
            community = node_id_to_community[edge.source]
        else:
            # For edges between communities to make totals work
            community = 'external'
        # If this our first time seeing community then add
        if community not in community_counts:
            community_counts[community] = {}
            for label in labels_to_count:
                community_counts[community][label] = {}

        attributes = edge.attributes()
        # Keep count for each community of the count of each value
        for label in labels_to_count:
            attribute_val = attributes[label]
            if attribute_val in community_counts[community][label]:
                community_counts[community][label][attribute_val] += 1
            else:
                community_counts[community][label][attribute_val] = 1

    return community_counts


def get_graph_counts(community_counts, labels_to_count):
    """
    Aggregate community counts across communities

    """
    graph_counts = dict.fromkeys(labels_to_count, {})
    # Aggregate counts across graph
    for community in community_counts:
        for label in community_counts[community]:
            for (label_val, label_val_count) in community_counts[community][label].items():

                if label_val in graph_counts[label]:
                    graph_counts[label][label_val] += label_val_count
                else:
                    graph_counts[label][label_val] = label_val_count
    return graph_counts


def label_communities(input_file, algorithm, attributes_to_ignore, count_type="both"):
    # TODO: Consider refactoring to split edge vs node code more completely and only merge for display
    G = igraph.load(input_file)
    # iterate through verticies, collect labels we are interested in

    count_type = count_type.lower()
    edge_labels_to_count = []
    node_labels_to_count = []

    if count_type in ('node', 'vertex', 'both'):
        for graph_key in G.vs[0].attribute_names():
            if not graph_key.startswith('algo') and not graph_key.startswith('id') \
                    and not graph_key.startswith('weight') and graph_key not in attributes_to_ignore:
                node_labels_to_count.append(graph_key)

    if count_type in ('edge', 'both'):
        print(G.es[0].attribute_names())
        for graph_key in G.es[0].attribute_names():
            if not graph_key.startswith('algo') and not graph_key.startswith('id') \
                    and not graph_key.startswith('weight') and graph_key not in attributes_to_ignore:
                edge_labels_to_count.append(graph_key)

    print(edge_labels_to_count + node_labels_to_count)

    # Algo is stored in vertex props and not edge props
    algo_names_possible = set([])
    for graph_key in G.vs[0].attribute_names():
        if graph_key.startswith('algo'):
            algo_names_possible.add(graph_key)

    algo_name = 'algo_' + algorithm
    if algo_name not in algo_names_possible:
        raise ValueError('%s not in possible algorithms %s' % (algo_name, str(list(algo_names_possible))))

    print('Getting Node Counts')
    if count_type in ('node', 'vertex', 'both'):
        node_community_counts = get_community_counts(G, algo_name, node_labels_to_count, "node")
        node_graph_counts = get_graph_counts(node_community_counts, node_labels_to_count)

    print('Getting Edge Counts')
    if count_type in ('edge', 'both'):
        edge_community_counts = get_community_counts(G, algo_name, edge_labels_to_count, "edge")
        edge_graph_counts = get_graph_counts(edge_community_counts, edge_labels_to_count)

    print('Displaying Community Labels')
    for community in sorted(node_community_counts, key=int):
        print('------------------------------------------------')
        print('Displaying Community', community)
        if count_type in ('node', 'vertex', 'both'):
            for label in node_labels_to_count:
                # Get items
                items = node_community_counts[community][label].items()
                # Pull most common item based on count
                (max_label_val, max_label_val_count) = max(items, key=itemgetter(1))
                # Get totals for percentage in community with attribute
                total_count = sum(map(itemgetter(1), items))

                # TODO: Consider showing for singleton communities?
                if max_label_val_count > 1 and max_label_val_count / float(total_count) >= .5:
                    tfidf = max_label_val_count / node_graph_counts[label][max_label_val]
                    print('%s\t%s: %s of %s Nodesfor tf-idf %s' % (
                        label, max_label_val, max_label_val_count, total_count, tfidf))
        if count_type in ('edge', 'both'):
            for label in edge_labels_to_count:
                # Edge counts don't contain all communities since not all communities have internal edges???
                if community in edge_community_counts:
                    # Get items
                    items = edge_community_counts[community][label].items()
                    # Pull most common item based on count
                    (max_label_val, max_label_val_count) = max(items, key=itemgetter(1))
                    # Get totals for percentage in community with attribute
                    total_count = sum(map(itemgetter(1), items))

                    # TODO: Consider showing for singleton communities?
                    if max_label_val_count > 1 and max_label_val_count / float(total_count) >= .5:
                        tfidf = max_label_val_count / edge_graph_counts[label][max_label_val]
                        print('%s\t%s: %s of %s for tf-idf %s' % (
                            label, max_label_val, max_label_val_count, total_count, tfidf))


def main():
    parser = argparse.ArgumentParser(description=
                                     'Attempt to label communities based on common attributes')
    parser.add_argument('input_path', type=str, help='file or directory containing  graphml files with results')
    parser.add_argument('algorithm', type=str, help='Algorithm desired (i.e. infomap)')
    parser.add_argument('--ignore', type=str, default="",
                        help='Attributes to suppress (comma delimited) i.e. stops,timezone')
    args = parser.parse_args()

    if not os.path.exists(args.input_path):
        print("Path \"{}\" does not exist".format(args.input_path))
        return

    args.ignore = set(args.ignore.split(','))

    # TODO: Allow labeling by edge or node instead of both?
    label_communities(args.input_path, args.algorithm, args.ignore, "both")


if __name__ == "__main__":
    main()
