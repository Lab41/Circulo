from functools import partial
import igraph
import circulo.algorithms
import statistics

from circulo.data.databot import CirculoData


def fix_graph(G, prune, fix_type, descript):

    G_copy = G.copy()

    if not G_copy.is_weighted():
        G_copy.es()['weight'] = 1

    if fix_type == "to_undirected":
        G_copy.to_undirected(combine_edges={'weight':sum})
    elif fix_type == "to_simple":
        G_copy.simplify(combine_edges={'weight':sum})


    #TODO: some algos might be able to leverage the weights, meaning we won't need to prune
    #for now, just go ahead an prune if collapsed


    prune(G_copy)
    num_pruned = G.ecount() - G_copy.ecount()
    print("\t[Info - ", descript,"] Pruned ", num_pruned," of ",G.ecount()," edges")

    #safety check: let user know if Graph is close to complete
    #we consider 80% of num complete edges as close to complete
    complete_edges = G_copy.vcount()*(G_copy.vcount()-1)/2
    if complete_edges *.8 < G_copy.ecount():
            print("\t[WARNING: ",descript,"] Collapsed graph is nearly complete")

    num_components =  len(G_copy.components(mode=igraph.WEAK))

    if num_components is not 1:
        print("\t[WARNING: ", descript, "] graph has become disconnected with ", num_components, " components.")


    return G_copy




def cleanup(G, databot, descript, algo_directed, algo_simple):
    '''
    GRAPH Cleaning: Sometimes the graphs need to be cleaned for certain type of algorithms.
    The idea here is that we are trying to best match the data to what the algorithm can do.
    We start with specific matches and work our way to more general.
    '''

    #first we check if algo and data have same directedness and type.
    if G.is_directed() == algo_directed and G.is_simple() == algo_simple:
        weight_attr =  "weight" if G.is_weighted() else None
        return G, weight_attr

    if algo_directed and not G.is_directed():
        print("\t[Info - ", descript, "] - Warning: Passing undirected graph to directed algo")

    #if the graph is directed and algo is not directed, we make the graph undirected
    if G.is_directed() and not algo_directed:
        print('\t[Info - ',descript,'] Converting graph to undirected (summing edge weights)')
        G = fix_graph(G, databot.prune, fix_type="to_undirected", descript=descript)

    #if the algo is simple but the data is not, then we have to make the data simple
    elif  algo_simple and not G.is_simple():
        print('\t[Info - ',descript,'] Collapsed multigraph edges (summing edge weights)')
        G = fix_graph(G, databot.prune, fix_type="to_simple", descript=descript)


    #we could do this outside the function, but it makes it cleaner this way
    weights_attr = "weight" if G.is_weighted() else None

    return G, weights_attr


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
    G, weights  = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_infomap, G, edge_weights=weights, vertex_weights=None)

def comm_fastgreedy(G, databot, descript):
    G, weights  = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_fastgreedy, G, weights=weights)

def comm_edge_betweenness(G, databot, descript):
    G, weights  = cleanup(G, databot, descript, algo_directed=True, algo_simple=True)
    return partial(igraph.Graph.community_edge_betweenness, G, G.is_directed(), weights)

def comm_leading_eigenvector(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_leading_eigenvector, G, weights=weights)

def comm_multilevel(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_multilevel, G,  weights=weights)

def comm_label_propagation(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_label_propagation, G, weights=weights)

def comm_walktrap(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_walktrap, G, weights=weights)

def comm_spinglass(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(igraph.Graph.community_spinglass, G, weights=weights)

def comm_conga(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.conga.conga, G)

def comm_congo(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return  partial(circulo.algorithms.congo.congo, G)

def comm_radicchi_strong(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'strong')

def comm_radicchi_weak(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.radicchi.radicchi,G,'weak')

def comm_bigclam(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    ctx = databot.get_context()
    num_comms =  ctx[CirculoData.CONTEXT_OPTIMAL_PARTITIONS] if CirculoData.CONTEXT_OPTIMAL_PARTITIONS in ctx.keys() else 100

    min_comms = int(num_comms * .8)
    max_comms = int(num_comms * 1.2)

    return partial(circulo.algorithms.snap_bigclam.bigclam, G, detect_comm=num_comms, min_comm=min_comms, max_comm=max_comms)

def comm_coda(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_coda.coda, G)

def comm_clauset_newman_moore(G, databot, descript):
    G, weights = cleanup(G, databot, descript, algo_directed=False, algo_simple=True)
    return partial(circulo.algorithms.snap_cnm.clauset_newman_moore, G)
