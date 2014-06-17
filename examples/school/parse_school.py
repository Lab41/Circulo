import sys
import networkx as nx

def main(gexfFiles):
	for filename in gexfFiles:
		writeGraphML(filename)

def writeGraphML(filename):
	G = nx.read_gexf(filename)
	for node in G.node:
		for attrib in G.node[node]:
			if type(G.node[node][attrib]) == dict:
				G.node[node][attrib] = 0
	newFileName = filename[:filename.rfind('.')] + ".graphml"
	nx.write_graphml(G, newFileName)

if __name__ == "__main__":
	main(sys.argv[1:])