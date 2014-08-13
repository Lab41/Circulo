import igraph
import os
import subprocess
from circulo.utils.snap import setup,read_communities_by_community

def bigclam(G, data_prefix='snap_', node_filepath='', detect_comm=100, min_comm=5, max_comm=100, trials=10, threads=4, alpha=0.05, beta=0.3):
    '''
    BigClam from Snap

    Parameters
    ----------
    G :                 A NetworkX graph or edge list file
    data_prefix:        Output file for communitities (data_prefix + cmtyvv.txt)
    node_file_path:     Input file name for node names (Node ID, Node label)
    detect_comm:        The number of communities to detect (-1: detect automatically) (Default: 100)
    min_comm:           Minimum number of communities to try (Default = 5)
    max_comm:           Maximum number of communities to try (Default = 100)
    trials:             How many trials for the number of communities (Default = 10)
    threads:            Number of threads for parallelization (Default = 4)
    alpha:              Alpha for backtracking line search (Default = 0.05)
    beta:               Beta for backtracking line search (Default = 0.3)

    Returns:  List of SubGraphs representing the communities.  The SubGraphs are automatically serialized to disk as file data_prefix+'cmtyvv.txt'
    '''

    snap_home, graph_file = setup(G)


    if graph_file is None:
        return

    path_bigclam = os.path.join(snap_home, "examples", "bigclam", "bigclam")

    try:

        out = subprocess.Popen([path_bigclam,"-o:"+data_prefix,"-i:"+graph_file,"-l:"+node_filepath,"-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-sa:"+str(alpha), "-sb:"+str(beta)]).wait()

    except TypeError as e:
        print("Error occurred: {}".format(e))
        return


    os.remove(graph_file)

    return read_communities_by_community(data_prefix + "cmtyvv.txt", G)


def main():

    G = igraph.Graph.Erdos_Renyi(n=30, m=100)
    snap_home, filename = setup(G)

    vc = bigclam(G)
    print(vc)


if __name__ == "__main__":
    main()
