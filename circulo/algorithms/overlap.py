import igraph as ig
import operator
from collections import defaultdict
from time import sleep


#############################
# Fuzzy Modularity Measures #
#############################

def nepusz_modularity(G, cover):
    raise NotImplementedError("See the CONGA 2010 paper")

def zhang_modularity(G, cover):
    raise NotImplementedError("""See 'Identification of overlapping community structure in
        complex networks using fuzzy C-means clustering'""")

def nicosia_modularity(G, cover):
    raise NotImplementedError("""See 'Extending the definition of
        modularity to directed graphs with overlapping communities'""")


#############################
# Crisp modularity measures #
#############################

def count_communities(G, cover):
    """
    Helper for lazar_modularity.

    Returns a dict {v:count} where v is a vertex id and
    count is the number of different communities it is
    assigned to.
    """
    counts = {i.index : 0 for i in G.vs}
    for community in cover:
        for v in community:
            counts[v] += 1
    return counts


def get_weights(G):
    """
    Given a graph G, returns a list of weights. If the graph is unweighted,
    returns a list of 1s the same length as the number of edges. 
    """
    try:
        # asssumes weight as an attribute name means graph is weighted.
        weights = G.es['weight']
    except KeyError:
        #unweighted means all weights are 1.
        weights = [1 for e in G.es]
    return weights


def get_single_lazar_modularity(G, community, weights, counts):
    """
    Returns the lazar modularity of a single community.
    """
    totalInternalWeight = sum(weights[G.es[e].index] for e in community) # m_c in paper
    numVerticesInCommunity = len(community) # V_c in paper
    numPossibleInternalEdges = numVerticesInCommunity * (numVerticesInCommunity - 1) / 2
    if numPossibleInternalEdges == 0: return 0
    edgeDensity = totalInternalWeight / numPossibleInternalEdges / numVerticesInCommunity
    interVsIntra = 0
    comm = set(community)
    for v in community:
        interVsIntraInternal = 0
        neighbors = G.neighbors(v)
        degree = len(neighbors) # k_i in paper
        numCommunitiesWithin = counts[v] # s_i in paper
        for n in neighbors:
            weight = weights[G.get_eid(v, n)]
            if n in comm:
                interVsIntraInternal += weight
            else:
                interVsIntraInternal -= weight
        interVsIntraInternal /= (degree * numCommunitiesWithin)
        interVsIntra += interVsIntraInternal
    return edgeDensity * interVsIntra


def lazar_modularity(G, cover):
    """
    Returns the crisp modularity measure as defined by Lazar et al. 2009

    Defined as the average edge density times normalized difference
    between inter and intracommunity edges for each community.

    See CONGA 2010 or Lazar's paper for a precise definition.
    """
    numCommunities = len(cover) # |C| in the paper
    totalModularity = 0 # M_c in the paper
    weights = get_weights(G)
    counts = count_communities(G, cover)
    for c in cover:
        totalModularity += get_single_lazar_modularity(G, c, weights, counts)
    averageModularity = 1/numCommunities * totalModularity #  M in the paper
    return averageModularity


##################################
# Classes for overlapping covers #
##################################

