## American College Football

The data can be found at <http://www-personal.umich.edu/~mejn/netdata/football.zip>

## Description
Football games played between Division 1A colleges during the regular season.

Directed: No

Weighted: No

Multigraph: Yes

### Vertices 
Each vertex represents a team. 

Attributes:
* **label**: School name
* **id**: Unique identifying integer id
* **value**: Integer value specifying conference.

### Edges
There is an edge between two vertices for each game the teams have played each other. Since a few teams play each other multiple times, this is a multigraph. It can be converted into a weighted graph by calling `download_utils.multigraph_to_weights` from the Circulo package.

Attributes: None

## Other Notes
* See `run.py` for specific details

## Ground Truth
`get_ground_truth` groups the vertices by conference.

## References
Data from Mark Newman's personal website. 

M. Girvan and M. E. J. Newman, *Proc. Natl. Acad. Sci. USA* **99**, 7821-7826 (2002).