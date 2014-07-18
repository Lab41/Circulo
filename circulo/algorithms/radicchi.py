import sys
import igraph as ig
import itertools

def radicchi_wrapper(G, measure='weak'):
    """ Wrapper for execution of the Radicchi community-detection algorithm. Returns 
    covers of the graph, with metadata representing provenance - in essence, a "dendrogram"
    that represents splits into communities. """
    g = G.copy()
    g.vs['id'] = list(range(g.vcount()))

    result = radicchi(G, g, 0, measure=measure)

    clustering = [0] * G.vcount()
    for i,l in enumerate(result):
        for v in l:
            clustering[v] = i

    return ig.VertexClustering(G, clustering)

def radicchi(G, g, level, measure='strong'):
    """
    Uses the Radicchi et al. algorithm to find the communities in a graph. Returns a list of the splits in the graph.
    """
    # Caching some global graph information and updating it manually. Because igraph
    # tends to recalculate this stuff on the whole graph every time, 
    # storing it and manipulating only the parts that change will make things faster.

    print(("  " * level) + "------------------")
    print(("  " * level) + "At level %s" % level)

    edge_clustering_coefficient = edge_clustering_coefficient_3 if (measure == 'strong') else edge_clustering_coefficient_4

    communities = []
    while True:
        if g.ecount() == 0:
            break

        min_edge = None; min_ecc = None
        for e in g.es:
            edge = e.tuple
            ecc = edge_clustering_coefficient(g, edge[0], edge[1])
            if not min_edge or ecc < min_ecc:
                min_edge = edge
                min_ecc = ecc

        g.delete_edges([min_edge])
        u, v = min_edge

        print(("  " * level) + "Removing (%s, %s)" % (g.vs['label'][u], g.vs['label'][v]))
        
        if g.edge_connectivity(source=u, target=v) == 0:
            # print("Graph has split")
            # print(g.components())

            result = prune_components(G, g, community_measure=measure)
            if result['pruned']:
                orig_communities = result['orig_communities']
                new_communities = result['new_communities']
                remaining = result['remaining']

                for i,c in enumerate(new_communities):
                    community_labels = [g.vs['label'][j] for j in c] 
                    print(("  " * level) + "Found a community: %s" % orig_communities[i])
                    print(("  " * level) + "Community names: %s" % community_labels)
                    # print(("  " * level) + "Leaving level %s" % level)
                    s = g.subgraph(c)
                    subcommunities = radicchi(G, s, level+1, measure)
                    if(len(subcommunities) == 0):
                        communities.append(orig_communities[i])
                    else:
                        communities.extend(subcommunities)

                    # print(("  " * level) + "Back to level %s" % level)

                orig_remaining = [g.vs['id'][i] for i in remaining]
                remaining_labels = [g.vs['label'][i] for i in remaining] 
                print(("  " * level) + "Working with remainder: %s" % orig_remaining)
                print(("  " * level) + "Remainder names: %s" % remaining_labels)
                r = g.subgraph(remaining)
                subcommunities = radicchi(G, r, level+1, measure)
                clustered = sum(subcommunities, [])

                isolated_remaining = [i for i in orig_remaining if i not in clustered]
                print(("  " * level) + "Found isolates: %s" % isolated_remaining)
                communities.extend([[i] for i in isolated_remaining])

                break

    print(("  " * level) + "Done with level %s" % level)
    print(("  " * level) + "------------------")

    return communities

def prune_components(orig, new, community_measure='strong'):
    """ Uses the given community measure to prune connected components in the graph new that
        represent communities in the graph orig, using the given community measure.  """
    components = new.components()
    ids = new.vs['id']

    new_components = [c for c in components]
    orig_components = [[ids[v] for v in component] for component in new_components]

    is_community = is_strong_community if (community_measure=='strong') else is_weak_community
    community_indices = [i for i, component in enumerate(orig_components) if is_community(orig, component)]

    orig_communities = [orig_components[i] for i in community_indices]
    new_communities = [new_components[i] for i in community_indices]

    result_pruned = False
    result_remaining_nodes = None
    result_orig_communities = None
    result_new_communities = None
    if len(community_indices) > 1:
        all_new_community_nodes = sum(new_communities, [])
        all_new_nodes = range(new.vcount())
        all_new_remaining_nodes = list(set(all_new_nodes) - set(all_new_community_nodes))

        result_pruned = True
        result_remaining_nodes = all_new_remaining_nodes
        result_new_communities = new_communities
        result_orig_communities = orig_communities

    return {"pruned": result_pruned, "orig_communities": result_orig_communities, 
            "new_communities": result_new_communities, "remaining": result_remaining_nodes}

def is_strong_community(G, nodes):
    """
    Checks whether the provided set of nodes form a strong community in the graph G.
    """
    # precondition: nodes must be sorted
    subgraph = G.subgraph(nodes)
    degree = G.degree(nodes)
    community_degree = subgraph.degree()
    for i in range(len(nodes)):
        if community_degree[i] <= (degree[i] - community_degree[i]):
            return False

    return True

def is_weak_community(G, nodes):
    """
    Checks whether the provided set of nodes form a weak community in the graph G.
    """
    # precondition: nodes must be sorted
    subgraph = G.subgraph(nodes)
    degree = G.degree(nodes)
    indegree = subgraph.degree()
    tsum = sum(degree)
    insum = sum(indegree)
    outsum = tsum - insum

    return insum > outsum

def edge_clustering_coefficient_3(G, u, v):
    """
    Computes the "edge clustering coefficient" of the given edge, defined as the number of triangles
    in which it participates compared to the maximum number of triangles of which it could be a part.
    """
    udeg = G.degree(u)
    vdeg = G.degree(v)
    mdeg = min(udeg-1, vdeg-1)
    if mdeg == 0:
        return float('inf')
    else:
        cdeg = len(set(G.neighbors(u)) & set(G.neighbors(v)))
        return (cdeg + 1.0) / mdeg

def edge_clustering_coefficient_4(G, u, v):
    """
    Computes a modified form of the edge clustering coefficient using squares instead of triangles.
    """
    udeg = G.degree(u)
    vdeg = G.degree(v)
    mdeg = min(udeg-1, vdeg-1)
    if mdeg == 0:
        return float('inf')
    else:
        uneighbors = G.neighbors(u)
        vneighbors = set(G.neighbors(v))

        num_squares = 0
        for w in uneighbors:
            if w == v:
                continue
            wneighbors = G.neighbors(w)
            for x in wneighbors:
                if x != u and x in vneighbors:
                    num_squares += 1
        
        return (num_squares + 1.0) / mdeg

def main(argv):
    g = ig.Graph.Read_GML('netscience.gml')
    communities = radicchi_wrapper(g)
    print(communities)
    return communities

if __name__ == "__main__":
    main(sys.argv[1:])
