# Goal is to annotate a vertex cover with dictionary representing various cluster metrics

from igraph import Graph


def __describe(array, axis=0):
  from scipy.stats import describe
  from scipy import median
  stats = describe(array, axis)
  stats = stats + (median(array, axis),)

  return dict(zip(['Size', '(min,max)', 'Arithmetic Mean', 'Unbiased Variance', 'Biased Skewness', 'Biased Kurtosis', 'Median'], stats))

def triangle_participation(G):
    '''
    This returns an array indicating whether the ith node in the graph belongs to a triad.
    '''
    rv = [False]*G.vcount()

    for u in G.vs():
        if rv[u.index]:
            continue
        for v in u.neighbors():
            for w in v.neighbors():
                is_triad = u in w.neighbors()
                rv[u.index] |= is_triad
                rv[v.index] |= is_triad
                rv[w.index] |= is_triad
    return rv

def triangle_participation_ratio(G):
    '''
    The fraction of nodes in a graph that belong to a triad.
    '''
    rv = G.triangle_participation()
    return sum(rv)/G.vcount()

def cohesiveness(G):
    '''
    Equation: g(S) = minS′⊂S φ(S′) where φ(S′) is the conductance of S′ measured in the induced subgraph by S.
    To iterate over all possible subgraphs of a community would be too inefficient 2^n, therefore we approximate
    the best subgraph (which would have the lowest conductance) by using Local Spectral communitying to find the best
    cut
    (cite: http://cs.stanford.edu/people/jure/pubs/comscore-icdm12.pdf)
    '''
    from circulo.algorithms import spectral
    if G.vcount() <= 2:
        val = 1
    else:
        #TODO: Consider using G_i.mincut() instead.
        val, vc = spectral.min_conductance(G)
    return val

def compute_metrics(G, refresh = True):
    if refresh or G.metrics == None:
        G.metrics = {
                'Internal Number Nodes'         : G.vcount(),
                'Internal Number Edges'         : G.ecount(),
                'Density'                       : G.density(),
                'Degree Statistics'             : __describe(G.degree()),
                'Diameter'                      : G.diameter(),
                'Cohesiveness'                  : G.cohesiveness(), 
                'Triangle Participation Ratio'  : G.triangle_participation_ratio(),
                'Transitivity Undirected (Global Clustering Coefficient)'
                                                : G.transitivity_undirected(),
                'Transitivity Local Undirected (Local Clustering Coefficient)'
                                                : __describe(G.transitivity_local_undirected(mode='zero'))
        }

Graph.metrics = None
Graph.compute_metrics = compute_metrics
Graph.cohesiveness = cohesiveness
Graph.triangle_participation = triangle_participation
Graph.triangle_participation_ratio = triangle_participation_ratio
