from scipy.stats import describe
from scipy import median
import igraph

def aggregate(array, prefix="",axis=0):

    stats = describe(array, axis)

    return  {
        prefix+' Size':int(stats[0]),
        prefix+' Min':float(stats[1][0]),
        prefix+' Max':float(stats[1][1]),
        prefix+' Mean':float(stats[2]),
        prefix+' Unbiased Variance':float(stats[3]),
        prefix+' Biased Skewness':float(stats[4]),
        prefix+' Biased Kurtosis':float(stats[5]),
        prefix+' Median':float(median(array,axis))
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


