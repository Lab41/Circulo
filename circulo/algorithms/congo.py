from collections import Counter, defaultdict
import itertools
import igraph as ig
import numpy as np
import operator

import overlap



# NOTE: for karate test, use random seed 2. 
def CONGO(OG, h):
    """
    TODO
    """
    G = OG.copy()
    G.vs['CONGA_orig'] = [i.index for i in OG.vs]
    edgeBetweenness, pairBetweenness = edge_and_pair_betweenness(G, G.vs)
    
    comm = G.components()

    # Just in case the original graph is disconnected
    nClusters = len(comm)

    allCovers = {nClusters : ig.VertexCover(OG)}


    while G.es:
        split, edgeBetweenness, pairBetweenness = remove_edge_or_split_vertex(G, edgeBetweenness, pairBetweenness, h)
        print len(G.es)
        #print edgeBetweenness, pairBetweenness
        #edgeBetweenness, pairBetweenness = recalculate_betweenness(G, edgeBetweenness, pairBetweenness)
        if split:
            comm = G.components().membership
            cover = get_cover(G, OG, comm)
            nClusters += 1
            # short circuit stuff would go here.
            allCovers[nClusters] = cover
    return overlap.CrispOverlap(OG, allCovers)


def edge_and_pair_betweenness(G, region):
    """
    TODO
    """
    
    edge_betweenness = initialize_edge_betweenness_dict(G)
    pair_betweenness = initialize_pair_betweenness_dict(G)

    for i in range(len(region)):
        #print i, "/", len(region)
        pathCounts = Counter()
        # Only find the shortest paths that we haven't already seen
        shortest_paths_from_v = G.get_all_shortest_paths(region[i], to=region[i+1:])
        for path in shortest_paths_from_v: # reads twice. Can I get it down to once?
            pathCounts[path[-1]] += 1
        for path in shortest_paths_from_v:
            update_betweenness(G, path, pair_betweenness, edge_betweenness, pathCounts[path[-1]])
    return edge_betweenness, pair_betweenness




def add_or_subtract_betweenness(G, region, ebOld, pbOld, op=operator.pos):
    ebNew, pbNew = edge_and_pair_betweenness(G, region)
    for edge in ebNew:
        ebNew[edge] = op(ebNew[edge])
        if edge in ebOld:
            ebNew[edge] += ebOld[edge]
    for v in pbNew: # PYTHONIFY!
        for uw in pbNew[v]:
            pbNew[v][uw] = op(pbNew[v][uw])
            if v in pbOld and uw in pbOld[v]:
                pbNew[v][uw] += pbOld[v][uw]
    return ebNew, pbNew


    



def initialize_edge_betweenness_dict(G):
    return {e.tuple : 0 for e in G.es}


def remove_edge_or_split_vertex(G, eb, pb, h):
    maxEdge = max(eb, key=eb.get)
    maxEb = eb[maxEdge]
    vertexBetweenness = vertex_betweeenness_from_eb(G, eb)
    vInteresting = [i for i, b in enumerate(vertexBetweenness) if b > maxEb]
    if vInteresting:
        maxSplitBetweenness, vToSplit, splitInstructions = \
          max_split_betweenness(G, pb, vInteresting)
        if maxSplitBetweenness > maxEb: # check is this guaranteed?
            return split_vertex(G, vToSplit, splitInstructions, eb, pb, h)
    return delete_edge(G, maxEdge, eb, pb, h)




def recalculate_betweenness(G, eb, pb):
    return edge_and_pair_betweenness(G, G.vs)



def get_cover(G, OG, comm):
    """
    Given the graph, the original graph, and a community
    membership list, returns a vertex cover of the communities 
    referring back to the original community.
    """
    coverDict = defaultdict(list)
    for i, community in enumerate(comm):
        coverDict[community].append(int(G.vs[i]['CONGA_orig']))
    return ig.clustering.VertexCover(OG, clusters=coverDict.values())


def initialize_pair_betweenness_dict(G):
    """
    Initializes and zeroes out the pair betweenness dict.

    The dict is of the form {v:frozenset((u, w)):score}, 
    where v is the index of the middle vertex, u and w its neighbors
    in the calculation, and score the group's pair betweenness.
    """
    return {vertex.index : {uw : 0 for uw in 
                                itertools.combinations(G.neighbors(vertex), 2)}
                                    for vertex in G.vs}


def update_betweenness(G, path, pair, edge, count):
    """
    Given a shortest path in G, along with a count of paths
    that length, to determine weight, updates the edge and
    pair betweenness dicts with the path's new information.
    """
    weight = 1./count
    pos = 0
    while pos < len(path) - 2:
        pair[path[pos + 1]][order_tuple((path[pos], path[pos + 2]))] += weight
        edge[order_tuple((path[pos], path[pos + 1]))] += weight
        pos += 1
    while pos < len(path) - 1:
        edge[order_tuple((path[pos], path[pos + 1]))] += weight
        pos += 1


