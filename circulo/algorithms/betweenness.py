import igraph as ig
import itertools
from collections import Counter
import time


def edge_and_pair_betweenness(G):
	eb = {edge.tuple : 0 for edge in G.es}
	pb = {vertex.index : {uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs}

	for v in G.vs:
		flows, pairFlows = get_flows(G, v.index, eb, pb)



		for flow in flows: # pythonify
			eb[flow] += flows[flow] / 2. # counted twice.

		for pflow in pairFlows:
			for uw in pairFlows[pflow]:
				pb[pflow][uw] += pairFlows[pflow][uw] / 2. # not sure about this one.

	return eb, pb

def get_flows(G, index, eb, pb):
	# don't reinitialize these dicts each time.
	flows = {edge.tuple : 0 for edge in G.es}
	pairFlows = {vertex.index : {uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs}



	#numPaths[index] = 1
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
				# questionable
				gCount = Counter(grandparents)
				gFlowProportion = bfsDict[g]["numPaths"] / totalPaths / float(gCount[g])
				gFlow = gFlowProportion * bfsDict[v]["flow"] # works better with flowProportion, look into this!
				pairFlows[p][order_tuple((v, g))] = gFlow




	# print bfsDict
	# print
	# print flows
	# print
	# print pairFlows
 # 	print
 # 	print
 	return flows, pairFlows

def order_tuple(toOrder):
    if toOrder[0] <= toOrder[1]:
        return toOrder
    return (toOrder[1], toOrder[0])
	
# def parents_and_children(G, bfs):
# 	relatives = {}

# 	for v in G.vs:

# 		neighbors = G.neighbors(v)
# 		parents = [p for p in neighbors if p ]
# 		children = []
# 		relatives[v.index] = (parents, children)




# 	bfs = G.bfs(index)


# def get_layer_bounds(v, bfs):






#tg = ig.Graph.GRG(200, .2)
tg = ig.Graph.Growing_Random(200, 8)
#tg = ig.read("football.gml")
tg = tg.as_undirected()
time1 = time.time()
eb, pb = edge_and_pair_betweenness(tg);
time2 = time.time()
import CONGO
time3 = time.time()
ebC, pbC = CONGO.edge_and_pair_betweenness(tg, tg.vs)
time4 = time.time()


counter = 0
bad = 0
for key, val in pb.items():
    for key1, val1 in val.items():
    	counter += 1
        if abs(pb[key][key1] - pbC[key][key1]) > 1e-10:
        	bad += 1
        	print abs(pb[key][key1] - pbC[key][key1])
        	print key, key1
        	print "FAILED."
print counter, bad, float(bad)/counter
print time2-time1, time4-time3