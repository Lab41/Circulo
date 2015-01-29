import os
import igraph
import argparse
from operator import itemgetter
import json


def get_community_counts(G, node_ids_to_communities, labels_to_count, count_type="node"):
    count_type = count_type.lower()
    if count_type in ('node', 'vertex'):
        return get_community_counts_by_node(G, node_ids_to_communities, labels_to_count)
    elif count_type == "edge":
        return get_community_counts_by_edge(G, node_ids_to_communities, labels_to_count)
    else:
        raise ValueError('%s is not a valid count type. Must be "node" or "edge"' % count_type)


def get_community_counts_by_node(G, node_ids_to_communities, labels_to_count):
    """
    Using node attributes create an aggregation (by community) of counts for every attribute/attribute value

    """
    # TODO: Consider estimating cardinality of columns before counting
    community_counts = {}  # {community:{label:{label_val:count}}}
    # Iterate through nodes
    for i, node in enumerate(G.vs):
        attributes = node.attributes()
        for community in node_ids_to_communities[i]:
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


def get_community_counts_by_edge(G, node_ids_to_communities, labels_to_count):
    """
    Using edge attributes create an aggregation (by community) of counts for every attribute/attribute value

    """
    # # Build mapping of node id to community
    # node_id_to_community = {}
    # for i, node in enumerate(G.vs):
    #     #attributes = node.attributes()
    #     #community = attributes[algo_name]
    #     node_id_to_community[i] = set(node_ids_to_communities[i])

    # Build up community counts where edge is internal to community
    community_counts = {}  # {community:{label:{label_val:count}}}
    for edge in G.es:
        communities = set(node_ids_to_communities[edge.source]) & set(node_ids_to_communities[edge.target])
        if communities is None:
            # For edges between communities to make totals work
            communities = set(['external'])

        for community in communities:
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


def label_communities(input_file, results_filename, attributes_to_ignore, count_type="both"):
    # TODO: Consider refactoring to split edge vs node code more completely and only merge for display
    G = igraph.load(input_file)

    # Build up node_ids_to_community
    node_ids_to_communities = {}
    results = json.load(open(results_filename))

    community_size = {} # Total size of each community
    for i, communities in enumerate(results['membership']):
        node_ids_to_communities[i] = communities
        for community in communities:
            if community not in community_size:
                community_size[community] = 1
            else:
                community_size[community] += 1


    # iterate through verticies, collect labels we are interested in
    count_type = count_type.lower()
    edge_labels_to_count = []
    node_labels_to_count = []
    print('Labels to Ignore: ', attributes_to_ignore)
    if count_type in ('node', 'vertex', 'both'):
        for graph_key in G.vs[0].attribute_names():
            if not graph_key.startswith('algo') and not graph_key.startswith('id') \
                    and not graph_key.startswith('weight') and graph_key not in attributes_to_ignore:
                node_labels_to_count.append(graph_key)

    if count_type in ('edge', 'both'):
        for graph_key in G.es[0].attribute_names():
            if not graph_key.startswith('algo') and not graph_key.startswith('id') \
                    and not graph_key.startswith('weight') and graph_key not in attributes_to_ignore:
                edge_labels_to_count.append(graph_key)

    print('Attributes: ', edge_labels_to_count + node_labels_to_count)

    print('Getting Node Counts')
    if count_type in ('node', 'vertex', 'both'):
        node_community_counts = get_community_counts(G, node_ids_to_communities, node_labels_to_count, "node")
        node_graph_counts = get_graph_counts(node_community_counts, node_labels_to_count)

    print('Getting Edge Counts')
    if count_type in ('edge', 'both'):
        edge_community_counts = get_community_counts(G, node_ids_to_communities, edge_labels_to_count, "edge")
        edge_graph_counts = get_graph_counts(edge_community_counts, edge_labels_to_count)

    print('Displaying Community Labels')
    for community in sorted(community_size, key=int):
        print('------------------------------------------------')
        print('Displaying Community', community, '[%d Nodes]'%community_size[community])
        if count_type in ('node', 'vertex', 'both'):
            # Figure out if we want to print each label
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
                    #print('%s\t%s: %s of %s Nodes for tf-idf %s' % (
                    print('%s\t%s: %s of %s Nodes [Percent of label in graph: %0.2f]' % (
                        label, max_label_val, max_label_val_count, total_count, tfidf*100))
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
                        print('%s\t%s: %s of %s Edges [Percent of label in graph: %0.2f]' % (
                            label, max_label_val, max_label_val_count, total_count, tfidf*100))


def main():
    parser = argparse.ArgumentParser(description=
                                     'Attempt to label communities based on common attributes')
    parser.add_argument('graphml_file', type=str, help='Graphml file representing graph')
    parser.add_argument('results_file', type=str, help='Results JSON File')
    parser.add_argument('--ignore', type=str, default="",
                        help='Attributes to suppress (comma delimited) i.e. stops,timezone')
    args = parser.parse_args()

    if not os.path.exists(args.graphml_file):
        print("Path \"{}\" does not exist".format(args.graphml_file))
        return

    args.ignore = set(args.ignore.split(','))

    # TODO: Allow labeling by edge or node instead of both?
    label_communities(args.graphml_file, args.results_file, args.ignore, "both")


if __name__ == "__main__":
    main()
