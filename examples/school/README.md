
#Primary School - Cumulative Networks


Run `python do_example.py` to automatically perform all steps outlined below. Note: the example doesn't currently work in all environments -- very finicky about Cairo.
However, the `download` and `prepare` functions should work fine.


###Data Prep

- The data can be found at [http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/](http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/)
- To download and extract the two data sets, do the following:

	`curl -O http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz`
	
	`gunzip sp_data_school_day_*_g.gexf_.gz`

- Finally, to convert the graphs to a format recognized by iGraph, run

	`python parse_school.py sp_data_school_day_*.gexf_`

There should now be two new .graphml files in the working directory.
	
## Exercise

__Requirements__

- NetworkX from https://networkx.github.io
- iGraph from http://igraph.org
- Unfortunately, plotting also requires Cairo from http://cairographics.org, along with its Python bindings. (py2cairo). So far, I've been unsuccessful downloading these bindings on OSX, so this script has to be run on GNU/Linux. You can download Cairo on Ubuntu with `sudo apt-get install libcairo2-dev`


```
import igraph as ig

g = ig.load("sp_data_school_day_1_g.graphml") # whichever file you would like

# Assigning colors to genders for plotting
colorDict = {"M": "blue", "F": "pink", "Unknown": "black"}

for vertex in g.vs:
	# each vertex is labeled as its classname and colored as its gender.
    vertex["label"] = vertex["classname"]
    vertex["color"] = colorDict[vertex["gender"]]


layout = g.layout("fr") # Fruchterman-Reingold layout

# If Cairo is improperly installed, raises TypeError: plotting not available
ig.plot(g, layout=layout) 
```

