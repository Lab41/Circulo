import igraph as ig
import statistics


def probability_metric_score(G, clusters):
    """
    Returns the mean of all of the cluster's scores under the probability metric 
    defined below. Contains much less information than probability_metric_graph,
    but allows for a single number with which one can compare clustering algorithms.
    """
    l = [p[0] for p in probability_metric_graph(G, clusters)]
    return statistics.mean(l);

def probability_metric_graph(G, clusters):
    """
    Calculates the probability metric on the graph G for each cluster in
    clusters. Returns a list of 3-tuples [(a, b, c),...] where a is the mean,
    b the standard deviation, and c the variance, indexed by cluster id. 

    This metric measures how likely a particle placed on some vertex will stay within
    the original community after n random steps, where n is the number of vertices in 
    the community (or some other, better value for normalization). 

    This returns a list [(mean, variance)_0, (mean, variance)_1..., (mean, variance)_n]
    where the statistics within each cluster are represented by its index in the list.

    A high mean suggests strong community structure, but a high variance suggests that
    a few objects in the community might be outliers and not necessarily belong.
    
    Currently, we use the size of the community as the number of steps taken, but this
    isn't based on much theory. Some analysis is necessary to find a better choice for n.

    If you want one "score" to score the clustering instead of individual communities, 
    call probability_metric_score instead.
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
    # numVertices = G.vcount();
    # normalization = nMembers / numVertices 
    data = [p_in_after_n(G, v, nMembers, members) for v in members]
    mean = statistics.mean(data) # could divide mean by normalization
    var = statistics.pvariance(data, mu=mean)
    return mean, var


def p_in_after_n(G, v, n, comm):
    """
    Finds the probability that a particle will remain 
    within the community during every step of an 
    n step random walk, beginning from v. At each step,
    the particle is equally likely to travel to any
    of its neighbors.

    TODO: use weights
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
