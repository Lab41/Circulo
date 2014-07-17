import importlib
from igraph import plot

'''
Senate Split Example using Plotting

This example shows the potential of the igraph layouts. Rather than using an explicit
community detection algorithm, this example shows how a force-directed layout can be
effective for visualizing communities in a graph.
'''

#the percentage that the two senators vote together. We filter edges based on this value
PERCENT_PAIR_VOTE = .6

#get the graph from the data holding
G = importlib.import_module("data.congress_voting.run").get_graph()

#delete edges less than the threshold of 60%
G.delete_edges(G.es.select(weight_lt=(PERCENT_PAIR_VOTE * max(G.es['weight']))))

#color dictionary for coloring vertices based on party affiliation
color_dict = {"Democrat": "#E0FFFF", "Republican": "#F08080", "Independent":"purple"}

#use a community detection layout
layout = G.layout_fruchterman_reingold(weights="weight")

#plot the graph
plot(G, layout = layout,
        vertex_label = G.vs["full_name"],
        vertex_color = [color_dict[party] for party in G.vs["party"]],
        edge_color = "#DCDCDC",
        bbox = (1400, 1000),
        margin = 20
        )
