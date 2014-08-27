from functools import partial
import igraph
import circulo.algorithms

import circulo.algorithms.radicchi
import circulo.algorithms.conga


def ensure_undirected(G, ctx):
    if ctx['directed']:
        print('Graph is directed, converting to undirected')
        G_copy = G.copy()
        G_copy.to_undirected()
    else:
        G_copy = G

    return G_copy

def comm_infomap(G,ctx):
    return partial(igraph.Graph.community_infomap, G, edge_weights=ctx['weight'], vertex_weights=None), True

def comm_fastgreedy(G, ctx):
    return partial(igraph.Graph.community_fastgreedy, ensure_undirected(G, ctx), weights=ctx['weight']), True

def comm_edge_betweenness(G, ctx):
    return partial(igraph.Graph.community_edge_betweenness, G, ctx['directed'], weights=ctx['weight']), False

def comm_leading_eigenvector(G, ctx):
    return partial(igraph.Graph.community_leading_eigenvector, G, weights=ctx['weight']), True

def comm_multilevel(G, ctx):
    return partial(igraph.Graph.community_multilevel, ensure_undirected(G, ctx),  weights=ctx['weight']), True

def comm_label_propagation(G, ctx):
    return partial(igraph.Graph.community_label_propagation, G, weights=ctx['weight']),    True

def comm_walktrap(G, ctx):
    return partial(igraph.Graph.community_walktrap, G, weights=ctx['weight']), True

def comm_spinglass(G, ctx):
    return partial(igraph.Graph.community_spinglass, G, weights=ctx['weight']), True

def comm_conga(G, ctx):
    return partial(circulo.algorithms.conga.CONGA, G), False

def comm_congo(G, ctx):
    return  partial(circulo.algorithms.congo.CONGO, G), False

def comm_radicchi_strong(G, ctx):
    return partial(circulo.algorithms.radicchi.radicchi,G,'strong'), False

def comm_radicchi_weak(G, ctx):
    return partial(circulo.algorithms.radicchi.radicchi,G,'weak'), False