def vertex_betweeenness_from_eb(G, eb):
    """
    Calculates the vertex betweenness scores in G. Returns a list
    in which the indices are the vertex indices and the values are
    their betweeennesses. The same as G.betweenness(), but faster because
    it uses the edge betweenness scores.

    (CONGA, page 4, equation 1)
    """
    components = G.components()
    membership = components.membership
    vbs = []
    for vertex in G.vs:
        numComponents = len(components[membership[vertex.index]])
        incidentEdges = G.incident(vertex)
        vb = .5 * (sum(eb[G.es[e].tuple] for e in incidentEdges) - (numComponents - 1))
        vbs.append(vb)
    return vbs


def max_split_betweenness(G, pb, vInteresting):
    maxSplitBetweenness = 0   

    vToSplit = None
    # for every vertex of interest, we want to figure out the maximum score achievable
    # by splitting the vertices in various ways, and return that optimal split
    for v in vInteresting:
        clique = create_clique(G, v, pb[v])

        if clique.size < 4:
            continue
        # initialize a list on how we will map the neighbors to the collapsing matrix
        vMap = [[ve] for ve in G.neighbors(v)]
        
        # we want to keep collapsing the matrix until we have a 2x2 matrix and its
        # score. Then we want to remove index j from our vMap list and concatenate
        # it with the vMap[i]. This begins building a way of keeping track of how
        # we are splitting the vertex and its neighbors
        while clique.size > 4:
            i,j,clique = reduce_matrix(clique)
            vMap[i] += vMap.pop(j)

        if clique[0,1] > maxSplitBetweenness:
            maxSplitBetweenness = clique[0,1]
            vToSplit = v
            splitInstructions = vMap

    if vToSplit is None:
        return -1000, 0, None

    return maxSplitBetweenness, vToSplit, splitInstructions


def get_truncated_eb_and_pb(G, neighborhood):
    edge_betweenness = defaultdict(float)
    pair_betweenness = initialize_pair_betweenness_dict(G)

    for i in range(len(neighborhood)):
        pathCounts = Counter()
        # Only find the shortest paths that we haven't already seen
        shortest_paths_from_v = G.get_all_shortest_paths(neighborhood[i], to=neighborhood[i+1:])
        for path in shortest_paths_from_v: # reads twice. Can I get it down to once?
            pathCounts[path[-1]] += 1
        for path in shortest_paths_from_v:
            update_betweenness(G, path, pair_betweenness, edge_betweenness, pathCounts[path[-1]])
    return edge_betweenness, pair_betweenness

def subtract_betweenness(G, eb, pb, neighborhood):
    ebTrunc, pbTrunc = get_truncated_eb_and_pb(G, neighborhood)
    for key in ebTrunc:
        eb[key] -= ebTrunc[key]
    for v in pbTrunc:
        for uw in pbTrunc[v]:
            pb[v][uw] -= pbTrunc[v][uw]


def add_betweenness(G, eb, pb, neighborhood):
    ebTrunc, pbTrunc = get_truncated_eb_and_pb(G, neighborhood)
    for key in ebTrunc:
        eb[key] += ebTrunc[key]
    for v in pbTrunc:
        if v not in pb:
            pb[v] = pbTrunc[v]
        else:
            for uw in pbTrunc[v]:
                if uw in pb[v]:
                    pb[v][uw] += pbTrunc[v][uw]
                else:
                    pb[v][uw] = pbTrunc[v][uw]


def get_neighborhood_vertex(G, v, h):
    return G.neighborhood(v, order=h)


def get_neighborhood_edge(G, e, h):
    neigh = set(G.neighborhood(e[0], order=h-1))
    neigh.update(G.neighborhood(e[1], order=h-1))
    return list(neigh)


def split_vertex(G, v, splitInstructions, eb, pb, h):
    """
    Splits the vertex v into two new vertices, each with
    edges depending on s. Returns True if the split 
    divided the graph, else False.
    """
    neighborhood = get_neighborhood_vertex(G, v, h)
    eb, pb = add_or_subtract_betweenness(G, neighborhood, eb, pb, operator.neg)
    new_index = G.vcount()
    neighborhood.append(new_index)
    G.add_vertex()
 #   G.vs[new_index]['label'] = G.vs[v]['label']
    G.vs[new_index]['CONGA_orig'] = G.vs[v]['CONGA_orig']
    
    # adding all relevant edges to new vertex, deleting from old one.
    for partner in splitInstructions[0]:
        G.add_edge(partner, new_index)
        G.delete_edges((v, partner)) 
    #    clean_betweennesses(pb, eb, (v, partner))

    print "split:", v, splitInstructions
    eb, pb = add_or_subtract_betweenness(G, neighborhood, eb, pb, operator.pos)

    # check if the two new vertices are disconnected.
    return check_for_split(G, (v, new_index)), eb, pb


