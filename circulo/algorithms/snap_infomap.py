import igraph
from circulo.utils.snap import divisive, setup

def infomap(G, output="communities"):
    return divisive(G, "3", output)

def main():

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = infomap(G)
    print(vc)

if __name__ == "__main__":
    main()
