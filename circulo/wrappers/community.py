from functools import partial
import igraph

import circulo.algorithms
from circulo.algorithms import *

import statistics


from circulo.data.databot import CirculoData


def cleanup(G, databot, descript, algo_directed, algo_simple, algo_uses_weights):
    '''
    GRAPH Cleaning: Sometimes the graphs need to be cleaned for certain type of algorithms.
    The idea here is that we are trying to best match the data to what the algorithm can do.
    We start with specific matches and work our way to more general.
    '''

    alterations = []

    #first we check if algo and data have same directedness and type.
    if G.is_directed() == algo_directed and G.is_simple() == algo_simple:
        weight_attr =  "weight" if G.is_weighted() else None
        return G, weight_attr, alterations

    if algo_directed and not G.is_directed():
        print("\t[Info - ", descript, "] - Warning: Passing undirected graph to directed algo")

    #make a copy to prevserve original
    G_copy = G.copy()

    #add edge weights if not existing
    if not G_copy.is_weighted():
        G_copy.es()['weight'] = 1
        alterations.append('weighted')

    #if the graph is directed and algo is not directed, we make the graph undirected
    if G_copy.is_directed() and not algo_directed:
        orig_edge_count = G_copy.ecount()
        G_copy.to_undirected(combine_edges={'weight':sum})
        alterations.append('undirected')
        edges_removed = orig_edge_count - G_copy.ecount()
        print("\t[Info - ", descript, "] Converted directed to undirected: ", edges_removed, " edges collapsed of ", orig_edge_count)

    #if the algo is simple but the data is not, then we have to make the data simple
    if  algo_simple and not G.is_simple():
        orig_edge_count = G_copy.ecount()
        G_copy.simplify(combine_edges={'weight':sum})
        alterations.append('simple')
        edges_removed = orig_edge_count - G_copy.ecount()
        print("\t[Info - ", descript, "] Simplifying multigraph: ", edges_removed, " edges collapsed of ", orig_edge_count)


    #safety check: let user know if Graph is close to complete
    #we consider 80% of num complete edges as close to complete
    complete_edges = G_copy.vcount()*(G.vcount()-1)/2

    if complete_edges *.8 < G_copy.ecount():
        print("\t[WARNING: ",descript,"] Graph is nearly complete")
        #we only prune graphs that do not use weights
        if not algo_uses_weights:
            orig_edge_count = G_copy.ecount()
            databot.prune(G_copy)
            alterations.append('pruned')
            num_pruned = orig_edge_count - G_copy.ecount()
            print("\t[Info - ", descript,"] Pruned ", num_pruned," of ", orig_edge_count," edges")

    num_components =  len(G_copy.components(mode=igraph.WEAK))

    if num_components is not 1:
        print("\t[WARNING: ", descript, "] graph has become disconnected with ", num_components, " components.")

    return G_copy, "weight", alterations


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

def comm_infomap(G, databot, descript):
    G, weights, alterations  = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_infomap, G, edge_weights=weights, vertex_weights=None)

def comm_fastgreedy(G, databot, descript):
    G, weights, alterations  = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_fastgreedy, G, weights=weights)

def comm_edge_betweenness(G, databot, descript):
    #edge betweenness does support undirected and directed, so just say that the algo_directed is the
    #same as the data being passed to it
    G, weights, alterations  = cleanup(G, databot, descript, algo_directed=G.is_directed(), algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_edge_betweenness, G, G.is_directed(), weights)

def comm_leading_eigenvector(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_leading_eigenvector, G, weights=weights)

def comm_multilevel(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_multilevel, G,  weights=weights)

def comm_label_propagation(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_label_propagation, G, weights=weights)

def comm_walktrap(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_walktrap, G, weights=weights)

def comm_spinglass(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=True)
    return alterations, partial(igraph.Graph.community_spinglass, G, weights=weights)

def comm_conga(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return alterations, partial(circulo.algorithms.conga.conga, G)

def comm_congo(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return  alterations, partial(circulo.algorithms.congo.congo, G)

def comm_radicchi_strong(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return alterations, partial(circulo.algorithms.radicchi.radicchi,G,'strong')

def comm_radicchi_weak(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return alterations, partial(circulo.algorithms.radicchi.radicchi,G,'weak')

def comm_bigclam(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    ctx = databot.get_context()
    num_comms =  ctx[CirculoData.CONTEXT_OPTIMAL_PARTITIONS] if CirculoData.CONTEXT_OPTIMAL_PARTITIONS in ctx.keys() else 100

    min_comms = int(num_comms * .8)
    max_comms = int(num_comms * 1.2)

    return alterations, partial(circulo.algorithms.snap_bigclam.bigclam, G, detect_comm=num_comms, min_comm=min_comms, max_comm=max_comms)

def comm_coda(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return alterations, partial(circulo.algorithms.snap_coda.coda, G)

def comm_clauset_newman_moore(G, databot, descript):
    G, weights, alterations = cleanup(G, databot, descript, algo_directed=False, algo_simple=True, algo_uses_weights=False)
    return alterations, partial(circulo.algorithms.snap_cnm.clauset_newman_moore, G)
