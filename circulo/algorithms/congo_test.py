import CONGO
import unittest
import igraph

class TestCongoFunctions(unittest.TestCase):

	def setUp(self):
		"""
		Initializes the graph for testing to Zachary's
		karate club.
		"""
		self.graph = igraph.Graph.Famous("zachary")


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


	def test_vertex_betweeenness_from_eb(self):
		"""
		Checks that the implementation of vertex_betweeenness_from_eb
		yields the same results as that of igraph's graph.betweenness
		"""
		eb = self.graph.edge_betweenness()
		vbtheirs = self.graph.betweenness()
		vbmine = CONGO.vertex_betweeenness_from_eb(self.graph, eb)
		for i in range(self.graph.vcount()):
			self.assertAlmostEqual(vbtheirs[i], vbmine[i]) 


	def test_edge_betweenness(self):
		"""
		Checks that the implementation of edge_betweenness in
		edge_and_pair_betweenness matches that of igraph's
		graph.edge_betweenness.
		"""
		ebtheirs = self.graph.edge_betweenness()
		ebmine, _ = CONGO.edge_and_pair_betweenness(self.graph)
		for e in self.graph.es:
			self.assertAlmostEqual(ebtheirs[e.index], ebmine[frozenset(e.tuple)])


	def test_pair_betweenness(self):
		"""
		Checks to make sure that the sum of all pair betweennesses
		on a specific vertex are equal to its vertex betweenness.
		"""
		_, pb = CONGO.edge_and_pair_betweenness(self.graph)
		vb = self.graph.betweenness()
		for v in pb:
			self.assertAlmostEqual(sum(pb[v].values()), vb[v])


def suite():
	suite = unittest.TestSuite()
	tests = ['test_test', 'test_vertex_betweeenness_from_eb', 'test_edge_betweenness', 'test_pair_betweenness']

	return unittest.TestSuite(map(TestCongoFunctions, tests))


if __name__ == '__main__':
    unittest.main()