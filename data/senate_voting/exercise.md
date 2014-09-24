## Exercise

__Requirements__

- NetworkX Fork from ....
- IPython QtConsole
- Snap from ...



From the iPython QtConsole 

	#inline images
	import matplotlib
	%matplotlib inline  

	import os
	os.environ['SNAPHOME'] = '/path/to/snap'


	#set the inline image size to be larger
 	import matplotlib.pylab as pylab
 	pylab.rcParams['figure.figsize'] = (14.0, 12.0)

	#ETL the congress voting data
	%run parse_congress.py Filter
	
	import networkx as nx
	
	#from the senate dir, read in the senate data (you can do the house data too)
	G = nx.read_graphml('senate/senate.graphml', node_type=int)
	
	#set the layout
	pos = nx.fruchterman_reingold_layout(G, k=2)
	
	#create the labels
	labels=dict((n, d['name'] + ' ' + d['party']) for n,d in G.nodes(data=True) if d.has_key('party'))

	
	nx.draw(G, pos = pos, node_size=60, node_color="red", edge_color="grey", with_labels=True, labels=labels)




