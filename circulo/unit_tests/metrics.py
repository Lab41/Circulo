import random
import unittest
import numpy as np
import circulo.metrics
import igraph
from circulo.metrics import VertexCoverMetric


class TestMetrics(unittest.TestCase):
    def setUp(self):
        self.G=igraph.load("karate.gml")
        membership=[
                    [0,1,2,3,7,11,12,13,17,19,21],
                    [4,5,6,10,16],
                    [8,9,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33]]
        self.cover=igraph.VertexCover(self.G, membership)

        self.comm_metrics = None
        if False:
          vcm = VertexCoverMetric()
          metrics=vcm.run_analysis(self.cover, weights = None)
          self.comm_metrics = metrics.comm_metrics

    def test_density(self):
        truth = [.4181818, .6, .22875817]

        #Density is an igraph ``metric''
        test  = [ s.density() for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.density for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)


    def test_avgdegree(self):
        truth = [4.181818182, 2.4, 3.8888889]

        # Average degree is an igraph + python method
        from scipy import mean
        test  = [ mean(s.degree()) for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test = [a.degree_avg for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_FOMD(self):
        truth = [0.545454545, 0, 0.277777778]

        test  = self.cover.fraction_over_median_degree()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test = [a.fomd for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_expansion(self):
        truth = [1.272727, 0.8, 0.555556]

        test  = self.cover.expansion()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.degree_boundary_avg for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)


    def test_cutratio(self):
        truth = [.05534,.02759,.03472,]

        test  = self.cover.cut_ratio()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.cut_ratio for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)


    def test_conductance(self):
        truth = [0.2333333,0.25, 0.125]

        test  = self.cover.conductance()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.conductance for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_normalizedcut(self):
        truth = [0.346236559, 0.277027027, 0.229166667]

        test  = self.cover.normalized_cut()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.normalized_cut for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_TPR(self):
        truth = [0.9091,0.6, 0.9444]

        test  = [ s.triangle_participation_ratio() 
                  for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.tpr[1] for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_MaxODF(self):
        truth = [.5,0.3333333, 0.5 ]

        test  = self.cover.maximum_out_degree_fraction()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.odf_dict['max'] for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_avgODF(self):
        truth = [0.138131313, 0.233333333, 0.117592593]

        test  = self.cover.average_out_degree_fraction()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.odf_dict['average'] for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_FlakeODF(self):
        truth = [0,0,0]
        test  = self.cover.flake_out_degree_fraction()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.odf_dict['flake'] for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_separability(self):
        truth = [1.6428571,1.5, 3.5]

        test  = self.cover.separability()
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.separability for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)


    def test_localclusteringcoefficient(self):
        truth = [0.75310245, 0.33333333, 0.65153920]

        # Local Clustering Coeff is an igraph function
        from scipy import mean
        test  = [ mean(s.transitivity_local_undirected(mode='zero'))
                  for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

        if self.comm_metrics:
          test  = [a.clustering_coefficient for a in self.comm_metrics]
          self.assertListAlmostEquals(truth, test, 2)

    def test_cohesiveness(self):
        truth = []

        test  = [ s.cohesiveness() for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

    def assertListAlmostEquals(self, a, b, places=None, msg=None):
        self.assertEquals(np.round(a,places).tolist(), 
                          np.round(b,places).tolist(), msg=msg)


if __name__ == '__main__' :
    unittest.main()

