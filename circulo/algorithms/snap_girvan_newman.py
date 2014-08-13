import igraph
from circulo.utils.snap import setup, divisive

def girvan_newman(G, output="communities.txt"):
    return divisive(G, "1", output)

def main():

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = girvan_newman(G)
    print(vc)

if __name__ == "__main__":
    main()
