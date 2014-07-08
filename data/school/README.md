
#Primary School - Cumulative Networks

- If circulo is not installed, be sure to set the PYTHONPATH to the project home directory, otherwise the circulo package will not be found

Run `python do_example.py` to automatically perform all steps outlined below. Note: the example relies on the python plotting framework "Cairo", which sometimes can be difficult to install. For directions on how to install Cairo for python refer to the main README for the Circulo project.


###Data Prep

- The data can be found at [http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/](http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/)
- To download and extract the two data sets, do the following:

	`curl -O http://www.sociopatterns.org/wp-content/uploads/2014/05/sp_data_school_day_[1-2]_g.gexf_.gz`
	
	`gunzip sp_data_school_day_*_g.gexf_.gz`

- Finally, to convert the graphs to a format recognized by iGraph, run

	`python parse_school.py sp_data_school_day_*.gexf_`

There should now be two new .graphml files in the working directory.
	
- NOTE: The Download code does this slightly differently for simplicity

## Exercise

__Requirements__

- NetworkX from https://networkx.github.io
- iGraph from http://igraph.org
- Cairo from http://cairographics.org along with its Python bindings. (py2cairo).

__Code__

- Please refer to do_example.py
- The example illustrates how to visualize the school data using an igraph layout
