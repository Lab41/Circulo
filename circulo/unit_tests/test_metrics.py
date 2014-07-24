import random
import unittest
import igraph
from circulo.metrics import VertexCoverMetric

class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.G=igraph.load("karate.gml")
        
        membership=[
                    [0,1,2,3,7,11,12,13,17,19,21],
                    [4,5,6,10,16],
                    [8,9,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33]]
        cover=igraph.VertexCover(self.G, membership)
        metrics=VertexCoverMetric.run_analysis(cover, weights=None)
        metrics.report()
        self.comm_metrics=metrics.comm_metrics
        
    def test_density(self):
        self.assertEqual(round(.4181818, 2), round(self.comm_metrics[0].density, 2))
        self.assertEqual(round(.6, 2), round(self.comm_metrics[1].density,2))
        self.assertEqual(round(.22875817, 2), round(self.comm_metrics[2].density,2))

    def test_avgdegree(self):
        self.assertEqual(round(4.181818182, 2), round(self.comm_metrics[0].degree_avg,2))
        self.assertEqual(round(2.4, 2), round(self.comm_metrics[1].degree_avg,2))
        self.assertEqual(round(3.8888889,2), round(self.comm_metrics[2].degree_avg,2))

    def test_FOMD(self):
        self.assertEqual(round(0.545454545,2), round(self.comm_metrics[0].fomd, 2))
        self.assertEqual(round(0, 2), round(self.comm_metrics[1].fomd, 2))
        self.assertEqual(round(0.277777778,2), round(self.comm_metrics[2].fomd,2))

    def test_expansion(self):
        self.assertEqual(round(1.272727, 2), round(self.comm_metrics[0].degree_boundary_avg, 2))
        self.assertEqual(round(0.8, 2), round(self.comm_metrics[1].degree_boundary_avg, 2))
        self.assertEqual(round(0.555556, 2), round(self.comm_metrics[2].degree_boundary_avg,2))

    def test_cutratio(self):
        self.assertEqual(round(.05534, 2), round(self.comm_metrics[0].cut_ratio, 2))
        self.assertEqual(round(.02759, 2), round(self.comm_metrics[1].cut_ratio, 2))
        self.assertEqual(round(.03472, 2), round(self.comm_metrics[2].cut_ratio, 2))

    def test_conductance(self):
        self.assertEqual(round(0.2333333,2), round(self.comm_metrics[0].conductance,2))
        self.assertEqual(round(0.25,2), round(self.comm_metrics[1].conductance,2))
        self.assertEqual(round(0.125,2), round(self.comm_metrics[2].conductance,2))

    def test_normalizedcut(self):
        self.assertEqual(round(0.346236559,2), round(self.comm_metrics[0].normalized_cut,2))
        self.assertEqual(round(0.277027027,2), round(self.comm_metrics[1].normalized_cut,2))
        self.assertEqual(round(0.229166667, 2), round(self.comm_metrics[2].normalized_cut,2))

    def test_TPR(self):
        self.assertEqual(round(0.9091, 2), round(self.comm_metrics[0].tpr[1], 2))
        self.assertEqual(round(0.6, 2), round(self.comm_metrics[1].tpr[1], 2))
        self.assertEqual(round(0.7778, 2), round(self.comm_metrics[2].tpr[1], 2))

    def test_MaxODF(self):
        self.assertEqual(round(0.5,2), round(self.comm_metrics[0].odf_dict["max"], 2))
        self.assertEqual(round(0.3333333,2), round(self.comm_metrics[1].odf_dict["max"], 2))
        self.assertEqual(round(0.5, 2), round(self.comm_metrics[2].odf_dict["max"], 2))

    def test_avgODF(self):
        self.assertEqual(round(0.138131313,2), round(self.comm_metrics[0].odf_dict["average"], 2))
        self.assertEqual(round(0.233333333,2), round(self.comm_metrics[1].odf_dict["average"], 2))
        self.assertEqual(round(0.117592593, 2), round(self.comm_metrics[2].odf_dict["average"], 2))

    def test_FlakeODF(self):
        self.assertEqual(round(0, 2), round(self.comm_metrics[0].odf_dict["flake"], 2))
        self.assertEqual(round(0, 2), round(self.comm_metrics[1].odf_dict["flake"], 2))
        self.assertEqual(round(0, 2), round(self.comm_metrics[2].odf_dict["flake"], 2))

    def test_separability(self):
        self.assertEqual(round(1.6428571,2), round(self.comm_metrics[0].separability, 2))
        self.assertEqual(round(1.5, 2), round(self.comm_metrics[1].separability, 2))
        self.assertEqual(round(3.5, 2), round(self.comm_metrics[2].separability, 2))

    def test_clusteringcoefficient(self):
        self.assertEqual(round(0.77049062, 2), round(self.comm_metrics[0].clustering_coefficient, 2))
        self.assertEqual(round(0.74358974, 2), round(self.comm_metrics[1].clustering_coefficient, 2))
        self.assertEqual(round(0.71404151, 2), round(self.comm_metrics[1].clustering_coefficient, 2))






if __name__ == '__main__' :
    unittest.main()

