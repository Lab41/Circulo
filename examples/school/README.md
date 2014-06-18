
#Primary School - Cumulative Networks



###Data Prep

- The data can be found at [http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/](http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/)
- To download and extract the two data sets, do the following:

	`curl -O http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz`
	
	`gunzip sp_data_school_day_*_g.gexf_.gz`

- Finally, to convert the graphs to a format recognized by iGraph, run

	`python parse_school.py sp_data_school_day_*.gexf_`

-- There should now be two new .graphml files in the working directory.
	
## Exercise

__Requirements__

- NetworkX from https://networkx.github.io
- iGraph from http://igraph.org



To c

```
import igraph as ig

G = ig.Graph()

G.Read_GraphML(...) #whichever file you would like 


```

