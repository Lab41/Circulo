## Interactions within Pretty Good Privacy

The data can be found at <http://deim.urv.cat/~alexandre.arenas/data/xarxes/PGP.zip>

## Description
Users of the Pretty-Good-Privacy algorithm. Only the giant component included.

Directed: No

Weighted: Yes (But all weights are 1, so not really)

Multigraph: No

### Vertices 
Each vertex is a person using the Pretty-Good-Privacy algorithm.

Attributes:
* **x**: x-coordinate for plotting
* **y**: y-coordinate for plotting
* **z**: z-coordinate for plotting
* **id**: Unique identifier

### Edges
Interactions under PGP.

Attributes:
* **weight**: Always 1. Unweighted, for all intents and purposes.

## Ground Truth
Not yet implemented,

## Other Notes
* See `run.py` for specific details

## References
Taken from Alexandre Arenas' personal site.

M. Boguña, R. Pastor-Satorras, A. Diaz-Guilera and A. Arenas, *Physical Review E*, vol. **70**, 056122 (2004).