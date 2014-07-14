import igraph as ig
import itertools
from collections import Counter


def edge_and_pair_betweenness(G):
	"""
	An attempt to find the edge and pair betweennesses without finding all 
	shortest paths, using flows. Currently unused.
	"""
	eb = {edge.tuple : 0 for edge in G.es}
	pb = {vertex.index : {uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs}
	for v in G.vs:
		flows, pairFlows = get_flows(G, v.index, eb, pb)
		for flow in flows: # pythonify
			eb[flow] += flows[flow] / 2. # counted twice.
		for pflow in pairFlows:
			for uw in pairFlows[pflow]:
				pb[pflow][uw] += pairFlows[pflow][uw] / 2. 
	return eb, pb


def get_flows(G, index, eb, pb):
	"""
	Initializing the edge and pair betweenness dicts using flows.
	Edge betweenness correct, but pair betweenness needs work. 
	This can be used as a template for future work concerning flows.
	"""
	# don't reinitialize these dicts each time.
	flows = {edge.tuple : 0 for edge in G.es}
	pairFlows = {vertex.index : {uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs}
	bfs = G.bfsiter(index, advanced=True)
	bfsList = [bfs.next()[0].index]
	# skipping root, manually adding it
	bfsDict = {index : {"depth" : 0, "parents" : [], "numPaths": 1, "flow": 1}}
	nodesSeen = set([index])
	# initializing bfs dict (decompose)
	for v, depth, parent in bfs:
		i = v.index
		bfsList.append(i) # probably don't need
		parents = [p for p in G.neighbors(v) if p in nodesSeen and bfsDict[p]["depth"] < depth]
		nodesSeen.add(i)
		numPaths = sum(bfsDict[p]["numPaths"] for p in parents)
		bfsDict[i] = {"depth": depth, "parents": parents, "numPaths": numPaths, "flow": 1}

	# getting flows (decompose)
	for v in reversed(bfsList):
		# getting edge flows
		parents = bfsDict[v]["parents"]
		totalPaths = float(sum(bfsDict[p]["numPaths"] for p in parents))
		for p in parents:
			flowProportion = bfsDict[p]["numPaths"] / totalPaths
			flow = flowProportion * bfsDict[v]["flow"]
			flows[order_tuple((v, p))] = flow
			bfsDict[p]["flow"] += flow
			grandparents = bfsDict[p]["parents"]
			totalGrandparentPaths = float(sum(bfsDict[g]["numPaths"] for g in set(grandparents)))
			for g in grandparents:
				gCount = Counter(grandparents)
				gFlowProportion = bfsDict[g]["numPaths"] / totalPaths / float(gCount[g])
				gFlow = gFlowProportion * bfsDict[v]["flow"]
				pairFlows[p][order_tuple((v, g))] = gFlow