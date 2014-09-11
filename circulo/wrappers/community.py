from functools import partial
import igraph
import circulo.algorithms

def ensure_undirected(ctx):
    if ctx['directed']:
        print('Graph is directed, converting to undirected')
        G_copy = ctx['graph'].copy()
        G_copy.to_undirected()
    else:
        G_copy = ctx['graph']

    return G_copy


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

def comm_infomap(ctx):
    return partial(igraph.Graph.community_infomap, ctx['graph'], edge_weights=ctx['weight'], vertex_weights=None)

def comm_fastgreedy(ctx):
    return partial(igraph.Graph.community_fastgreedy, ensure_undirected(ctx), weights=ctx['weight'])

def comm_edge_betweenness(ctx):
    return partial(igraph.Graph.community_edge_betweenness, ctx['graph'], ctx['directed'], weights=ctx['weight'])

def comm_leading_eigenvector(ctx):
    return partial(igraph.Graph.community_leading_eigenvector, ctx['graph'], weights=ctx['weight'])

def comm_multilevel(ctx):
    return partial(igraph.Graph.community_multilevel, ensure_undirected(ctx['graph'], ctx),  weights=ctx['weight'])

def comm_label_propagation(ctx):
    return partial(igraph.Graph.community_label_propagation, ctx['graph'], weights=ctx['weight'])

def comm_walktrap(ctx):
    return partial(igraph.Graph.community_walktrap, ctx['graph'], weights=ctx['weight'])

def comm_spinglass(ctx):
    return partial(igraph.Graph.community_spinglass, ctx['graph'], weights=ctx['weight'])

def comm_conga(ctx):
    return partial(circulo.algorithms.conga.conga, ensure_undirected(ctx))

def comm_congo(ctx):
    return  partial(circulo.algorithms.congo.congo, ensure_undirected(ctx))

def comm_radicchi_strong(ctx):
    return partial(circulo.algorithms.radicchi.radicchi,ctx['graph'],'strong')

def comm_radicchi_weak(ctx):
    return partial(circulo.algorithms.radicchi.radicchi,ctx['graph'],'weak')

def comm_bigclam(ctx):
    return partial(circulo.algorithms.snap_bigclam.bigclam, ensure_undirected(ctx))

def comm_coda(ctx):
    return partial(circulo.algorithms.snap_coda.coda, ctx['graph'])

def comm_clauset_newman_moore(ctx):
    return partial(circulo.algorithms.snap_cnm.clauset_newman_moore, ctx['graph'])
