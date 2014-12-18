# Circulo Datasets 

###Summary
This directory contains the python scripts that download the individual datasets for the Circulo framework.  Each subdirectory represents a single dataset. Each dataset is converted into graphml and stored in the [GRAPHS](circulo/data/GRAPHS) directory by the run.py script. As such, run.py is responsible for downloading and converting raw data into a graphml formatted file.  Each run.py script must contain a class that inherits from the CirculoData class found in the [databot](circulo/data/databot.py) module.  


###How do I add a new dataset?

The key to understanding how to import a dataset into Circulo is to be familiar with the CirculoData class in the [databot](circulo/data/databot.py) module. We'll pretend our new dataset is called "friends".  To import the friends dataset into the Circulo framework, follow these steps:

1. Create a new subdirectory with a name describing the new dataset: `mkdir friends`
2. Create the python file `friends/run.py` and be sure that `run.py` contains a class that inherits from CirculoData. In this case, we will call the class `FriendsData`. 
3. Copy the README template into the new directory, naming it `README.md`: `cp README_template.md friends/README.md`. Be sure to be as thorough as possible when writing the README so that others will understand your dataset.
4. Override the necessary functions from the CirculoData class in the FriendsData class in `run.py`.  Please see other `run.py` files for examples.  The amount of code required in the `run.py` file largely depends on how close the original data is to a graph format. 
5. Add a row to the Dataset Index in this README.

## Dataset Index
| Dataset | Description | Has Ground Truth?
| ------- | ------------|:---------------------:|
| amazon | Co-purchasing Data | Yes |
| house_voting | 2014 congress (house) voting data | Yes |
| flights | Flights data from <http://openflights.org/data.html> | Yes |
| football | NCAA D1A games played in the Fall 2000 season |  Yes |
| karate | Famous data set of Zachary's karate club | Yes |
| malaria | Amino acids in malaria parasite | **No** |
| nba_schedule | Games played in the 2013-2014 NBA season | Yes |
| netscience | Graph of collaborators on papers about network science | **No** |
| pgp | Interactions in pretty good privacy |  **No** |
| revolution |This is a bipartite graph representing colonial American dissidents' membership |**No**|
| school | Face-to-face interactions in a primary school | Yes |
| scotus | Supreme court case citation network | **No** |
| senate_voting | 2014 congress (senate) voting data | Yes |
| southern_women | bipartite graph of southern women social groups | __No__ |

## Resources
Here are some links with lots of graphs. Most of these sites also point you towards other resources. If you need a graph that we don't provide a script for, these sites are a good place to start looking.

<http://nexus.igraph.org>: igraph's own repository of graphs. Available in several formats.

<https://networkdata.ics.uci.edu/about.php> UC Irvine's repository of graphs. Available in several formats.

<http://www-personal.umich.edu/~mejn/netdata/> Mark Newman's personal collection of graphs. Available in gml.

<http://snap.stanford.edu/data/> Snap's repository of (especially large) datasets. 

<http://mlg.ucd.ie/index.html#software> Interesting datasets curated by University College Dublin.
