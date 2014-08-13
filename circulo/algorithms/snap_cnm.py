import igraph
from circulo.utils.snap import divisive, setup

def clauset_newman_moore(G, output="communities.txt"):
    return divisive(G, "2", output)

def main():

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = clauset_newman_moore(G)
    print(vc)

if __name__ == "__main__":
    main()
