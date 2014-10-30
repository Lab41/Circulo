from functools import partial
import igraph
import circulo.algorithms

WEIGHT_PRUNE_THRESHOLD=.75


def cleanup(ctx, descript, algo_directed, algo_simple):
    '''
    GRAPH Cleaning: Sometimes the graphs need to be cleaned for certain type of algorithms.
    The idea here is that we are trying to best match the data to what the algorithm can do.
    We start with specific matches and work our way to more general.
    '''

    #first we check if the algo can take BOTH a directed and SIMPLE graph.
    if ctx['directed'] == algo_directed and ctx['simple'] == algo_simple:
        print("\t[Info - ", descript, "] - No graph cleaning required")
        return ctx['graph'], ctx['weight'], ctx['directed']


    collapsed = False
    directed_graph = ctx['directed']


    if algo_directed is True and directed_graph is False:
        print("\t[Info - ", descript, "] - Warning: Passing undirected graph to directed algo")

    #otherwise we need to make some mods to the graph, so we will copy it then make the mods
    G_copy = ctx['graph'].copy()

    #if the graph is directed and algo is not directed
    if ctx['directed'] and not algo_directed:
        #can't collapse on weight without first making sure the edges are weighted
        #In this case, we just give each edge a weight of 1
        if not G_copy.is_weighted():
            G_copy.es()['weight'] = 1
        #here we make the actual conversion
        G_copy.to_undirected(combine_edges={'weight':sum})
        print('\t[Info - ',descript,'] Converting graph to undirected (summing edge weights)')
        collapsed = True

    #if the algo is simple but the data is not, then we have to make the data simple
    if algo_simple and not ctx['simple']:
        #can't collapse on weight without first making sure the edges are weighted
        if not G_copy.is_weighted():
            G_copy.es()['weight'] = 1
        G_copy.simplify(combine_edges={'weight':sum})
        print('\t[Info - ',descript,'] Collapsed multigraph edges (summing edge weights)')
        collapsed = True

    if collapsed == True:
        weights = G_copy.es()['weight']
        threshold =  WEIGHT_PRUNE_THRESHOLD * max(weights)
        edges = G_copy.es.select(weight_lt=threshold)
        G_copy.delete_edges(edges)
        print("\t[Info - ", descript,"] Pruned ", len(edges)," edges less than ", WEIGHT_PRUNE_THRESHOLD, "%")
        #if the graph is collapsed, I think it becomes undirected
        directed_g = False

    weights = "weight" if G_copy.is_weighted() else None

    return G_copy, weights, directed_graph


stochastic_algos = {
        "infomap",
        "fastgreedy",
        "leading_eigenvector",
        "multilevel",
        "label_propogation",
        "walktrap",
        "spinglass",
        "bigclam",
        "clauset_newman_moore"
        }

def comm_infomap(ctx, descript):
    G, weights,_  = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_infomap, G, edge_weights=weights, vertex_weights=None)

def comm_fastgreedy(ctx, descript):
    G, weights,_ = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_fastgreedy, G, weights=weights)

def comm_edge_betweenness(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=True, algo_simple=True)
    return partial(igraph.Graph.community_edge_betweenness, G, directed, weights)

def comm_leading_eigenvector(ctx, descript):
    G, weights, _ = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_leading_eigenvector, G, weights=weights)

def comm_multilevel(ctx, descript):
    G, weights, _ = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_multilevel, G,  weights=weights)

def comm_label_propagation(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_label_propagation, G, weights=weights)

def comm_walktrap(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_walktrap, G, weights=weights)

def comm_spinglass(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_spinglass, G, weights=weights)

def comm_conga(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.conga.conga, G)

def comm_congo(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return  partial(circulo.algorithms.congo.congo, G)

def comm_radicchi_strong(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'strong')

def comm_radicchi_weak(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'weak')

def comm_bigclam(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_bigclam.bigclam, G)

def comm_coda(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_coda.coda, G)

def comm_clauset_newman_moore(ctx, descript):
    G, weights, directed = cleanup(ctx, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_cnm.clauset_newman_moore, G)
