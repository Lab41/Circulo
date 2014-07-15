import congo as CONGO
import unittest
import igraph
import itertools

class TestCongoFunctions(unittest.TestCase):

    def setUp(self):
        """
        Initializes the graph for testing to Zachary's
        karate club.
        """
        self.graph = igraph.Graph.Famous("zachary")
        self.graph.vs['CONGA_orig'] = [i.index for i in self.graph.vs]
        self.graph.es['eb'] = 0
        self.graph.vs['pb'] = [{uw : 0 for uw in itertools.combinations(self.graph.neighbors(vertex), 2)} for vertex in self.graph.vs]


    def tearDown(self):
        self.graph = None


    def test_test(self):
        """
        Calculates the edge betweenness twice and checks
        equality. Just making sure the testing framework
        and igraph are working properly.
        """
        eb = self.graph.edge_betweenness()
        self.assertEqual(self.graph.edge_betweenness(), eb)


    def test_edge_betweenness(self):
        """
        Checks that the implementation of edge_betweenness in
        edge_and_pair_betweenness matches that of igraph's
        graph.edge_betweenness.
        """
        ebtheirs = self.graph.edge_betweenness()
        ebmine, _ = CONGO.edge_and_pair_betweenness(self.graph)
        for e in self.graph.es:
            self.assertAlmostEqual(ebtheirs[e.index], ebmine[e.tuple])


    def test_pair_betweenness(self):
        """
        Checks to make sure that the sum of all pair betweennesses
        on a specific vertex are equal to its vertex betweenness.
        """
        _, pb = CONGO.edge_and_pair_betweenness(self.graph)
        vb = self.graph.betweenness()
        for v in pb:
            self.assertAlmostEqual(sum(pb[v].values()), vb[v])


    # def test_vertex_betweeenness_from_eb(self):
    #   """
    #   Checks that the implementation of vertex_betweeenness_from_eb
    #   yields the same results as that of igraph's graph.betweenness
    #   """
    #   eb = self.graph.edge_betweenness()
    #   ebmine, _ = CONGO.edge_and_pair_betweenness(self.graph)
    #   vbtheirs = self.graph.betweenness()
    #   vbmine = CONGO.vertex_betweeenness_from_eb(self.graph, ebmine)
    #   for v in self.graph.vs:
    #       self.assertAlmostEqual(vbtheirs[v.index], vbmine[v.index])


    def test_initialize_betweenness(self):
        cp = self.graph.copy()

        eb = self.graph.edge_betweenness()
        CONGO.do_initial_betweenness(cp, 3)
        for i, e in enumerate(eb):
            self.assertAlmostEqual(e, cp.es[i]['eb'])


# def testBetweennesses(G, h):
#     eb = G.edge_betweenness(cutoff=h)
#     for i, v in enumerate(G.es):
#         print v['eb'], 2 * eb[i], abs(v['eb'] - 2 * eb[i]) > .001


def suite():
    suite = unittest.TestSuite()
    tests = ['test_test', 'test_vertex_betweeenness_from_eb', 'test_edge_betweenness', 'test_pair_betweenness']

    return unittest.TestSuite(list(map(TestCongoFunctions, tests)))


if __name__ == '__main__':
    unittest.main()