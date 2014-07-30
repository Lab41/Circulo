## SCOTUS Citation Network
The data can be found at http://jhfowler.ucsd.edu/judicial.htm (see [1])

## Description
The dataset represents the citation graph of the Supreme Court of the United States from 1762-2002, drawn from 534
volumes of the U.S. Reports. 

Graph properties:
    - Directed: True
    - Weighted: False
    - Multigraph: False

### Vertices 
Each vertex of the graph represents a case argued before the U.S. Supreme Court.

Attributes:
    - caseid: Internal ID used for identifying cases by authors of the dataset.
    - usid: ID of the case in the U.S. Supreme Court archives (volume and case number)
    - parties: Disputing parties in the case (e.g. 'Marbury v. Madison', 'Brown v. Board of Education of Topeka')
    - year: Year the case was argued.

### Edges
Edges represent majority opinion citations of previous cases; they are directed and point from citing case to cited case.

Attributes: none.

## Ground Truth
No ground truth exists for this dataset.

## Other Notes
* See `run.py` for specific details.

## References
[1] "The Authority of Supreme Court Precedent." James H. Fowler, Sangick Jeon. _Social Neworks_ 30 (1): 16-30 (January 2008)
[2] "Network Analysis and the Law: Measuring the Legal Importance of Supreme Court Precedents." James H. Fowler, Timothy R. Johnson, James F. Spriggs II, Sangick Jeon, Paul J. Wahlbeck. _Political Analysis,_ 15 (3): 324-346 (July 2007).
