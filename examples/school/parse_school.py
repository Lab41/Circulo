import sys
import os
import networkx as nx

def main(gexfFiles):
	"""
	Takes a list of files in .gexf format, and converts each to GraphML.
	"""
	for filename in gexfFiles:
		writeGraphML(filename)

def writeGraphML(filename):
	"""
	Takes a file in .gexf format, and writes a new file in the same directory
	in GraphML format. The name will be the same, but the extension will be
	changed to .graphml
	"""
	G = nx.read_gexf(filename)
	for node in G.node:
		for attrib in G.node[node]:
			if type(G.node[node][attrib]) == dict:
				# graphML doesn't play nice with dictionaries as attributes.
				# this line just deletes positional information.
				G.node[node][attrib] = 0
	newFileName = filename[:filename.rfind('.')] + ".graphml"
	nx.write_graphml(G, newFileName)
	# removes original file
	os.remove(filename)

if __name__ == "__main__":
	main(sys.argv[1:])