class CrispOverlap(object):
    """
    TODO
    """
    def __init__(self, graph, covers, modularities=None, optimal_count=None, modularity_measure="lazar"):
        """
        Initializes a CrispOverlap object with the given parameters.

            Graph: The graph to which the object refers
            covers: a dict of VertexCovers, also referring to this graph, of the form {k : v}
                where k is the number of clusters and v is the vertexCluste
            modularities (optional): a dict of modularities of the form {c:m} where c is
                the number of clusters and m is the modularity.
            optimal_count (optional): A hint for the number of clusters to use.
            modularity_measure (optional): The name of the modularity function to use.
                Right now, the only choice is "lazar."
        """
        # Possibly figure out a better data structure like a merge
        # list that contains all information needed?

        # So far only know of Lazar's measure for crisp overlapping.
        self._measureDict = {"lazar" : lazar_modularity}
        self._covers = covers
        self._graph = graph
        self._optimal_count = optimal_count
        self._modularities = modularities
        if modularity_measure in self._measureDict:
            self._modularity_measure = modularity_measure
        else: raise KeyError("Modularity measure not found.")


    def __getitem__(self, numClusters):
        """
        Returns the cover with the given number of clusters.
        """
        if not numClusters:
            raise KeyError("Number of clusters must be a positive integer.")
        return self._covers[numClusters]

    def __iter__(self):
        """
        Iterates over the covers in the list.
        """
        return (v for v in list(self._covers.values()))


    def __len__(self):
        """
        Returns the number of covers in the list.
        """
        return len(self._covers)

    def __bool__(self):
        """
        Returns True when there is at least one cover in the list.
        """
        return bool(self._covers)


    def __str__(self):
        """
        Returns a string representation of the list of covers.
        """
        return '{0} vertices in {1} possible covers.'.format(len(self._graph.vs), len(self._covers))


    def as_cover(self):
        """
        Returns the optimal cover (by modularity) from the object.
        """
        return self._covers[self.optimal_count]


    def change_modularity_measure(measure, recalculate=True):
        """
        Given measure, the name of a new modularity measure, switches
        the modularity function used. If recalculate=True, also recalculates
        the modularities and optimal count.

        Note: currently useless, as there is only one available measure.
        """
        if measure in self._measureDict:
            self._modularity_measure = measure
        else: raise KeyError("Modularity measure not found.")
        if recalculate:
            self.recalculate_modularities()

    def recalculate_modularities(self):
        """
        Recalculates the modularities and optimal count using the modularity_measure.
        """
        modDict = {}
        for cover in self._covers.values():
            modDict[len(cover)] = self._measureDict[self._modularity_measure](self._graph, cover)
        self._modularities = modDict
        self._optimal_count = max(iter(self._modularities.items()), key=operator.itemgetter(1))[0]
        return self._modularities


    @property
    def modularities(self):
        """
        Returns the a dict {c : m} where c is the number of clusters
        in the cover and m is the modularity. If modularity has not
        been calculated, it recalculates it for all covers. Otherwise,
        it returns the stored dict.

        Note: Call recalculate_modularities to recalculate the modularity.
        """
        if self._modularities:
            return self._modularities
        self._modularities = self.recalculate_modularities()
        return self._modularities


    @property
    def optimal_count(self):
        """Returns the optimal number of clusters for this dendrogram.

        If an optimal count hint was given at construction time and
        recalculate_modularities has not been called, this property simply returns the
        hint. If such a count was not given, this method calculates the optimal cover
        by maximizing the modularity along all possible covers in the object.

        Note: Call recalculate_modularities to recalculate the optimal count.
        """
        if self._optimal_count is not None:
            return self._optimal_count
        else:
            modularities = self.modularities
            self._optimal_count = max(list(modularities.items()), key=operator.itemgetter(1))[0]
            return self._optimal_count


    def pretty_print_cover(self, numClusters, label='CONGA_index'):
        """
        Takes a cover in vertex-id form and prints it nicely
        using label as each vertex's name.
        """
        cover = self._covers[numClusters]
        #if label == 'CONGA_index':
        pp = [self._graph.vs[num] for num in [cluster for cluster in cover]]
        #else: 
        #    pp = [G.vs[num][label] for num in [cluster for cluster in cover]]
        for count, comm in enumerate(pp):
            print("Community {0}:".format(count))
            for v in comm:
                print('\t {0}'.format(v.index if label == 'CONGA_index' else v[label]))
            print()


    def make_fuzzy(self):
        """
        TODO. see CONGA 2010
        """
        pass




# TODO. Other algorithms like FOG return a fuzzy overlapping.

# Nothing below this line has been implemented.
###############################################

class FuzzyOverlap(object):
    """
    TODO
    """
    def __init__(self, graph, coverDict, optimal_count=None, modularity_measure = "nepusz"):
        """
        TODO
        """
        # this repeats a ton of data. figure out a better data structure.
        self._coverDict = coverDict
        self._graph = graph
        self._optimal_count = optimal_count
        if modularity_measure in modularityDict:
            self._modularity_measure = modularity_measure
        else: raise KeyError("Modularity measure not found.")
        self._mod_flag = False
        self.fuzzyDict = {"nepusz" : nepusz_modularity,
                          "zhang": zhang_modularity,
                          "nicosia" : nicosia_modularity}


    @property
    def optimal_count(self):
        """
        TODO
        """
        if self._optimal_count is not None and not mod_flag:
            return self._optimal_count
        else:
            max_mod, max_index = max(enumerate(self.list_modularities))
            mod_flag = False
            return max_index + 1



    def change_modularity_measure(self, new):
        mod_flag = True
        if new in modularityDict:
            self._modularity_measure = new
        else: raise KeyError("Modularity measure not found.")
