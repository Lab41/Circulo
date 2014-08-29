## Davis "Southern Women" dataset

The data can be found at http://nexus.igraph.org/api/dataset_info?id=23&format=html.

## Description
The network given represents a bipartite attendance network of 18 Southern women attending 14 social events in the Deep South, collected by Davis et al. in their
book "Deep South."

Directed: No

Weighted: No

Multigraph: No

### Vertices 
The graph is bipartite. Type 1 vertices represent the 18 women; type 2 vertices represent the 14 social events. 

Attributes:
- name: Name of the woman or event.

### Edges
Edges represent attendance by a woman at an event. 

Attributes: None

## Ground Truth
No ground truth, although a clustering of the women was generated in later paper by Breiger et al.

## Other Notes
* See `run.py` for specific details

## References
- Breiger R. (1974). The duality of persons and groups. Social Forces, 53, 181-190.
- Davis, A et al. (1941). Deep South. Chicago: University of Chicago Press.
