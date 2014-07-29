## [Dataset Name]
The data can be found at http://jhfowler.ucsd.edu/judicial.htm.

## Description
The dataset represents the citation graph of the Supreme Court of the United States from 1762-2001

Directed: True

Weighted: False

Multigraph: False

### Vertices 
Each vertex of the graph represents a case argued before the U.S. Supreme Court. 

Attributes:
    - caseid: Internal ID used for identifying cases.
    - usid: ID of the case in the U.S. Supreme Court archives (volume and case number)
    - parties: Disputing parties in the case (e.g. 'Marbury v. Madison', 'Brown v. Board of Education of Topeka')
    - year: Year the case was argued.

### Edges
Edges represent majority opinion citations of previous cases; they are directed and point from citing case to cited case.

Attributes: none.

## Ground Truth
No ground truth exists for this dataset.

## Other Notes
* See `run.py` for specific details

## References
