## Primary School - Cumulative Networks

The data can be found at <http://www.sociopatterns.org/datasets/primary-school-cumulative-networks/>

## Description
A network of face to face time between people at a primary school.

Directed: No

Weighted: No (but can easily be modified to be weighted)

Multigraph: No

### Vertices 
Each vertex represents a person at the school (either a student or a teacher).

Attributes:
* **classname**: The school class and grade, if a student. Otherwise, "Teachers"
* **label**: Unique identifier.
* **id**: Yet another unique identifier.
* **gender**: M, F, or Unknown
* **viz**: Undocumented. Always 0.0

### Edges
An edge exists where some actor was face to face with another one. 

Attributes:
* **id**: Unique identifier. 
* **count**: The number of times that contact was established during the day.
* **duration**: The total time that the nodes on this edge spent in face to face contact, measured in 20 second intervals.

## Ground Truth
`get_ground_truth` returns a VertexClustering object in which the vertices are grouped by "classname".

## Other Notes
* See `run.py` for specific details
* Either "count" or "duration" would make sense as a weight for use with a weighted algorithm.
* `run.py` requires NetworkX from <https://networkx.github.io>.

## References

Thanks to sociopatterns.org. 
