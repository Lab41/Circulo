import CONGO
import unittest
import igraph

class TestCongoFunctions(unittest.TestCase):
	def setUp(self):
		self.graph = igraph.Graph.Famous("zachary")

	def tearDown(self):
		self.graph = None

	def test_test(self):
		eb = self.graph.edge_betweenness()
		self.assertEqual(self.graph.edge_betweenness(), eb, "gimme test failed.")

	def test_vertex_betweeenness_from_eb(self):
		eb = self.graph.edge_betweenness()
		#for i in range(self.graph.vcount()):
		self.assertEqual(self.graph.betweenness(), 
						 CONGO.vertex_betweeenness_from_eb(self.graph, eb))


def suite():
	suite = unittest.TestSuite()
	tests = ['test_test', 'test_vertex_betweeenness_from_eb']

	return unittest.TestSuite(map(TestCongoFunctions, tests))


if __name__ == '__main__':
    unittest.main()