
#Congress Voting Data Analysis


### Data Prep

- The data can be found at [https://www.govtrack.us/developers/data](https://www.govtrack.us/developers/data)
- To download the 2014 votes, you would do the following
	
	`rsync -avz --delete --delete-excluded --exclude **/text-versions/ govtrack.us::govtrackdata/congress/113/votes/2014 .`
- To download the legislator list that matches to the ids
	
	`rsync -avz --delete --delete-excluded --exclude **/text-versions/ govtrack.us::govtrackdata/congress-legislators/legislators-current.csv .`



## Exercise

__Requirements__

- NetworkX Fork from ....
- IPython QtConsole
- Snap from ...



From the iPython QtConsole 

	#inline images
	import matplotlib
	%matplotlib inline  

	#set the inline image size to be larger
 	import matplotlib.pylab as pylab
 	pylab.rcParams['figure.figsize'] = (14.0, 12.0)

	#ETL the congress voting data
	%run parse_congress.py
	
	import networkx as nx
	
	#from the senate dir, read in the senate data (you can do the house data too)
	G = nx.read_graphml('senate/senate.graphml')
	
	#set the layout
	pos = nx.fruchterman_reingold_layout(G, k=2)

	labels=dict((n,d['party']) for n,d in G.nodes(data=True) if d.has_key('party') and d.has_key('party'))

	nx.draw(G, pos = pos, node_size=60, node_color="red", with_labels=True, labels=labels)




