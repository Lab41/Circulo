## Airline Flight Data: Airport, Airline, and Route Data

The data can be found at <http://openflights.org/data.html>

## Description
Route data between airports.

**Directed**: Yes

**Weighted**: No

**Multigraph**: Default: No, but information is available.

### Vertices 
Each vertex represents some airport for which we have at least one flight record.

Attributes:
* **DST**: Daylight savings time. One of E (Europe), A (US/Canada), S (South America), O (Australia), Z (New Zealand), N (None) or U (Unknown).
* **altitude**: In feet.
* **ICAO**: 4-letter ICAO code. Blank if not assigned.
* **id**: Unique integral identifier. Generally use "name" instead, to reference.
* **name**: Unique OpenFlights identifier for this airport.
* **city**: Main city served by airport. May be spelled differently from airport_name.
* **latitude**: Decimal degrees, usually to six significant digits. Negative is South, positive is North.
* **longitude**: Decimal degrees, usually to six significant digits. Negative is West, positive is East.
* **timezone**: Hours offset from UTC. Fractional hours are expressed as decimals, eg. India is 5.5.
* **IATA/FAA**: 3-letter FAA code, for airports located in Country "United States of America". 3-letter IATA code, for all other airports. Blank if not assigned.
* **country**: Country or territory where airport is located.
* **airport_name**: Name of airport. May or may not contain the city name.


### Edges
There is a directed edge between two nodes wherever there is a flight between those nodes. By "flight," we mean a recurring flight like UA123, not an individual instance of a flight. Different airlines have flights between the same source and destination, so this is a multigraph that can be modified into a weighted graph by calling download_utils.multigraph_to_weights. `get_graph` does this automatically, but the graph is saved as a multigraph.

Attributes (only available in multigraph. Otherwise, the only attribute is "weight"):
* **airline_id**: Unique OpenFlights identifier for this airline.
* **equipment**: 3-letter codes for plane type(s) generally used on this flight, separated by spaces.
* **source_airport**: 3-letter (IATA) or 4-letter (ICAO) code of the source airport.
* **stops**: Number of stops on this flight ("0" for direct)
* **source_id**: Unique OpenFlights identifier for source airport
* **codeshare**: "Y" if this flight is a codeshare (that is, not operated by Airline, but another carrier), empty otherwise.
* **dest_airport**: 3-letter (IATA) or 4-letter (ICAO) code of the destination airport.
* **dest_id**: Unique OpenFlights identifier for destination airport.
* **airline**: 2-letter (IATA) or 3-letter (ICAO) code of the airline.

## Ground Truth
`get_ground_truth` returns a VertexClustering of vertices grouped by some attribute from the vertex attributes supplied by the user. Currently, the ground truth defaults to clustering by country.

## Other Notes
* See `run.py` for specific details

## References
Thanks to OpenFlights.org