#!/usr/bin/env python
#
# Copyright (c) 2014 In-Q-Tel, Inc/Lab41, All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import igraph
from igraph import VertexCover
import os
import sys
import urllib.request
from collections import defaultdict
from circulo.utils.general import get_largest_component
from circulo.data.databot import *

# Data from from http://openflights.org/data.html
AIRPORTS_URL = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat'

FLIGHTS_DATA = "flights.csv"
ROUTES_DATA = "routes.csv"

# "name" is really airport id, but is called name because igraph automatically
# indexes on name.
AIRPORTS_SCHEMA = {"name": 0, "airport_name": 1, "city": 2, "country": 3,
                   "IATA/FAA": 4, "ICAO": 5, "latitude": 6, "longitude": 7,
                   "altitude": 8, "timezone": 9, "DST": 10}

ROUTES_URL = 'https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat'
ROUTES_SCHEMA = {"airline": 0, "airline_id": 1, "source_airport": 2,
                 "source_id": 3, "dest_airport": 4, "dest_id": 5,
                 "codeshare": 6, "stops": 7, "equipment": 8}


class FlightData(CirculoData):
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
    def __download__(self):

        self.download_with_notes(AIRPORTS_URL, progressbar=False, download_file = "flights.csv")
        self.download_with_notes(ROUTES_URL, progressbar=False, download_file = "routes.csv")

    def __prepare__(self):
        """
        Takes files downloaded by __download__ and converts them into .graphml
        format.

        The graph prepared is **directed**, where the vertices are the airports,
        and there is an edge wherever there is a flight from one airport to
        another. Note that an edge a->b does not imply b->a.
        """

        # Create G with airports as vertices
        G = FlightData.initialize_vertices(os.path.join(self.raw_data_path, FLIGHTS_DATA))

        # Add all edges to G
        FlightData.initialize_edges(G, os.path.join(self.raw_data_path, ROUTES_DATA))

        # Delete all vertices with degree 0
        G.delete_vertices(G.vs.select(_degree = 0))

        #make sure that the graph is not disconnected. if so take larger component
        components = G.components(mode=igraph.WEAK)
        if len(components) > 1:
            G = G.subgraph(max(components, key=len))

        G.write_graphml(self.graph_path)


    def initialize_vertices(flights_file):
        """
        Reads file "flights_file" that is assumed to conform to AIRPORTS_SCHEMA.
        Returns a directed igraph.Graph where there is a vertex for each
        airport, with vertex attributes described in AIRPORTS_SCHEMA.
        """

        vertex_attrs = defaultdict(list)
        vertex_count = 0
        with open(flights_file, 'r') as f:
            for line in f:
                vertex_count+=1
                line = line.strip().split(',')
                for a in AIRPORTS_SCHEMA:
                    attr = line[AIRPORTS_SCHEMA[a]]
                    if attr == "\\N":
                        attr = None
                    vertex_attrs[a].append(attr)

        return igraph.Graph(n=vertex_count, directed=True, vertex_attrs=vertex_attrs)


    def initialize_edges(G, routes_file):
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

        attrs = defaultdict(list)

        with open(routes_file, 'r') as f:
            for line in f:
                line = line.strip().split(',')
                source_id = line[ROUTES_SCHEMA["source_id"]]
                dest_id = line[ROUTES_SCHEMA["dest_id"]]
                try:
                    source = G.vs.find(source_id).index
                    dest = G.vs.find(dest_id).index
                    edges.append((source, dest))
                except ValueError:
                    badRoute = source_id + " ==> " + dest_id
                    #UNCOMMENT FOR DEBUG INFO
                    #print("Skipping " + badRoute + " (Insufficient information to create edge.)")

                for a in ROUTES_SCHEMA:
                    attr = line[ROUTES_SCHEMA[a]]
                    if attr == "\\N":
                        attr = None
                    attrs[a].append(attr)

        G.add_edges(edges)

        for a in ROUTES_SCHEMA:
            G.es[a] = attrs[a]

    def get_context(self):
        """
        Specify which node attributes should be used in algorithms that take into account node attributes
        """
        return {
            CirculoData.CONTEXT_ATTRS_TO_USE:set(['country'])
        }

    def get_ground_truth(self, G):
        """
        This Ground Truth is the country of the airport
        """

        if G is None:
            return

        cluster_dict = defaultdict(list)

        for airport_id, airport_location in enumerate(G.vs['country']):
            cluster_dict[airport_location].append(airport_id)

        return VertexCover(G, [v for v in cluster_dict.values()]
)

def main():
    databot = FlightData("flights")
    databot.get_ground_truth()

if __name__ == "__main__":
    main()
