from functools import partial
import igraph
import circulo.algorithms

def edge_cleanup(ctx, descript):
    '''
        Converting a directed, and potentially multigraph, graph to an undirected graph, can result in a loss of
        precision; therefore, you must be careful when doing conversion. For now we have to make certain assumptions about
        how certain edge attributes are combined.  We are currently summing the weights of mulitgraphs and multiple directed edges
    '''

    #this will collapse multiedges and go to undirected
    if ctx['directed']:
        print('\t[Info - ',descript,'] Converting graph to undirected (summing edge weights), since algo requires undirected')
        G_copy = ctx['graph'].copy()
        G_copy.to_undirected(combine_edges={'weight':sum})
    #this will just collapse multiedges
    elif not ctx['simple']:
        print('\t[Info - ',descript,'] Collapsed multigraph edges since algo requires it')
        G_copy = ctx['graph'].copy()
        G_copy.simplify(combine_edges={'weight':sum})
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

def comm_infomap(ctx, descript):
    return partial(igraph.Graph.community_infomap, ctx['graph'], edge_weights=ctx['weight'], vertex_weights=None)

def comm_fastgreedy(ctx, descript):
    return partial(igraph.Graph.community_fastgreedy, edge_cleanup(ctx, descript), weights=ctx['weight'])

def comm_edge_betweenness(ctx, descript):
    return partial(igraph.Graph.community_edge_betweenness, ctx['graph'], ctx['directed'], weights=ctx['weight'])

def comm_leading_eigenvector(ctx, descript):
    return partial(igraph.Graph.community_leading_eigenvector, ctx['graph'], weights=ctx['weight'])

def comm_multilevel(ctx, descript):
    return partial(igraph.Graph.community_multilevel, edge_cleanup(ctx, descript),  weights=ctx['weight'])

def comm_label_propagation(ctx, descript):
    return partial(igraph.Graph.community_label_propagation, ctx['graph'], weights=ctx['weight'])

def comm_walktrap(ctx, descript):
    return partial(igraph.Graph.community_walktrap, ctx['graph'], weights=ctx['weight'])

def comm_spinglass(ctx, descript):
    return partial(igraph.Graph.community_spinglass, ctx['graph'], weights=ctx['weight'])

def comm_conga(ctx, descript):
    return partial(circulo.algorithms.conga.conga, edge_cleanup(ctx, descript))

def comm_congo(ctx, descript):
    return  partial(circulo.algorithms.congo.congo, edge_cleanup(ctx, descript))

def comm_radicchi_strong(ctx, descript):
    return partial(circulo.algorithms.radicchi.radicchi,ctx['graph'],'strong')

def comm_radicchi_weak(ctx, descript):
    return partial(circulo.algorithms.radicchi.radicchi,ctx['graph'],'weak')

def comm_bigclam(ctx, descript):
    return partial(circulo.algorithms.snap_bigclam.bigclam, edge_cleanup(ctx, descript))

def comm_coda(ctx, descript):
    return partial(circulo.algorithms.snap_coda.coda, ctx['graph'])

def comm_clauset_newman_moore(ctx, descript):
    return partial(circulo.algorithms.snap_cnm.clauset_newman_moore, ctx['graph'])
