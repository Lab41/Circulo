import networkx as nx
from subprocess import call
import igraph
from igraph import VertexClustering
import os
import sys
import glob
import urllib.request


# from http://openflights.org/data.html

AIRPORTS_URL = 'https://sourceforge.net/p/openflights/code/HEAD/tree/openflights/data/airports.dat?format=raw'
AIRPORTS_FILENAME = 'airports'

# "name" is really airport id, but is called name because igraph automatically
# indexes on name.
AIRPORTS_SCHEMA = {"name": 0, "airport_name": 1, "city": 2, "country": 3, 
                   "IATA/FAA": 4, "ICAO": 5, "latitude": 6, "longitude": 7, 
                   "altitude": 8, "timezone": 9, "DST": 10}

ROUTES_URL = 'https://sourceforge.net/p/openflights/code/HEAD/tree/openflights/data/routes.dat?format=raw'
ROUTES_FILENAME = 'routes'
ROUTES_SCHEMA = {"airline": 0, "airline_id": 1, "source_airport": 2, 
                 "source_id": 3, "dest_airport": 4, "dest_id": 5, 
                 "codeshare": 6, "stops": 7, "equipment": 8}


def __download__(data_dir):
    """
    Downloads the data from AIRPORTS_URL and ROUTES_URL, and saves
    the results in data_dir.
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(AIRPORTS_URL, AIRPORTS_FILENAME, data_dir)
    download_with_notes(ROUTES_URL, ROUTES_FILENAME, data_dir)


def download_with_notes(URL, FILENAME, data_dir):
    """
    Uses urllib to download data from URL. Saves the results in 
    data_dir/FILENAME. Provides basic logging to stdout.
    """
    print("Downloading data from " + URL + ".....")
    try:
        urllib.request.urlretrieve(URL, os.path.join(data_dir, FILENAME + ".dat"))
    except Exception as e:
        print("Data download failed -- make sure the url is still valid, and that urllib is properly installed.\n\n")
        raise(e)
    print("Download complete.")


def __prepare__(data_dir):
    """
    Takes files downloaded by __download__ and converts them into .graphml 
    format. 

    The graph prepared is **directed**, where the vertices are the airports,
    and there is an edge wherever there is a flight from one airport to 
    another. Note that an edge a->b does not imply b->a.
    """
    newFileName = os.path.join(data_dir, ROUTES_FILENAME + ".graphml")
    print("Parsing airport data...")
    # Create G with airports as vertices
    G = initialize_vertices(os.path.join(data_dir, AIRPORTS_FILENAME + ".dat"))
    print("Parsing route data...")
    # Add all edges to G
    initialize_edges(G, os.path.join(data_dir, ROUTES_FILENAME + ".dat"))
    print("Graph successfully created.")
    print("Deleting airports with no flights...")
    # Delete all vertices with degree 0
    delete_empty_airports(G)
    print("Writing to " + newFileName + "...")
    G.write_graphml(newFileName)
    print("Data is now available in " + newFileName)


def initialize_vertices(fileName):
    """
    Reads a file fileName, that is assumed to conform to AIRPORTS_SCHEMA. 
    Returns a directed igraph.Graph where there is a vertex for each
    airport, with vertex attributes described in AIRPORTS_SCHEMA.  
    """
    vertices = {}
    for a in AIRPORTS_SCHEMA:
        vertices[a] = []

    with open(fileName, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            for a in AIRPORTS_SCHEMA:
                attr = line[AIRPORTS_SCHEMA[a]]
                if attr == "\\N":
                    attr = None
                vertices[a].append(attr)
    numVertices = len(vertices[a])
    print("Adding vertices to graph...")
    return igraph.Graph(n=numVertices, directed=True, vertex_attrs=vertices)


def initialize_edges(G, fileName):
    """
    Reads a file fileName, that is assumed to conform to ROUTES_SCHEMA. 
    Adds edges to G such that an edge exists from a to b if there is a
    flight from a to b. 

    Notes: 
        * This creates a multigraph. Routes from different airlines are not
    coalesced.

        * Not all of the routes in routes.dat have records of both airports. 
    These records are skipped.

        * Remember, the graph is directed! Call .as_undirected() to pretend as
    though it's not.
    """
    edges = []
    attrs = {}
    for a in ROUTES_SCHEMA:
        attrs[a] = []

    with open(fileName, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            source_id = line[ROUTES_SCHEMA["source_id"]]
            dest_id = line[ROUTES_SCHEMA["dest_id"]]
            try:
                source = G.vs.find(source_id).index
                dest = G.vs.find(dest_id).index
            except ValueError:
                badRoute = source_id + " ==> " + dest_id
                print("Skipping " + badRoute + " (Insufficient information to create edge.)")
            edges.append((source, dest))
            for a in ROUTES_SCHEMA:
                attr = line[ROUTES_SCHEMA[a]]
                if attr == "\\N":
                    attr = None
                attrs[a].append(attr)
    print("Adding edges to graph...")
    G.add_edges(edges)
    for a in ROUTES_SCHEMA:
        G.es[a] = attrs[a]


def delete_empty_airports(G):
    """
    Given G, deletes all nodes with degree 0.
    """
    toDelete = []
    for v in G.vs:
        if not v.degree():
            toDelete.append(v)
    G.delete_vertices(toDelete)


def get_graph():
    """
    Returns a directed graph of flights, where the vertices are airports
    and the edges are flights. The returned graph is a multigraph, because
    routes from different airlines are not coalesced.

    Note that the "name" attribute is probably not what one would expect. 
    It is implemented this way because igraph indexes on "name," but no other
    attributes, and we often need to find the OpenFlights identifier.

    Each vertex has the following attributes:
        name: Unique OpenFlights identifier for this airport.
        airport_name: Name of airport. May or may not contain the City name.
        city: Main city served by airport.
        country: Country or territory where airport is located.
        IATA/FAA: 3-letter FAA code, for airports located in Country "United 
            States of America".
            3-letter IATA code, for all other airports.
            Blank if not assigned.
        ICAO: 4-letter ICAO code.
            Blank if not assigned.
        latitude: Decimal degrees, usually to six significant digits. Negative
            is South, positive is North.
        longitude: Decimal degrees, usually to six significant digits.
            Negative is West, positive is East.
        altitude: In feet.
        timezone: Hours offset from UTC. Fractional hours are expressed as
            decimals, eg. India is 5.5.
        DST: Daylight savings time. One of E (Europe), A (US/Canada), 
            S (South America), O (Australia), Z (New Zealand), N (None) or 
            U (Unknown).

    Each edge has the following attributes:
        airline: 2-letter (IATA) or 3-letter (ICAO) code of the airline.
        airline_id: Unique OpenFlights identifier for airline.
        source_airport: 3-letter (IATA) or 4-letter (ICAO) code of the source
            airport.
        source_id: Unique OpenFlights identifier for source airport.
            Airport)
        dest_airport: 3-letter (IATA) or 4-letter (ICAO) code of the
            destination airport.
        dest_id: Unique OpenFlights identifier for destination airport.
        codeshare: "Y" if this flight is a codeshare (that is, not operated by
            Airline, but another carrier), empty otherwise.
        stops: Number of stops on this flight ("0" for direct)
        equipment: 3-letter codes for plane type(s) generally used on this
            flight, separated by spaces
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(data_dir, ROUTES_FILENAME + ".graphml")

    if not os.path.exists(graph_path):
        __download__(data_dir)
        __prepare__(data_dir)
    else:
        print(graph_path, "already exists. Using old file.")

    return igraph.load(graph_path)


def get_ground_truth(G=None, attr='country'):
    """
    Ground Truth is hard to define for the flight info. This Ground
    Truth simply clusters the nodes by country. Another possibility 
    would be DST, which is essentially continents, or timezone. Returns a 
    VertexClustering object.
    """
    if G is None:
        G = get_graph()

    # initialize a dict of the form {a: none}
    # where a is an option that appears in g.vs[attr]
    categories = dict.fromkeys(G.vs[attr])

    # Let each key of the dict refer to its own community.
    counter = 0
    for i in categories:
        categories[i] = counter
        counter += 1

    # creates a membership list of vertices of the form 
    # [x_0, x_1, x_2...] where x_i is the number of the 
    # category that vertex i belongs to.
    membership = [categories[v[attr]] for v in G.vs]

    return VertexClustering(G, membership)



def main():
    G = get_graph()
    get_ground_truth(G)

if __name__ == "__main__":
    main()
