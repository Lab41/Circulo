# Goal is to annotate a vertex cover with dictionary representing various cluster metrics
from igraph import Cover, VertexCover
from scipy import nansum, nanmax
import uuid

def __get_weight_attr(G, name, weights):
    if isinstance(weights, str):
      return (weights, False)
    elif weights is not None:
      attr_name = uuid.uuid5(uuid.NAMESPACE_DNS, '{}.circulo.lab41'.format(name))
      G.es[attr_name] = weights
      return (attr_name, True)
    return (None, False)

def __remove_weight_attr(G, attr_name, remove):
    if remove:
      del G.es[uid]

def __weighted_sum(external_edges, w_attr):
  return len(external_edges) if w_attr is None else sum([ e[w_attr] for e in external_edges ])

def fomd(cover, weights=None):
    '''
    Fraction over median (weighted) degree is the number of nodes that have an internal (weighted) degree greater than the median (weighted) degree of
    all nodes in the graph.
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'fomd', weights)

    import scipy
    median = scipy.median(cover.graph.strength(weights=w_attr))
    rv = []
    for subgraph in cover.subgraphs():
        rv += [sum(1.0 for v in subgraph.strength(weights=w_attr) if v > median)/subgraph.vcount()]

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv

def expansion(cover, weights=None):
    '''
    Expansion is the ratio between the (weighted) number of external (boundary) edges in a cluster and the number of nodes in the cluster.
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'expansion', weights)

    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        size_i = cover.size(i)
        rv += [1.0*__weighted_sum(external_edges[i], w_attr)/size_i]

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv

def cut_ratio(cover):
    '''
    Cut ratio is the ratio between the number of external (boundary) edges in a cluster and the cluster's maximum possible number of external edges
    '''
    rv = []
    external_edges = cover.external_edges()
    size_g = cover.graph.vcount()
    for i in range(len(cover)):
        size_i = cover.size(i)
        denominator = (size_i*(size_g-size_i))
        rv += [1.0*len(external_edges[i])/denominator if denominator > 0 else float('nan')]
    return rv

def conductance(cover, weights=None):
    '''
    Conductance is the ratio between the (weighted) number of external (boundary) edges in a cluster and the cluster's total (weighted) number of edges
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'conductance', weights)

    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = __weighted_sum(cover.subgraph(i).es(), w_attr)
        ext_edges_cnt = __weighted_sum(external_edges[i], w_attr)
        denominator = (2.0*int_edges_cnt+ext_edges_cnt)
        rv += [ext_edges_cnt/denominator if denominator > 0 else float('nan')]

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv

def separability(cover, weights=None):
    '''
    Separability is the ratio between the (weighted) number of internal edges in a cluster and its (weighted) number of external (boundary) edges.
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'separability', weights)

    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = __weighted_sum(cover.subgraph(i).es(), w_attr)
        ext_edges_cnt = __weighted_sum(external_edges[i], w_attr)
        rv += [1.0*int_edges_cnt/ext_edges_cnt if ext_edges_cnt > 0 else float('nan')]

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv


def normalized_cut(cover, weights=None):
    '''
    Normalized cut is the sum of (weighted) conductance with the fraction of the (weighted) number of external edges over (weighted) number of all non-cluster edges
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'normalized_cut', weights)

    rv = cover.conductance(weights)
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = __weighted_sum(cover.subgraph(i).es(), w_attr)
        ext_edges_cnt = __weighted_sum(external_edges[i], w_attr)
        tot_edge_cnt = __weighted_sum(cover.graph.es(), w_attr)
        denominator = (2.0*(tot_edge_cnt - int_edges_cnt)+ext_edges_cnt)
        rv[i] += ext_edges_cnt/denominator if denominator > 0 else float('nan')

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv

def maximum_out_degree_fraction(cover, weights=None):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges
    and its internal edges. Maximum ODF returns the maximum fraction for the cluster.
    '''
    odf = out_degree_fraction(cover, weights=weights)
    return [ nanmax(ratios) for ratios in odf ]

