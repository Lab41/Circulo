import igraph
import numpy as np

def radicchi(G):
    g = G.copy()
    splits = []
    while g.ecount() > 0:
        edge_ccs = {e.tuple : edge_clustering_coefficient(g, *e.tuple) for e in g.es}
        min_edge = min(edge_ccs, key=edge_ccs.get)
        print "Deleting %s, %s" % min_edge
        g.delete_edges(min_edge)
        if not in_same_component(g, *min_edge):
            print "ALSO APPENDING %s, %s" % min_edge
            splits.append(min_edge)

    return splits

def in_same_component(G, u, v):
    return G.edge_disjoint_paths(source=u, target=v) > 0

def edge_clustering_coefficient(G, u, v):
    udeg = G.degree(u)
    vdeg = G.degree(v)
    mdeg = min(udeg-1, vdeg-1)
    if mdeg == 0:
        return float('inf')
    else:
        cdeg = len(common_neighbors(G, u, v))
        return (cdeg + 1.0) / mdeg

def common_neighbors(G, u, v):
    return set(G.neighbors(u)) & set(G.neighbors(v))
