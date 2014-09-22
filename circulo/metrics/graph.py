# coding: utf-8
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
    return 1.0*sum(rv)/G.vcount()

def cohesiveness(G, weights=None):
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
        val, vc = G.min_conductance(weights=weights)
    return val

def __helper_m(key_prefix, describe_dict):
    dict0 = {}

    for k, v in describe_dict.items():
        if k == "(min,max)":
            min_key = key_prefix + " (min)"
            max_key = key_prefix = " (max)"

            dict0[min_key] = v[0]
            dict0[max_key] = v[1]

            pass
        else:
            new_key = key_prefix + " (" + k + ")"
            dict0[new_key] = v

def compute_metrics(G, refresh = True):

    if refresh or G.metrics == None:
        G.metrics = {
                'Internal Number Nodes'         : G.vcount(),
                'Internal Number Edges'         : G.ecount(),
                'Density'                       : G.density(),
                #'Degree Statistics'             : __describe(G.degree()),
                'Diameter'                      : G.diameter(),
                'Cohesiveness'                  : G.cohesiveness(),
                'Triangle Participation Ratio'  : G.triangle_participation_ratio(),
                'Transitivity Undirected (Global Clustering Coefficient)'
                                                : G.transitivity_undirected()
                #'Transitivity Local Undirected (Local Clustering Coefficient)'
                #                                : __describe(G.transitivity_local_undirected(mode='zero'))

                }
        #Transitivity Local Undirected(Local Clustering Coefficient)
        combined = G.metrics + __helper_m('TLU--Local Clustering Coefficient', __describe(G.transitivity_local_undirected(mode='zero'))
        #Degree statistics
        #G.metrics += __helper_m('Degree Statistics', __describe(G.degree())

        import sys
        sys.exit(0)



Graph.metrics = None
Graph.compute_metrics = compute_metrics
Graph.cohesiveness = cohesiveness
Graph.triangle_participation = triangle_participation
Graph.triangle_participation_ratio = triangle_participation_ratio
