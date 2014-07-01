from Queue import PriorityQueue

def CONGO(OG):
	G = OG.copy()
	edgeBetweenness = G.edge_betweenness()
	splitBetweenness = 4



def vertex_betweeenness_from_eb(G, eb):
	components = G.components()
	membership = components.membership
	vbs = []
	for vertex in G.vs:
		numComponents = len(components[membership[vertex.index]])
		incidentEdges = G.incident(vertex)
		vb = .5 * (sum(eb[e] for e in incidentEdges) - (numComponents - 1))
		print vb
		vbs.append(vb)
#	print vbs
	print G.betweenness()
	return vbs
