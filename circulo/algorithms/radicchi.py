import igraph as ig

def radicchi(G):
    g = G.copy()
    splits = []
    while g.ecount() > 0:
        min_edge = None
        min_ecc = None # not float('inf') because edge_clustering_coefficient may actually return that; instead we just check for None
        degree = g.degree()
        neighbors = [set(g.neighbors(v)) for v in g.vs]
        for e in g.es:
            u, v = e.tuple
            ecc = edge_clustering_coefficient_1(u, v, degree, neighbors)
            # ecc = edge_clustering_coefficient_2(G, u, v, degree)
            if not min_edge or ecc < min_ecc:
                min_edge = (u, v)
                min_ecc = ecc

        g.delete_edges(min_edge)
        u, v = min_edge
        if not in_same_component(g, u, v):
            # print "ALSO APPENDING %s, %s" % min_edge
            splits.append([u, v])

    return splits

def in_same_component(G, u, v):
    return G.edge_disjoint_paths(source=u, target=v) > 0

def edge_clustering_coefficient_1(u, v, degree, neighbors):
    udeg = degree[u]
    vdeg = degree[v]
    mdeg = min(udeg-1, vdeg-1)
    if mdeg ==0:
        return float('inf')
    else:
        cdeg = common_neighbors_1(u, v, neighbors)
        return (cdeg + 1.0) / mdeg

def edge_clustering_coefficient_2(G, u, v, degree):
    udeg = degree[u]
    vdeg = degree[v]
    mdeg = min(udeg-1, vdeg-1)
    if mdeg == 0:
        return float('inf')
    else:
        cdeg = common_neighbors_2(G, u, v, udeg, vdeg)
        return (cdeg + 1.0) / mdeg

def common_neighbors_1(u, v, neighbors):
    return len(neighbors[u] & neighbors[v])

def common_neighbors_2(G, u, v, udeg, vdeg):
    dice = G.similarity_dice(pairs=[(u,v)], loops=False)[0]
    result = dice * (udeg + vdeg) * 0.5
    return result

def createDendrogram(G, splits):
   """
   Given a historical list of split edges, creates a dendrogram 
   by calculating the merges. 
 
   Unfortunately, runs in O(n^2). TODO: think about another algorithm
   (perhaps a tree approach?) that does better. This is a useful function
   for any divisive algorithm for which splits can be saved more easily
   than merges.

   Written by Robbie Ostrow (rostrow@iqt.org).
   """
 
   # To create a dendrogram, new merges have id of max id + 1
   n = len(splits) + 1
   merges = []
   while splits:
     # most recent split popped off
     edge = splits.pop()
 
     merges += [edge]
     
     # since we have merged 2 vertices, we have to replace
     # all occurences of those vertices with the new 
     # "merged" index n.
     splits = replaceOccurences(splits, n, edge)
     
     n += 1
 
   return ig.VertexDendrogram(G, merges)

def replaceOccurences(splits, n, edge):
    """
    Given a 2d list `splits`, replaces all occurences of elements in
    `edge` with n.
    """
    for i in range(len(splits)):
            for j in range(2):
                    if splits[i][j] in edge:
                            splits[i][j] = n
    return splits

if __name__ == "__main__":
    g = ig.Graph.Read_GML('netscience.gml')
    splits = radicchi(g)
    print splits
