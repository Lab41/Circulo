import igraph as ig
import itertools
import statistics


def probability_metric_graph(G, clusters):
    """
    Calculates the probability metric on the graph G for each cluster in
    clusters. Returns a list of 3-tuples [(a, b, c),...] where a is the mean,
    b the standard deviation, and c the variance, indexed by cluster id. 

    TODO: explain about/change default value of n. 
    """
    fullStats = []
    for cluster in clusters:
        fullStats.append(probability_metric_cluster(G, cluster))
    return fullStats


def probability_metric_cluster(G, members):
    """
    Given the members of a cluster and the graph they belong to, finds
    the cluster's mean, standard deviation, and variance. 

    Note: n currently defaults to the number of members in the community.
    TODO: testing, to find out whether this is a legitimate normalization.
    """
    nMembers = len(members) # figure out if this is a good normalization
    data = [p_in_after_n(G, v, nMembers, members) for v in members]
    mean = statistics.mean(data)
    stddev = statistics.pstdev(data, mu=mean)
    var = statistics.pvariance(data, mu=mean)
    return mean, stddev, var


def p_in_after_n(G, v, n, comm):
    """
    Finds the probability that a particle will remain 
    within the community during every step of an 
    n step random walk, beginning from v. At each step,
    the particle is equally likely to travel to any
    of its neighbors.
    """
    return p_in_after_n_r_cached(G, v, n, set(comm), {})


def p_in_after_n_r_cached(G, v, n, comm, cache):
    """
    Memoized, recursive implementation of p_in_after_n.
    Internal function.
    """
    if (v, n) in cache:
        # memoized, don't recurse
        return cache[(v, n)]
    if v not in comm:
        # left the community
        return 0

    neighbors = set(G.neighbors(v))
    numNeighbors = float(len(neighbors))

    if n == 1:
        # Second to last step of the possible recursion, 
        # short circuit so we don't have to recurse down to 0
        return len(neighbors & comm) / numNeighbors
    
    totalP = 0.
    for neighbor in neighbors:
        pGivenNeighbor = p_in_after_n_r_cached(G, neighbor, n-1, comm, cache)
        cache[(neighbor, n-1)] = pGivenNeighbor
        totalP += 1/numNeighbors * pGivenNeighbor
    cache[(v, n)] = totalP
    return totalP


if __name__ == "__main__":
    g = ig.load("netscience_single_component.gml")
    clust = g.community_edge_betweenness().as_clustering()
    print(probability_metric_graph(g, clust))
   # print probability_metric(g, clust, 3)