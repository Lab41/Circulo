import itertools
from time import time

def probability_metric(G, membershipList, n):
    pass




def p_in_after_n(G, v, n, comm):
    return p_in_after_n_r_cached(G, v, n, comm, {})



def p_in_after_n_r_cached(G, v, n, comm, cache):
    """
    Finds the probability that a particle will remain 
    within the community during every step of an 
    n step random walk, beginning from v. At each step,
    the particle is equally likely to travel to any
    of its neighbors.
    """
    #print cache
    if (v, n) in cache:
        return cache[(v, n)]
    if v not in comm:
        return 0

    neighbors = set(G.neighbors(v))
    numNeighbors = float(len(neighbors))
    if n == 1:
        # how many neighbors in community
        return len(neighbors & comm) / numNeighbors
    
    totalP = 0.

    for neighbor in neighbors:
        pGivenNeighbor = p_in_after_n_r_cached(G, neighbor, n-1, comm, cache)
        cache[(neighbor, n-1)] = pGivenNeighbor
        totalP += 1/numNeighbors * pGivenNeighbor#p_in_after_n_r(G, neighbor, n-1, comm)
    cache[(v, n)] = totalP
    return totalP

def p_in_after_n_r(G, v, n, comm):
    """
    Finds the probability that a particle will remain 
    within the community during every step of an 
    n step random walk, beginning from v. At each step,
    the particle is equally likely to travel to any
    of its neighbors.
    """
    #print cache
    # if (v, n) in cache:
    #     return cache[(v, n)]
    if v not in comm:
        return 0

    neighbors = set(G.neighbors(v))
    numNeighbors = float(len(neighbors))

    if n==0:
        print "here"
        return int(v in comm)
    # if n == 1:
    #     # how many neighbors in community
    #     return len(neighbors & comm) / numNeighbors
    
    totalP = 0.

    for neighbor in neighbors:
        print totalP
        pGivenNeighbor = p_in_after_n_r(G, neighbor, n-1, comm)
        #cache[(neighbor, n-1)] = pGivenNeighbor
        totalP += 1/numNeighbors * pGivenNeighbor#p_in_after_n_r(G, neighbor, n-1, comm)
        #print totalP
    # cache[(v, n)] = totalP
    return totalP


def p_in_after_n_i(G, v, n, comm):
    # slower than the recursive version, but yields a slightly
    # different answer. todo: figure out what's going on. 
    if v not in comm:
        return 0

    p = 1.
    travels = [v]
    for _ in range(n):
        travels = itertools.chain.from_iterable(G.neighbors(t) for t in travels)
        count = 0.
        leng = 0.
        newTravels = []
        for t in travels:
            if t in comm:
                count += 1
                newTravels.append(t)
            leng += 1
        if count == 0: return 0        
        p *= count/leng
        travels = newTravels
    return p


def test():
    import igraph as ig
    #g = ig.load("netscience_single_component.gml")
    g = ig.Graph()
    g.add_vertices(4)

    g.add_edge(0, 1)
    g.add_edge(0, 2)
    g.add_edge(0, 3)
    g.add_edge(1, 3)
    clust = g.community_edge_betweenness().as_clustering(2)
    print clust
    print len(clust)


    
    time1 = time()
    withCache = [[p_in_after_n(g, x, 2, set(cl)) for x in cl] for i, cl in enumerate(clust)]
    timeCache = time() - time1
    time1 = time()
    withoutCache = [[p_in_after_n_r(g, x, 2, set(cl)) for x in cl] for i, cl in enumerate(clust)]
    timeNoCache = time() - time1
    time1 = time()
    iterative = [[p_in_after_n_i(g, x, 2, set(cl)) for x in cl] for i, cl in enumerate(clust)]
    timeIter = time() - time1
    # time1 = time()
    # for _ in range(5):
    #     results1 = [[p_in_after_n(g, x, 5, set(cl)) for x in cl] for i, cl in enumerate(clust)]
    # print time() - time1
    # time1 = time()
    # for _ in range(5):
    #     results2 = [[p_in_after_n_i(g, x, 5, set(cl)) for x in cl] for i, cl in enumerate(clust)]
    # print time() - time1

    for i, v in enumerate(withoutCache):
        for j, v1 in enumerate(v):
            print "with Cache: ", withCache[i][j], timeCache
            print "without Cache: ", withoutCache[i][j], timeNoCache
            print "iterative: ", iterative[i][j], timeIter
            print "diffCache: ", withCache[i][j] - withoutCache[i][j]
            print "diffIterCache", withCache[i][j] - iterative[i][j]
            print "diffIterNoCache:", withoutCache[i][j] - iterative[i][j]
            print i, j
            print 
    # print results1
    # print 
    # print
    # print results2

if __name__ == "__main__":
    test()