def average_out_degree_fraction(cover, weights=None):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges
    and its internal edges. Average ODF returns the average fraction for the cluster.
    '''
    rv = []
    odf = out_degree_fraction(cover, weights)
    for i in range(len(cover)):
      ratios = odf[i]
      rv += [ nansum(ratios)/cover.subgraph(i).vcount() ]
    return rv

def flake_out_degree_fraction(cover, weights=None):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges
    and its internal edges. Flake ODF returns the number of nodes for which this ratio is less than 1, i.e. a node has fewer internal edges than external ones.
    '''
    rv = []
    odf = out_degree_fraction(cover, weights)
    for i in range(len(cover)):
        flake = [ ratio > 1/2.0 for ratio in odf[i] ]
        rv += [sum(flake)/cover.subgraph(i).vcount()]
    return rv

def out_degree_fraction(cover, weights=None):
    '''
    Out Degree Fraction (ODF) of a node in a cluster is the ratio between its number of external (boundary) edges
    and its internal edges.
    '''
    w_attr, remove = __get_weight_attr(cover.graph, 'out_degree_fraction', weights)

    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.strength(weights=w_attr)
        for edge in external_edges[i]:
            node_index = edge.source if i in cover.membership[edge.source] else edge.target
            ext_edge_per_node[node_index] += 1.0 if weights is None else edge[w_attr]
        ratios = []
        for pair in zip(ext_edge_per_node, degree_per_node):
             ratios += [ pair[0]/pair[1] if pair[1] != 0 else float('nan') ]
        rv += [ratios]

    __remove_weight_attr(cover.graph, w_attr, remove)
    return rv

def external_edges(cover) :
    '''
    @param cover a VertexCover object.
    @returns an array of external edges per cluster in the cover.
    '''
    array_of_sets = [ [] for v in cover ]
    #Iterate over crossing edges
    for edge in [ a[1] for a in zip(cover.crossing(), cover.graph.es()) if a[0]]:
        membership = [cover.membership[edge.source]]
        if not cover.graph.is_directed():
            membership += [cover.membership[edge.target]]

        for node_membership in membership:
            for cluster_id in node_membership:
                array_of_sets[cluster_id] += [edge]

    return array_of_sets

def compute_metrics(cover, weights=None):
   cover.metrics = {
            'Fraction over a Median Degree' : fomd(cover, weights),
            'Expansion'                     : expansion(cover, weights),
            'Cut Ratio'                     : cut_ratio(cover),
            'Conductance'                   : conductance(cover, weights),
            'Normalized Cut'                : normalized_cut(cover, weights),
            'Maximum Out Degree Fraction'   : maximum_out_degree_fraction(cover, weights),
            'Average Out Degree Fraction'   : average_out_degree_fraction(cover, weights),
            'Flake Out Degree Fraction'     : flake_out_degree_fraction(cover, weights),
            'Separability'                  : separability(cover, weights),
            'Subgraphs'                     : []
            }

   for i in range(len(cover)):
        sg = cover.subgraph(i)
        sg.compute_metrics(refresh=False)
        cover.metrics['Subgraphs'] += [sg.metrics]


def print_metrics(cover):

    if cover.metrics == None:
        if cover.graph.is_weighted():
            cover.compute_metrics(weights="weight")
        else:
            cover.compute_metrics()

    key_print_buffer = 40

    for cover_id in range(len(cover)):
        print("\n\nCover {}".format(cover_id))
        for k,v in cover.metrics.items():
            num_dots = key_print_buffer - len(k)
            dot_str = '.' * num_dots
            if(k != "Subgraphs"):
                print("{}{}{}".format(k, dot_str,v[cover_id]))
            else:
                print("Subgraph_____")
                #for k,v in v.items():
                #    print("{}...".format(k))
                for i in v:
                    print(i)

Cover.fraction_over_median_degree = fomd
VertexCover.metrics = None
VertexCover.print_metrics = print_metrics
VertexCover.compute_metrics = compute_metrics
VertexCover.external_edges = external_edges
VertexCover.expansion = expansion
VertexCover.cut_ratio = cut_ratio
VertexCover.conductance = conductance
VertexCover.normalized_cut = normalized_cut
VertexCover._out_degree_fraction = out_degree_fraction
VertexCover.maximum_out_degree_fraction = maximum_out_degree_fraction
VertexCover.average_out_degree_fraction = average_out_degree_fraction
VertexCover.flake_out_degree_fraction = flake_out_degree_fraction
VertexCover.separability = separability
