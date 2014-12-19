from scipy.stats import describe
from scipy import median
import igraph
import numpy as np
from itertools import combinations

from circulo.metrics.omega import omega_index

def aggregate(array, prefix="",axis=0):

    stats = describe(array, axis)

    if len(array) == 1:
        variance = -1.0
    else:
        variance = float(stats[3])


    return  {
        prefix+'Size':int(stats[0]),
        prefix+'Min':float(stats[1][0]),
        prefix+'Max':float(stats[1][1]),
        prefix+'Mean':float(stats[2]),
        prefix+'Unbiased Variance':variance,
        prefix+'Biased Skewness':float(stats[4]),
        prefix+'Biased Kurtosis':float(stats[5]),
        prefix+'Median':float(median(array,axis))
            }



def get_largest_component(G, descript="not specified"):
    """
    Given a graph, returns the subgraph containing only its largest component".
    """
    components = G.components(mode=igraph.WEAK)
    if len(components) == 1:
        return G
    print("[Graph Prep -",descript,"]... Disconnected Graph Detected. Using largest component.")
    print("[Graph Prep -",descript,"]... Original graph: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    G = G.subgraph(max(components, key=len))
    print("[Graph Prep -",descript,"]... Largest component: {} vertices and {} edges.".format(G.vcount(), G.ecount()))
    return G



def run_comparison(memberships, comparator="omega"):
    '''
    Given a list of memberships, uses the comparator to compare results

    Args:
        membershps: a list of membership arrays
        comparator: the algorithm to use at the comparator (default: omega)

    Return:
        a symetric matrix containing the results
    '''

    size = len(memberships)
    pairs = combinations(range(size), 2)
    M = np.zeros((size, size), dtype=float)
    np.fill_diagonal(M, 1)

    if comparator == "omega":
        comp_func = omega_index
    else:
        raise NotImplementedError('Unknown comparison function')

    #fill in top right
    for i, j in pairs:
        score = comp_func(memberships[i], memberships[j])
        M[i,j] = score
        M[j,i] = score

    return M
