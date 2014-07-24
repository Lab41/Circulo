# Goal is to annotate a vertex cover with dictionary representing various cluster metrics 
from igraph import Cover 
from scipy import nansum

def fomd(subgraph, degree_stats_dict):
    '''
    Fraction of nodes of subgraph that have internal degree higher than the median degree value of entire set of graph nodes
    '''
    median = degree_stats_dict['Median']

    return sum(1.0 for v in subgraph.degree() if v > median)/subgraph.vcount()


def generic(cover, operator):
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        rv += [operator(i, external_edges[i], cover)]
    return rv

def expansion(cover):
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        size_i = cover.size(i)
        rv += [1.0*len(external_edges[i])/size_i]
    return rv

def cut_ratio(cover):
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        size_i = cover.size(i)
        size_g = cover.graph.vcount()
        rv += [1.0*len(external_edges[i])/(size_i*(size_g-size_i))]
    return rv

def conductance(cover):
    rv = []
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = cover.subgraph(i).ecount()
        ext_edges_cnt = len(external_edges[i])
        rv += [ext_edges_cnt/(2*int_edges_cnt+ext_edges_cnt)]
    return rv

def normalized_cut(cover):
    rv = cover.conductance()
    external_edges = cover.external_edges()
    for i in range(len(cover)):
        int_edges_cnt = cover.subgraph(i).ecount()
        ext_edges_cnt = len(external_edges[i])
        tot_edge_cnt = cover.graph.ecount()
        rv[i] += ext_edges_cnt/(2*(tot_edge_cnt - int_edges_cnt)+ext_edges_cnt)

    return rv

def maximum_out_degree_fraction(cover):
    rv = []
    external_edges = cover.external_edges()
    val = 1.0 if cover.graph.is_directed() else .5;
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            ext_edge_per_node[edge.source] += val
            if not cover.graph.is_directed():
                ext_edge_per_node[edge.target] += val
        ratios = []
        for pair in zip(ext_edge_per_node, degree_per_node):
            ratios += [ pair[0]/pair[1] if pair[1] != 0 else float('nan') ]
        rv += [max(ratios)]
    return rv

def average_out_degree_fraction(cover):
    rv = []
    external_edges = cover.external_edges()
    val = 1.0 if cover.graph.is_directed() else .5;
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            ext_edge_per_node[edge.source] += val
            if not cover.graph.is_directed():
                ext_edge_per_node[edge.target] += val
        ratios = []
        for pair in zip(ext_edge_per_node, degree_per_node):
            ratios += [ pair[0]/pair[1] if pair[1] != 0 else float('nan') ]
        rv += [nansum(ratios)/cover.subgraph(i).vcount()]
    return rv

def flake_out_degree_fraction(cover):
    rv = []
    external_edges = cover.external_edges()
    val = 1.0 if cover.graph.is_directed() else .5;
    for i in range(len(cover)):
        ext_edge_per_node = [0]*cover.graph.vcount()
        degree_per_node = cover.graph.degree()
        for edge in external_edges[i]:
            ext_edge_per_node[edge.source] += val
            if not cover.graph.is_directed():
                ext_edge_per_node[edge.target] += val
        flake = []
        for pair in zip(ext_edge_per_node, degree_per_node):
            flake += [ pair[0] > pair[1]/2.0 ]
        rv += [sum(flake)/cover.subgraph(i).vcount()]
 
    return rv

def external_edges(cover) :
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


def get_cluster_metrics(cover, cluster_id):
    cover.graph.compute_metrics(refresh=False)
    external_edges = cover.external_edges()[cluster_id]
    g_metrics = cover.graph.metrics

    subgraph = cover.subgraph(cluster_id)
    subgraph.compute_metrics()

    metrics = { 
            'Fraction over a Median Degree' : fomd(subgraph, g_metrics['Degree Statistics']),
            'Triangle Participation Ratio'  : None,                
            'Expansion'                     : None,
            'Cut Ratio'                     : None,    
            'Conductance'                   : None,    
            'Normalized Cut'                : None,     
            'Out Degree Frac'               : None, 
            'Separability'                  : None 
    }

    return metrics

def compute_metrics(cover):
    cover.graph.compute_metrics(refresh=False)
    g_metrics = cover.graph.metrics
    cover.metrics = { 
            'Fraction over a Median Degree' : [fomd(cover.subgraph(i), g_metrics['Degree Statistics']) for i in range(len(cover))],
            'Expansion'                     : expansion(cover),
            'Cut Ratio'                     : cut_ratio(cover),    
            'Conductance'                   : conductance(cover),    
            'Normalized Cut'                : normalized_cut(cover),     
            'Maximum Out Degree Fraction'   : maximum_out_degree_fraction(cover), 
            'Average Out Degree Fraction'   : average_out_degree_fraction(cover),
            'Flake Out Degree Fraction'     : flake_out_degree_fraction(cover),
            'Separability'                  : [],
            'Subgraphs'                     : []
            }

    for i in range(len(cover)):
        sg = cover.subgraph(i)
        sg.compute_metrics(refresh=False)
        cover.metrics['Subgraphs'] += [sg.metrics]


Cover.metrics = None
Cover.compute_metrics = compute_metrics
Cover.external_edges = external_edges
Cover.expansion = expansion
Cover.cut_ratio = cut_ratio
Cover.conductance = conductance
Cover.normalized_cut = normalized_cut
Cover.maximum_out_degree_fraction = maximum_out_degree_fraction
Cover.average_out_degree_fraction = average_out_degree_fraction
Cover.flake_out_degree_fraction = flake_out_degree_fraction
