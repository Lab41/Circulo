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


import csv
import re
import sys
import os
import glob
from subprocess import call

import igraph
from igraph import VertexCover

from circulo.data.databot import CirculoData


class NBAData(CirculoData):


    def __download__(self):

        try:
            call(["git", "clone", "https://github.com/davewalk/2013-2014-nba-schedule", self.raw_data_path])
        except Exception as e:
            print("Git Clone Failed to retrieve data")
            raise(e)


    def convert(self, string):
        '''
        Puts the team names into a consistent format since the naming is inconsistent throughout
        the datasets
        '''
        string = string.lower()
        string = re.sub('_',"-", string)
        string = re.sub(' ',"-", string)
        return string


    def __prepare__(self):

        team_dict = {}

        G = igraph.Graph()

        data_regex = os.path.join(self.raw_data_path,"data","csv",'*.csv')

        #adds the vertices strictly based on the names of the files
        for filename in glob.glob(data_regex):
            std_team_name = re.sub('.csv',"",os.path.basename(filename))
            std_team_name = re.sub('_',"-",std_team_name)
            G.add_vertex(std_team_name)

        #each file represents a team
        for filename in glob.glob(data_regex):

            with open(filename, "r") as data:

                reader = csv.reader(data)
                std_team_name = re.sub('.csv',"",os.path.basename(filename))
                std_team_name = re.sub('_',"-", std_team_name)

                team0 = G.vs.find(name=std_team_name)

                #skip first row of header info
                next(reader,None)

                for row in reader:

                    std_opponent = self.convert(row[2])
                    team1 = G.vs.find(name=std_opponent)

                    if team0 is None or team1 is None:
                        raise("Vertex not found for input team name")
                        sys.exit(1)

                    G.add_edge(team0, team1)

        G.write_graphml(self.graph_path)


    def get_ground_truth(self, G):

        #ground truth table
        divisions = {
                "boston-celtics":0,
                "brooklyn-nets":0,
                "new-york-knicks":0,
                "philadelphia-76ers":0,
                "toronto-raptors":0,
                "chicago-bulls":1,
                "cleveland-cavaliers":1,
                "detroit-pistons":1,
                "indiana-pacers":1,
                "milwaukee-bucks":1,
                "atlanta-hawks":2,
                "charlotte-bobcats":2,
                "miami-heat":2,
                "orlando-magic":2,
                "washington-wizards":2,
                "dallas-mavericks":3,
                "houston-rockets":3,
                "memphis-grizzlies":3,
                "new-orleans-pelicans":3,
                "san-antonio-spurs":3,
                "denver-nuggets":4,
                "minnesota-timberwolves":4,
                "oklahoma-city-thunder":4,
                "portland-trail-blazers":4,
                "utah-jazz":4,
                "golden-state-warriors":5,
                "los-angeles-clippers":5,
                "los-angeles-lakers":5,
                "phoenix-suns":5,
                "sacramento-kings":5
                }

        cluster_list = [[],[],[],[],[],[]]

        for vertex_id, team_name in enumerate(G.vs['name']):
            cluster_list[divisions[team_name]].append(vertex_id)

        return VertexCover(G, cluster_list)

def main():
    databot = NBAData("nba_schedule")
    databot.get_ground_truth(databot.get_graph())

if __name__ == "__main__":
    main()
