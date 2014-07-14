from collections import Counter, defaultdict
import itertools
import igraph as ig
import numpy as np
import operator
import logging

import overlap

# TODO:
#    * investigate is_separator
#    * rewrite initialization
#    * clean up logging
#    * only call fix_betweennesses when needed


def CONGO(OG, h):
    """
    Provides an Implementation of the CONGO algorithm defined by Steve Gregory 
    in his 2010 paper "A Fast Algorithm to Find Overlapping Communities in Networks."
    The parameters are OG, the graph on which the analysis is to be performed, and h, 
    the length of the longest shortest path that Congo is to consider.
    """

    logging.basicConfig(filename='congo.log',level=logging.DEBUG)
    G = OG.copy()

    # Just in case the original graph is disconnected
    comm = G.components()
    if len(comm) != 1:
        raise RuntimeError("Congo only makes sense for connected graphs.")

    # initializing attributes of copied graph
    G.vs['CONGA_orig'] = [i.index for i in OG.vs]
    G.es['eb'] = 0
    G.vs['pb'] = [{uw : 0 for uw in itertools.combinations(G.neighbors(vertex), 2)} for vertex in G.vs]

    # initializing all pair and edge betweennesses
    do_initial_betweenness(G, h)
    nClusters = 1

    # The first cover is simply the entire connected graph.
    allCovers = {nClusters : ig.VertexCover(OG)}
    while G.es:
        # get the edge with the max edge betweenness, and its betweenness.
        maxEdge, maxEb = max(enumerate(G.es['eb']), key=operator.itemgetter(1))
        G.vs['vb'] = G.betweenness(cutoff=h)
        
        # since split betweennes is upper bounded by vertex betweenness, we
        # only need to look at the vertices for which the vertex betweenness
        # is greater than the max edge betweenness. (We multiply by 2
        # because our edge betweenness calculations yield values in both
        # directions.)

        # TODO check if I need to multiply by 2
        vInteresting = [i for i, b in enumerate(G.vs['vb']) if 2 * b > maxEb]
        
        logging.info("Vertices to examine: %s", vInteresting)
        splitInstr = max_split_betweenness(G, vInteresting)

        # split if max split betweenness > max edge betweenness
        if splitInstr is None or splitInstr[0] <= maxEb:
            split = delete_edge(G, maxEdge, h)
        else:
            split = split_vertex(G, splitInstr[1], splitInstr[2], h)

        logging.info("%d vertices remaining", len(G.es))

        if split:
            # there must be a new community
            comm = G.components().membership
            cover = get_cover(G, OG, comm)
            nClusters += 1
            # short circuit stuff would go here.
            allCovers[nClusters] = cover
    return overlap.CrispOverlap(OG, allCovers)


def delete_edge(G, edge, h):
    """ 
    Given a graph G and one of its edges in tuple form, checks if the deletion 
    splits the graph.
    """

    
    tup = G.es[edge].tuple

    logging.info("Deleted: %s", tup)
    
    neighborhood = get_neighborhood_edge(G, tup, h)
    # subtracts local betweennesses in the region, as discussed
    # in the paper
    do_local_betweenness(G, neighborhood, h, operator.neg)
    G.delete_edges(edge)
    fix_betweennesses(G)
    # adds back in local betweennesses after the deletion
    do_local_betweenness(G, neighborhood, h, operator.pos)
    return check_for_split(G, tup)



def fix_pair_betweennesses(G):
    """
    Given a graph G, makes sure that all of the pair betweennesses
    listed as attributes remain possible, and removes those that are not.
    Also adds new attributes where new edges have been added.
    """
    for v in G.vs:
        toDel = []
        neededPairs = {uw for uw in itertools.combinations(G.neighbors(v), 2)}
        for pair in v['pb']:
            if pair not in neededPairs:
                toDel.append(pair)
        for d in toDel:
            del v['pb'][d]
        for pair in neededPairs:
            if pair not in v['pb']:
                v['pb'][pair] = 0


def fix_edge_betweennesses(G):
    """
    Given a graph G, makes sure that every edge has a betweenness
    score assigned to it.
    """
    for e in G.es:
        if e['eb'] is None:
            e['eb'] = 0


def fix_betweennesses(G):
    """
    Fixes the pair and edge betweennesses such that every attribute is up to date.
    """
    fix_pair_betweennesses(G)
    fix_edge_betweennesses(G)


def split_vertex(G, vToSplit, instr, h):
    """
    Splits the vertex v into two new vertices, each with
    edges depending on s. Returns True if the split 
    divided the graph, else False.
    """
    neighborhood = get_neighborhood_vertex(G, vToSplit, h)
    do_local_betweenness(G, neighborhood, h, operator.neg)
    new_index = G.vcount()
    G.add_vertex()
    G.vs[new_index]['CONGA_orig'] = G.vs[vToSplit]['CONGA_orig']
    G.vs[new_index]['pb'] = {uw : 0 for uw in itertools.combinations(G.neighbors(vToSplit), 2)}

    # adding all relevant edges to new vertex, deleting from old one.
    toAdd = list(zip(itertools.repeat(new_index), instr[0]))
    toDelete = list(zip(itertools.repeat(vToSplit), instr[0]))
    G.add_edges(toAdd)
    G.delete_edges(toDelete)
    neighborhood.append(new_index)
    fix_betweennesses(G)
    logging.info("split: %d, %s", vToSplit, instr)
    do_local_betweenness(G, neighborhood, h, operator.pos)
    # check if the two new vertices are disconnected.
    return check_for_split(G, (vToSplit, new_index))


