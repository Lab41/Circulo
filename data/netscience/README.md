## Network Science Collaborations

The data can be found at <http://www-personal.umich.edu/~mejn/netdata/netscience.zip>

## Description
Coauthorships of papers in the network science community.

Directed: No

Weighted: No (but can be)

Multigraph: No

### Vertices 
Each vertex represents an author of some paper on network science.

Attributes:
* **label**: The name of the researcher
* **id**: Unique identifier

### Edges
There is an edge between two authors if they are coauthors on a paper.

Attributes:
* **value**: (I think) that the value represents the "importance" of a connection. If there are n authors on a paper, each author adds 1/n to the value of their edge to each other author.

## Ground Truth
Not yet implemented.

## Other Notes
* See `run.py` for specific details

## References
Taken from Mark Newman's personal website.

M. E. J. Newman, *Phys. Rev. E* **74**, 036104 (2006).