import csv
import re
import sys
import os
import glob
from subprocess import call

import igraph
from igraph import VertexCover

git_dir = "2013-2014-nba-schedule"

def __download__(data_dir):
    """
    clones the data from the git repo to the raw data dir
    """

    os.mkdir(data_dir)

    try:
        call(["git", "clone", "https://github.com/davewalk/2013-2014-nba-schedule", os.path.join(data_dir, git_dir)])
    except Exception as e:
        print("Git Clone Failed to retrieve data")
        raise(e)


def convert(string):
    '''
    Puts the team names into a consistent format since the naming is inconsistent throughout
    the datasets
    '''
    string = string.lower()
    string = re.sub('_',"-", string)
    string = re.sub(' ',"-", string)
    return string


def __prepare__(data_dir, graph_path):
    '''
    Takes the raw data and converts it into a graphml file
    '''

    team_dict = {}

    fullpath = os.path.join(data_dir, graph_path)

    out = open(fullpath, "w")

    G = igraph.Graph()

    for filename in glob.glob(os.path.join(data_dir, git_dir,"data","csv",'*.csv')):
        std_team_name = re.sub('.csv',"",os.path.basename(filename))
        std_team_name = re.sub('_',"-",std_team_name)
        G.add_vertex(std_team_name)


    #each file represents a team
    for filename in glob.glob(os.path.join(data_dir,git_dir,"data","csv",'*.csv')):

        with open(filename, "r") as data:

            reader = csv.reader(data)

            std_team_name = re.sub('.csv',"",os.path.basename(filename))
            std_team_name = re.sub('_',"-", std_team_name)

            team0 = G.vs.find(name=std_team_name)

            #skip first row of header info
            next(reader,None)

            for row in reader:

                std_opponent = convert(row[2])
                team1 = G.vs.find(name=std_opponent)

                if team0 is None or team1 is None:
                    raise("Vertex not found for input team name")
                    sys.exit(1)

                #check if the pair already exists

                e = G.get_eid(team0.index, team1.index, directed=False, error=False)
                if e >= 0:
                    G.es[e]['weight'] += 1
                else:
                    G.add_edge(team0, team1, weight=1)

    G.write_graphml(fullpath)


def get_graph():

    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = "nba.graphml"
    full_path = os.path.join(data_dir, graph_path)

    if not os.path.exists(data_dir):
        __download__(data_dir)

    if not os.path.exists(full_path):
        __prepare__(data_dir, graph_path)

    return igraph.load(full_path)

def get_ground_truth(G):

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
    G = get_graph()
    clustering = get_ground_truth(G)

if __name__ == "__main__":
    main()
