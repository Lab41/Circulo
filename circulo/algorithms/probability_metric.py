def probability_metric(G, membershipList, n):
	pass



def p_in_after_n(G, v, n, comm):
	# memoize with already seen vertices
	if v not in comm:
		return 0

	neighbors = set(G.neighbors(v))
	numNeighbors = float(len(neighbors))
	if n == 1:
		# how many neighbors in community
		return len(neighbors & comm) / numNeighbors
	
	totalP = 0.

	for neighbor in neighbors:
		totalP += 1/numNeighbors * p_in_after_n(G, neighbor, n-1, comm)
	return totalP


def test():
	import igraph as ig
	g = ig.load("football.gml")
	clust = g.community_edge_betweenness().as_clustering()
	results = [[p_in_after_n(g, x, 3, set(cl)) for x in cl] for i, cl in enumerate(clust)]
	print results

