from collections import Counter, defaultdict
import itertools
import igraph as ig
import numpy as np

def CONGO(OG, h):
    """
    TODO
    """
    G = OG.copy()
    edgeBetweenness, pairBetweenness = edge_and_pair_betweenness(G)
    
    
    while G.es:
        split = remove_edge_or_split_vertex(G, edgeBetweenness, pairBetweenness)
        edgeBetweenness, pairBetweenness = recalculate_betweenness(G, edgeBetweenness, pairBetweenness)
        #edgeBetweenness, pairBetweenness = edge_and_pair_betweenness(G)


def recalculate_betweenness(G, eb, pb):
    return edge_and_pair_betweenness(G)


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

def remove_edge_or_split_vertex(G, eb, pb):
    maxEdge = max(eb, key=eb.get)
    maxEb = eb[maxEdge]
    vertexBetweenness = vertex_betweeenness_from_eb(G, eb)
    print vertexBetweenness
    vInteresting = [i for i, b in enumerate(vertexBetweenness) if b > maxEb]
    if vInteresting:
        maxSplitBetweenness, vToSplit, splitInstructions = \
          max_split_betweenness(G, pb, vInteresting)
        print maxSplitBetweenness, maxEb
        if maxSplitBetweenness > maxEb: # check is this guaranteed?
            print "here"
            return split_vertex(G, vToSplit, splitInstructions)
    return delete_edge(G, maxEdge)


def delete_edge(G, edge):
    """ 
    Given a graph G and one of its edges in tuple form, checks if the deletion 
    splits the graph.
    """
    edgeTup = tuple(edge)
    #print edgeTup
    G.delete_edges(edgeTup)
    return check_for_split(G, edgeTup)


def check_for_split(G, edge):
    """
    Given an edge in tuple form, check if it splits the
    graph into two disjoint clusters. If so, it returns
    True. Otherwise, False.
    """
    # Possibly keep a record of splits.
    return not G.edge_disjoint_paths(source=edge[0], target=edge[1])



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

        uwTup = tuple(uw)
        print uwTup
        clique[mapping[uwTup[0]], mapping[uwTup[1]]] = score
        clique[mapping[uwTup[1]], mapping[uwTup[0]]] = score

    # Ignore any self loops if they're there. If not, this line
    # does nothing and can be removed.
    np.fill_diagonal(clique, 0)
    return clique



def max_split_betweenness(G, pb, vInteresting):
    maxSplitBetweenness = 0    
    # for every vertex of interest, we want to figure out the maximum score achievable
    # by splitting the vertices in various ways, and return that optimal split
    for v in vInteresting:
        clique = create_clique(G, v, pb[v])
        print clique, "here"
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

    return maxSplitBetweenness, vToSplit, splitInstructions



def edge_and_pair_betweenness(G):
    """
    Calculates the edge betweenness and pair betweenness of
    all edges and vertices in the graph G. Returns (eb, pb)
    where eb is of the form {frozenset((v1, v2)):score} where
    v1 and v2 are the ids of the terminal vertices of the edge 
    and score is its betweenness, and pb is of the form 
    {v:frozenset((u, w)):score} where v is the index of the middle
    vertex, u, w its neighbors, and score the pair betweenness.
    """
    
    numVertices = G.vcount()
    edge_betweenness = defaultdict(float)
    pair_betweenness = initialize_pair_betweenness_dict(G)

    for vIndex in range(numVertices):
        pathCounts = Counter()
        # Only find the shortest paths that we haven't already seen
        shortest_paths_from_v = G.get_all_shortest_paths(vIndex, to=range(vIndex + 1, numVertices))
        for path in shortest_paths_from_v: # reads twice. Can I get it down to once?
            pathCounts[path[-1]] += 1
        for path in shortest_paths_from_v:
            update_betweenness(G, path, pair_betweenness, edge_betweenness, pathCounts[path[-1]])
    return edge_betweenness, pair_betweenness


def initialize_pair_betweenness_dict(G):
    """
    Initializes and zeroes out the pair betweenness dict.

    The dict is of the form {v:frozenset((u, w)):score}, 
    where v is the index of the middle vertex, u and w its neighbors
    in the calculation, and score the group's pair betweenness.
    """
    return {vertex.index : {frozenset(uw) : 0 for uw in 
                                itertools.permutations(G.neighbors(vertex), 2)}
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
        pair[path[pos + 1]][frozenset((path[pos], path[pos + 2]))] += weight
        edge[frozenset((path[pos], path[pos + 1]))] += weight
        pos += 1
    while pos < len(path) - 1:
        edge[frozenset((path[pos], path[pos + 1]))] += weight
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
        vb = .5 * (sum(eb[frozenset(G.es[e].tuple)] for e in incidentEdges) - (numComponents - 1))
        vbs.append(vb)
    return vbs


if __name__ == "__main__":
    CONGO(ig.read("football.gml"), None)