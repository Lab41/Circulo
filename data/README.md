## Summary

This directory contains links to various data sets and scrips to extract them into a format [readable by igraph](http://igraph.org/python/doc/tutorial/tutorial.html#igraph-and-the-outside-world). 

Each subdirectory's `run.py` provides the methods `get_graph()` and most provide `get_ground_truth()`. `get_graph` returns an igraph graph of the given data, described in the individual dataset's README. `get_ground_truth` returns a VertexClustering object of what we believe to be ground truth in the given data, again described in the specific README.

Running `python3 run.py` in some subdirectory will populate that directory with a new `data/` directory containing all relevant files, including a file in igraph-readable format.


## Adding a new dataset

To write an etl script for a new dataset, follow these steps. We'll pretend our new dataset is called "friends":

1. Create a new subdirectory with a name describing the new dataset: `mkdir friends`
2. Copy the etl template into the new directory, naming it `run.py`: `cp run_template.py friends/run.py`
2. Copy the README template into the new directory, naming it `README.md`: `cp README_template.md friends/README.md`
4. Implement all functions in `run.py`. If the file is already in igraph readable format, this should only involve changing the constants at the top of the file. Otherwise, you'll have to do the conversion yourself, in `__prepare__`.
5. Add an empty __init__.py to the subdirectory: `echo '' > friends/__init__.py`
5. Fill out the README
6. Add a row to the Progress table in this README.

## Progress
| Dataset | Description | `run.py` implemented? | README written? | Ground Truth implemented?
| ------- | ------------|:---------------------:|:---------------:|:----:|
| citi | New York bike trip histories recorded by [citibike](http://www.citibikenyc.com/system-data) | **No** | **In Progress** | **No** |
| congress_voting | Historical congress voting data | Yes | Yes | Yes |
| federal_contrib | Contribution records to political entities | **In progress** | **No** | **No** |
| flights | Flights data from <http://openflights.org/data.html> | Yes | Yes | Yes |
| football | NCAA D1A games played in the Fall 2000 season | Yes | Yes | Yes |
| karate | Famous data set of Zachary's karate club | Yes | **No** | **No** |
| nba_schedule | Games played in the 2013-2014 NBA season | Yes | **No** | **No** |
| netscience | Graph of collaborators on papers about network science | Yes | **No** | **No** |
| pgp | Interactions in pretty good privacy | Yes | **No** | **No** |
| school | Face-to-face interactions in a primary school | Yes | **No** | **No** |
| twitter | Several datasets taken from twitter | **No** | **No** | **No** |

## Resources
Here are some links with lots of graphs. Most of these sites also point you towards other resources. If you need a graph that we don't provide a script for, these sires are a good place to start looking.

<http://nexus.igraph.org>: igraph's own repository of graphs. Available in several formats.

<https://networkdata.ics.uci.edu/about.php> UC Irvine's repository of graphs. Available in several formats.

<http://www-personal.umich.edu/~mejn/netdata/> Mark Newman's personal collection of graphs. Available in gml.

<http://snap.stanford.edu/data/> Snap's repository of (especially large) datasets. 

<http://mlg.ucd.ie/index.html#software> Interesting datasets curated by University College Dublin.