import igraph
import os
import subprocess
from circulo.utils.snap import setup, read_communities_by_community


def coda(G, data_prefix='snap_', node_filepath='', graph_type=0, detect_comm=100, min_comm=5, max_comm=100, trials=10, threads=4, alpha=0.05, beta=0.3):
    '''
    Coda from Snap

    Parameters
    ----------
    G :                 A NetworkX graph or edge list file
    node_file_path:     Input file name for node names (Node ID, Node label)
    graph_type:         0=directed, 1=undirected (default: 0)
    detect_comm:        The number of communities to detect (-1: detect automatically) (Default: 100)
    min_comm:           Minimum number of communities to try (Default = 5)
    max_comm:           Maximum number of communities to try (Default = 100)
    trials:             How many trials for the number of communities (Default = 10)
    threads:            Number of threads for parallelization (Default = 4)
    alpha:              Alpha for backtracking line search (Default = 0.05)
    beta:               Beta for backtracking line search (Default = 0.3)
    '''

    snap_home, graph_file = setup(G)
    path_coda = os.path.join(snap_home, "examples", "coda", "coda")

    try:

        out = subprocess.Popen([path_coda,"-o:"+data_prefix,"-i:"+graph_file,"-l:"+node_filepath,"-g:"+str(graph_type),"-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-sa:"+str(alpha), "-sb:"+str(beta)]).wait()

    except TypeError as e:
        print("Error occurred: {}".format(e))
        return


    os.remove(graph_file)

    #CODE returns an "in" and an "out" file. Not sure why... so am just using out
    return read_communities_by_community(data_prefix + "cmtyvv.out.txt", G)



def main():

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = coda(G)
    print(vc)


if __name__ == "__main__":
    main()