def max_split_betweenness(G, vInteresting):
    """
    Performs the greedy algorithm discussed in the 2007 CONGA paper
    to approximate the maximum split betweenness. Returns a tuple 
    (a, b, c) where a is the maximum score, b the vertex to split
    to acheive the score, and c a list of the instructions for which 
    neighbors to connect to each side of the split.
    """
    maxSplitBetweenness = 0   
    vToSplit = None
    # for every vertex of interest, we want to figure out the maximum score achievable
    # by splitting the vertices in various ways, and return that optimal split
    for v in vInteresting:
        clique = create_clique(G, v, G.vs['pb'][v])
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

        if clique[0,1] >= maxSplitBetweenness:
            maxSplitBetweenness = clique[0,1]
            vToSplit = v
            splitInstructions = vMap
    if vToSplit is None:
        return None

    return maxSplitBetweenness, vToSplit, splitInstructions


def do_initial_betweenness(G, h):
    """
    Given a graph G and a depth h, calculates all edge and pair betweennesses
    and update's G's attributes to reflect the new scores.
    """
    # TOOD: get all shortest paths of length h + 1 or less.
    # This whole function should be redone.
    all_pairs_shortest_paths = []
    # Counter for normalizing scores
    pathCounts = Counter()
    for ver in G.vs:
        logging.info("initializing betweennesses for %d", ver.index)
        neighborhood = get_neighborhood_vertex(G, ver, h)
        for i, v in enumerate(neighborhood):
            s_s_shortest_paths = G.get_all_shortest_paths(v, to=neighborhood)#[i+1:])
            all_pairs_shortest_paths += s_s_shortest_paths 

    all_pairs_shortest_paths = set(tuple(p) for p in all_pairs_shortest_paths)

    for path in all_pairs_shortest_paths:
        pathCounts[(path[0], path[-1])] += 1

    for path in all_pairs_shortest_paths:
        if len(path) <= h + 1:
            update_betweenness(G, path, pathCounts[(path[0], path[-1])], operator.pos)


def do_local_betweenness(G, neighborhood, h, op=operator.pos):
    """ 
    Given a neighborhood and depth h, recalculates all betweennesses
    confined to the neighborhood. If op is operator.neg, it subtracts these
    betweennesses from the current ones. Otherwise, it adds them.
    """
    all_pairs_shortest_paths = []
    pathCounts = Counter()
    for i, v in enumerate(neighborhood):
        s_s_shortest_paths = G.get_all_shortest_paths(v, to=neighborhood)#[i+1:])
        all_pairs_shortest_paths += s_s_shortest_paths 
    neighSet = set(neighborhood)
    neighSize = len(neighborhood)
    apsp = []
    for path in all_pairs_shortest_paths:
        # path does not go out of region
        if len(neighSet | set(path)) == neighSize:
            pathCounts[(path[0], path[-1])] += 1 # can improve
            apsp.append(path)
    for path in apsp:
        if len(path) <= h + 1:
            update_betweenness(G, path, pathCounts[(path[0], path[-1])], op)


def update_betweenness(G, path, count, op):
    """
    Given a shortest path in G, along with a count of paths
    that length, to determine weight, updates the edge and
    pair betweenness dicts with the path's new information.
    """
    weight = op(1./count)
    pos = 0
    while pos < len(path) - 2:
        G.vs[path[pos + 1]]['pb'][order_tuple((path[pos], path[pos + 2]))] += weight
        G.es[G.get_eid(path[pos], path[pos + 1])]['eb'] += weight
        pos += 1
    if pos < len(path) - 1:
        G.es[G.get_eid(path[pos], path[pos + 1])]['eb'] += weight


def get_cover(G, OG, comm):
    """
    Given the graph, the original graph, and a community
    membership list, returns a vertex cover of the communities 
    referring back to the original community.
    """
    coverDict = defaultdict(list)
    for i, community in enumerate(comm):
        coverDict[community].append(int(G.vs[i]['CONGA_orig']))
    return ig.clustering.VertexCover(OG, clusters=list(coverDict.values()))


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
        vb = .5 * (sum(G.es[e]['eb'] for e in incidentEdges) - (numComponents - 1))
        vbs.append(vb)
    return vbs


def get_neighborhood_vertex(G, v, h):
    """
    Given a vertex and a height/depth to 
    traverse, find the neighborhood as defined in the CONGA
    paper.
    """
    return G.neighborhood(v, order=h)


def get_neighborhood_edge(G, e, h):
    """
    Given an edge and a height/depth to 
    traverse, find the neighborhood as defined in the CONGA
    paper.
    """
    neigh = set(G.neighborhood(e[0], order=h-1))
    neigh.update(G.neighborhood(e[1], order=h-1))
    return list(neigh)


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
    for uw, score in pb.items():
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
        # TODO: specify exception (when edge = target)
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
    tg = ig.read("pgp.gml")
    tg = tg.as_undirected()
    result = CONGO(tg, 2)
    result.pretty_print_cover(result.optimal_count, label='label')
