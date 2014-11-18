from functools import partial
import igraph
import circulo.algorithms
import statistics

from circulo.data.databot import CirculoData

def cleanup(G, descript, algo_directed, algo_simple):
    '''
    GRAPH Cleaning: Sometimes the graphs need to be cleaned for certain type of algorithms.
    The idea here is that we are trying to best match the data to what the algorithm can do.
    We start with specific matches and work our way to more general.
    '''

    #first we check if algo and data have same directedness and type.
    if G.is_directed() == algo_directed and G.is_simple() == algo_simple:
        print("\t[Info - ", descript, "] - No graph cleaning required directed: ", algo_directed, " simple: ", algo_simple)
        weight_attr =  "weight" if G.is_weighted() else None
        return G, weight_attr

    collapsed = False
    directed_graph = G.is_directed()


    if algo_directed and not G.is_directed():
        print("\t[Info - ", descript, "] - Warning: Passing undirected graph to directed algo")

    #otherwise we need to make some mods to the graph, so we will copy it then make the mods
    G_copy = G.copy()

    #if the graph is directed and algo is not directed
    if G.is_directed() and not algo_directed:
        #can't collapse on weight without first making sure the edges are weighted
        #In this case, we just give each edge a weight of 1
        if not G_copy.is_weighted():
            G_copy.es()['weight'] = 1
        #here we make the actual conversion
        G_copy.to_undirected(combine_edges={'weight':sum})
        print('\t[Info - ',descript,'] Converting graph to undirected (summing edge weights)')
        collapsed = True

    #if the algo is simple but the data is not, then we have to make the data simple
    if algo_simple and not G.is_simple():
        #can't collapse on weight without first making sure the edges are weighted
        if not G.is_weighted():
            G_copy.es()['weight'] = 1
        G_copy.simplify(combine_edges={'weight':sum})
        print('\t[Info - ',descript,'] Collapsed multigraph edges (summing edge weights)')
        collapsed = True

    if collapsed == True:
        weights = G_copy.es()['weight']

        #print("MEDIAN: ", statistics.median(weights), " MAX: ", max(weights))
        threshold = statistics.median(weights)
        orig_edge_len = G_copy.ecount()
        edges = G_copy.es.select(weight_lt=threshold)
        G_copy.delete_edges(edges)
        print("\t[Info - ", descript,"] Pruned ", len(edges)," of ",orig_edge_len," edges less than weight of ", threshold)
        #if the graph is collapsed, I think it becomes undirected
        directed_graph = False

    #we could do this outside the function, but it makes it cleaner this way
    weights_attr = "weight" if G_copy.is_weighted() else None


    return G_copy, weights_attr


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

def comm_infomap(G, ctx, descript):
    G, weights  = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_infomap, G, edge_weights=weights, vertex_weights=None)

def comm_fastgreedy(G, ctx, descript):
    G, weights  = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_fastgreedy, G, weights=weights)

def comm_edge_betweenness(G, ctx, descript):
    G, weights  = cleanup(G, descript, algo_directed=True, algo_simple=True)
    return partial(igraph.Graph.community_edge_betweenness, G, G.is_directed(), weights)

def comm_leading_eigenvector(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_leading_eigenvector, G, weights=weights)

def comm_multilevel(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_multilevel, G,  weights=weights)

def comm_label_propagation(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_label_propagation, G, weights=weights)

def comm_walktrap(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_walktrap, G, weights=weights)

def comm_spinglass(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_spinglass, G, weights=weights)

def comm_conga(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.conga.conga, G)

def comm_congo(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return  partial(circulo.algorithms.congo.congo, G)

def comm_radicchi_strong(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'strong')

def comm_radicchi_weak(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'weak')

def comm_bigclam(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)

    num_comms =  ctx[CirculoData.CONTEXT_OPTIMAL_PARTITIONS] if CirculoData.CONTEXT_OPTIMAL_PARTITIONS in ctx.keys() else 100

    min_comms = int(num_comms * .8)
    max_comms = int(num_comms * 1.2)

    print("COMMS: ", num_comms, min_comms, max_comms)

    return partial(circulo.algorithms.snap_bigclam.bigclam, G, detect_comm=num_comms, min_comm=min_comms, max_comm=max_comms)

def comm_coda(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_coda.coda, G)

def comm_clauset_newman_moore(G, ctx, descript):
    G, weights = cleanup(G, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_cnm.clauset_newman_moore, G)
