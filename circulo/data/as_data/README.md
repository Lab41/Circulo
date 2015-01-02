## AS Relationship Data

The data can be found at <http://www.caida.org/data/as-relationships/>

## Description
This dataset is taken from the Center for Applied Internet Data Analysis (CAIDA). This dataset assigns labels, either peer or isp, to Autonomous System (AS) Relationships. Understand AS relationships is useful for understanding the structure of the internet and why routing properties are the way they are.

Directed: No 

Weighted: No

Multigraph: No

### Vertices 
Each vertex represents an AS.

Attributes:
* **ASN**: The name of the researcher
* **aut_name**: Name of AS
* **changed**: Date of change to infomartion
* **country**: Country of AS
* **org_name**: Name of organization running AS
* **source**: Registrar (i.e. ARIN) 


### Edges
An edge represents a relationship between two AS.

Attributes:
* **relationship**: 1 if it is a provider/customer link, 0 if it is a peer AS link

## Ground Truth
Currently set to country the AS is in. Registrar might more closely reflect the community structure

## Other Notes
* See `run.py` for specific details

## References
The CAIDA UCSD AS-Relationship - 20141201,
<http://www.caida.org/data/as-relationships/>