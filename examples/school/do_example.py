from subprocess import call
import os
import shutil
import igraph as ig

import parse_school


def download():
	"""
	Downloads graphs from http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/
	and saves them in a directory schoolData. If schoolData already exists, it is cleared.
	"""
	if os.path.exists("schoolData"):
		shutil.rmtree("schoolData")
	os.mkdir("schoolData")
	os.chdir("schoolData")
	try:
		call(["curl", "-O", "http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz"])
	except Exception as e:
		print "cURL failed -- check if the site still has the graph data."
		raise(e)
	for filename in os.listdir("."):
		call(["gunzip", filename])

def prepare():
	"""
	Takes each file in .gexf format and converts it into the igraph-readable graphml.
	"""
	for filename in os.listdir("."):
		parse_school.writeGraphML(filename)


def example():
	"""
	Performs the example outlined in the README. Draws the graph of one dataset.
	"""
	g = ig.load("sp_data_school_day_1_g.graphml") # whichever file you would like

	# Assigning colors to genders for plotting
	colorDict = {"M": "blue", "F": "pink", "Unknown": "black"}

	for vertex in g.vs:
		# each vertex is labeled as its classname and colored as its gender.
   		vertex["label"] = vertex["classname"]
    	vertex["color"] = colorDict[vertex["gender"]]


	layout = g.layout("fr") # Fruchterman-Reingold layout

	# If Cairo is improperly installed, raises TypeError: plotting not available
	try:
		ig.plot(g, layout=layout)
	except TypeError as e:
		print "It looks like Cairo isn't properly installed. Refer to the wiki."
		exit(1)


def main():
	download()
	prepare()
	example()


if __name__ == "__main__":
	main()