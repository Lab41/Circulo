## NBA Schedule

The data can be found at <https://github.com/davewalk/2013-2014-nba-schedule>

## Description
Games played in the 2013-2014 NBA season.

Directed: No

Weighted: Yes

Multigraph: No

### Vertices 
Each vertex represents a team.

Attributes:
* **id**: Unique identifier.
* **name**: Team name.

### Edges
There is an edge between each team that plays each other, weighted by the number of games played.

Attributes:
* **weight**: Number of games played between the two teams.

## Ground Truth
`get_ground_truth` returns a VertexClustering of teams clustered by the six divisions.

## Other Notes
* See `run.py` for specific details

## References
Thanks to [Dave Walk](https://github.com/davewalk) and ESPN.com