def delete_edge(G, edge, eb, pb, h):
    """ 
    Given a graph G and one of its edges in tuple form, checks if the deletion 
    splits the graph.
    """
    print "Deleted:", edge
    neighborhood = get_neighborhood_edge(G, edge, h)
    eb, pb = add_or_subtract_betweenness(G, neighborhood, eb, pb, operator.neg)
    G.delete_edges(edge)
    #clean_betweennesses(pb, eb, edge)
    eb, pb = add_or_subtract_betweenness(G, neighborhood, eb, pb, operator.pos)
    #add_betweenness(G, eb, pb, neighborhood)
    return check_for_split(G, edge), eb, pb


def clean_betweennesses(pb, eb, deleted_edge):
    de = order_tuple(deleted_edge)
    try:
        del eb[de]
    except Exception as e:
        print e
    for v in pb:
        if v in de:
            todelete = []
            for uw in pb[v]:
                if set(uw) & set(de):
                    todelete.append(uw)
            for d in todelete:
                del pb[v][d]


def order_tuple(toOrder):
    if toOrder[0] <= toOrder[1]:
        return toOrder
    return (toOrder[1], toOrder[0])


def create_clique(G, v, pb):
    """
    Given a vertex and its pair betweennesses, returns a k-clique 
    representing all of its neighbors, with edge weights determined by the pair
    betweenness scores. Algorithm discussed on page 5 of the CONGA paper. 
    """
    neighbors = G.neighbors(v)

    # map each neighbor to its index in the adjacency matrix
    mapping = {neigh : i for i, neigh in enumerate(neighbors)}
    n = len(neighbors)

    # Can use ints instead: (dtype=int). Only works if we use matrix_min
    # instead of mat_min.
    clique = np.matrix(np.zeros((n, n)))

    for uw, score in pb.iteritems():

        
        clique[mapping[uw[0]], mapping[uw[1]]] = score
        clique[mapping[uw[1]], mapping[uw[0]]] = score

    # Ignore any self loops if they're there. If not, this line
    # does nothing and can be removed.
    np.fill_diagonal(clique, 0)
    return clique


def reduce_matrix(M):
    """
    Given a matrix M, collapses the row and column of the minimum value. This is just
    an adjacency matrix way of implementing the greedy "collapse" discussed in CONGA.

    Returns the new matrix and the collapsed indices. 
    """
    i,j = mat_min(M)
    #i, j = matrix_min(M)
    # add the ith row to the jth row and overwrite the ith row with those values
    M[i,:] = M[j,:] + M[i,:]
    
    # delete the jth row
    M = np.delete(M, (j), axis=0)
    
    # similarly with the columns
    M[:,i] = M[:,j] + M[:,i]
    M = np.delete(M, (j), axis=1)
    np.fill_diagonal(M,0) # not sure necessary.
    return i,j,M


def check_for_split(G, edge):
    """
    Given an edge in tuple form, check if it splits the
    graph into two disjoint clusters. If so, it returns
    True. Otherwise, False.
    """
    # Possibly keep a record of splits.
    try:
        return not G.edge_disjoint_paths(source=edge[0], target=edge[1])
        # specify exception
    except Exception as e:
        return False




def mat_min(M):
    """
    Given a matrix, find an index of the minimum value (not including the
    diagonal).
    """
    # take a matrix we pass in, and fill the diagonal with the matrix max. This is
    # so that we don't grab any values from the diag.
    np.fill_diagonal(M, float('inf'))
    
    # figure out the indices of the cell with the lowest value.
    i,j = np.unravel_index(M.argmin(), M.shape)
    np.fill_diagonal(M,0)
    return i, j



def matrix_min(mat):
    """
    Given a symmetric matrix, find an index of the minimum value 
    in the upper triangle (not including the diagonal.)
    """
    # Currently, this function is unused, as its result is 
    # the same as that of mat_min, and it is not always
    # faster. Left in for reference in case mat_min becomes
    # a bottleneck. 

    # find the minimum from the upper triangular matrix 
    # (not including the diagonal)
    upperTri = np.triu_indices(mat.shape[0], 1)
    minDex = mat[upperTri].argmin()

    # find the index in the big matrix. TODO: do so
    # with some algebra.
    triN = mat.shape[0] - 1
    row = 0
    
    
    while minDex >= triN:
        minDex -= triN
        triN -= 1
        row += 1
    col = mat.shape[0] - triN + minDex
    return row, col















if __name__ == "__main__":
    #tg = ig.Graph.Growing_Random(100, 5, citation=True)
    tg = ig.read("football.gml")
    tg = tg.as_undirected()
    print "starting"
    result = CONGO(tg, 200)
    print "done."
    result.pretty_print_cover(result.optimal_count, label='label')
#    CONGO(ig.read("football.gml").as_undirected(), 2).pretty_print_cover(10, label='label')
