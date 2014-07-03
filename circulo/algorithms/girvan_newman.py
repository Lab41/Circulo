import igraph as ig
import operator
import sys


def gn(origGraph):
	"""
	Parameters:
		origGraph: a graph in igraph format

	Return value:
		A dendrogram (VertexDendrogram) created by running Girvan-Newman

	Notes: 
		Runs the Girvan-Newman (edge-betweenness) algorithm on the graph provided.
		Iteratively removes the edge with the highest edge-betweenness, then recalculates.
	"""
	
	# initialize a list of removed edges that result in a split of the graph
	splits = []

	G = origGraph.copy() 

	while G.es:

		# Calculate all edge betweennesses
		# TODO: only recalculate on relevant portions
		edge_betweennesses = G.edge_betweenness()

		# returns an the first index if there is a tie at max.
		max_index, _ = max(enumerate(edge_betweennesses), key=operator.itemgetter(1))

		# edge with the max betweenness
		edge = G.es[max_index].tuple

		G.delete_edges(edge)

		if splitGraph(G, edge):

			# edge is a tuple, but we want a list of lists.
			splits += [list(edge)]

	vd = createDendrogram(origGraph, splits)

	# If we don't call this then as_clustering() fails. bugfix in development branch.
	vd.optimal_count 

	return vd


def splitGraph(G, edge):
	""" 
	Parameters:
		G: an igraph graph
		edge: an edge of the form (v1, v2) where v1 and v2 are vertices in G.
	
	Return value:
		A boolean value. True if removing the edge splits the graph.
	
	Notes:
		Checks to see if removing edge from G splits the graph into 2 disjoint
	communities. If so, returns True, otherwise False.
	"""

	return not G.edge_disjoint_paths(source=edge[0], target=edge[1])


def createDendrogram(G, splits):
	"""
	Given a historical list of split edges, creates a dendrogram 
	by calculating the merges. 

	Runs in O(nlgn) (But really, close to O(n).) This is a useful function
	for any divisive algorithm for which splits can be saved more easily
	than merges.
	"""

	# To create a dendrogram, new merges have id of max id + 1
	n = len(splits) + 1
	merges = []

	mergeDict = {}

	while splits:
		# most recent split popped off
		edge = splits.pop()

		# Get the values the dendrogram wants for each vertex by finding
		# where merges have already happened.
		edge = [traverse(vertex, mergeDict) for vertex in edge]

		merges += [edge]

		# Update the dict to reflect a new merge.
		for vertex in edge:
			mergeDict[vertex] = n
		
		n += 1

	return ig.VertexDendrogram(G, merges)


def traverse(vertex, mergeDict):
	"""
	Given a vertex and a dictionaty of merges, returns the id of the cluster
	the vertex belongs to.
	"""
	while vertex in mergeDict:
		vertex = mergeDict[vertex]
	return vertex



if __name__ == "__main__":
	G = ig.load(sys.argv[1])
	gn(G)