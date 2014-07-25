from functools import partial
import igraph 
import circulo.algorithms
import circulo.algorithms.radicchi

def comm_infomap(data_mod) :
    G = data_mod.get_graph()
    edge_weight = 'weight' if G.is_weighted() else None
    vertex_weight = None
    rv = partial(igraph.Graph.community_infomap, G, edge_weight, vertex_weight)
    stochastic = True
    return rv, stochastic

def comm_fastgreedy(data_mod):
    G = data_mod.get_graph()
    if G.is_directed():
        print('Graph is directed, converting to undirected')
        G.to_undirected()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_fastgreedy, G, weights=weight_attribute)
    stochastic = True
    return rv, stochastic

def comm_edge_betweenness(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_edge_betweenness, G, directed=G.is_directed(), weights=weight_attribute)
    stochastic = False 
    return rv, stochastic

def comm_leading_eigenvector(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_leading_eigenvector, G, weights=weight_attribute)
    stochastic = True
    return rv, stochastic

def comm_multilevel(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_multilevel, G, weights=weight_attribute)
    stochastic = True
    return rv, stochastic

def comm_label_propagation(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_label_propagation, G, weights=weight_attribute)
    stochastic = True
    return rv,stochastic 

def comm_walktrap(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_walktrap, G, weights=weight_attribute)
    stochastic = True
    return rv,stochastic

def comm_spinglass(data_mod):
    G = data_mod.get_graph()
    weight_attribute = 'weight' if G.is_weighted() else None
    rv = partial(igraph.Graph.community_spinglass, G, weights=weight_attribute)
    stochastic = True
    return rv,stochastic

def comm_conga(data_mod):
    G = data_mod.get_graph()
    rv = partial(circulo.algorithms.conga.CONGA, G) 
    stochastic = False
    return rv,stochastic

def comm_congo(data_mod):
    G = data_mod.get_graph()
    rv = partial(circulo.algorithms.congo.CONGO, G) 
    stochastic = False
    return rv,stochastic

def comm_radicchi_strong(data_mod):
    G = data_mod.get_graph()
    rv = partial(circulo.algorithms.radicchi.radicchi,G,'strong')
    stochastic = False 
    return rv,stochastic

def comm_radicchi_weak(data_mod):
    G = data_mod.get_graph()
    rv = partial(circulo.algorithms.radicchi.radicchi,G,'weak')
    stochastic = False
    return rv,stochastic

    
def comm_groundtruth(data_mod):
    G = data_mod.get_graph()
    rv = partial(data_mod.get_ground_truth,G)
    stochastic = False 
    return rv,stochastic

