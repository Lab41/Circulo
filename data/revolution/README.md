## Revolutionary War participants
This dataset is drawn from the appendix of David Hackett Fischer's _Paul Revere's Ride_; a CSV version is available within
the repository https://github.com/kjhealy/revere.git. 

## Description
This is a bipartite graph representing colonial American dissidents' membership in seven Whig (anti-British) groups during the
buildup to the American Revolutionary War. 
See http://kieranhealy.org/blog/archives/2013/06/09/using-metadata-to-find-paul-revere/ and http://www.sscnet.ucla.edu/polisci/faculty/chwe/ps269/han.pdf
for some analyses using this data.

For more traditional SNA applications, a one-mode projection of this data will yield a co-attendance network of the 254
examined Revolutionary War figures.

Graph properties:
   - Directed: False
   - Weighted: False
   - Multigraph: False
   - Bipartite: True

### Vertices 
The seven Type 1 nodes represent these seven groups (St. Andrew's Lodge, the Loyal
Nine, the North Caucus, the Long Room Club, the Boston Tea Party, the Boston Committe, and the London Enemies). 
The 254 Type 2 nodes represent colonial Americans (including John Adams, Paul Revere, and Joseph Warren). 

Attributes: None. 

### Edges
Each edge represents membership by a colonial American in a Whig group.

Attributes: None.

## Ground Truth
None provided.

## Other Notes
* See `run.py` for specific details

## References
[1] Fischer, David Hackett. 1994. _Paul Revere’s Ride._ New York: Oxford University Press. 
