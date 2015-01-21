import random
import unittest
import numpy as np
import circulo.metrics
import igraph

import importlib
import inspect
from circulo.data.databot import CirculoData
from circulo.setup.run_metrics import cover_from_membership
import circulo.metrics.cover


class TestMetrics(unittest.TestCase):
    def setUp(self):
        DATASET='karate'
        #load the graph and ground truth in
        data_mod =  importlib.import_module('circulo.data.'+DATASET+'.run')

        instance = None

        for name,cls in inspect.getmembers(data_mod):
            if inspect.isclass(cls) and issubclass(cls, CirculoData) and name != "CirculoData":
                instance = cls(DATASET)

        self.G = instance.get_graph()
        membership=[[0,1,2,3,7,11,12,13,17,19,21],
                    [4,5,6,10,16],
                    [8,9,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33]]
        self.weights=[5,7,4,5,8,7,2,1,1,6,7,4,9,6,8,2,2,1,2,5,6,5,7,7,3,4,4,6,7,7,5,7,4,8,5,4,5,3,1,6,4,3,3,3,1,6,2,7,8,8,1,7,5,7,5,4,7,3,7,5,8,9,4,2,8,8,6,3,6,6,8,5,6,7,5,7,7,7]
        self.G.es['weight'] = self.weights

        self.cover = circulo.metrics.cover.VertexCover(self.G, membership)

    def test_internaldensity(self):
        #doesn't apply to weighted graphs
        truth = [.4181818, .6, .22875817]

        #Density is an igraph ``metric''
        test  = [ s.density() for s in self.cover.subgraphs()]
        self.assertListAlmostEquals(truth, test, 2)

    def test_avgdegree(self):
        truth = [4.181818182, 2.4, 3.8888889]

        # Average degree is an igraph + python method
        from scipy import mean
        test  = [ mean(s.degree()) for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

    def test_wavgdegree(self):
        truth = [24, 15.2, 23.3333334]

        # Average degree is an igraph + python method
        from scipy import mean
        test  = [ mean(s.strength(weights='weight')) for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

    def test_FOMD(self):
        truth = [0.545454545, 0, 0.277777778]

        test = circulo.metrics.cover.fomd(self.cover)
        self.assertListAlmostEquals(truth, test, 2)

    def test_WFOMD(self):
        truth = [0.545454545, 0.4 , 0.388888889]

        test = circulo.metrics.cover.fomd(self.cover, weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_expansion(self):
        truth = [1.272727, 0.8, 0.555556]

        test  = self.cover.expansion()
        self.assertListAlmostEquals(truth, test, 2)

    def test_wexpansion(self):
        truth = [2.181818, 1.2, 1]

        test  = self.cover.expansion(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_cutratio(self):
        #not applicable to weighted graphs
        truth = [.05534,.02759,.03472,]

        test = circulo.metrics.cover.cut_ratio(self.cover, allow_nan=True)
        self.assertListAlmostEquals(truth, test, 2)

    def test_conductance(self):
        truth = [0.2333333,0.25, 0.125]

        test  = self.cover.conductance()
        self.assertListAlmostEquals(truth, test, 2)

    def test_wconductance(self):
        truth = [0.083333, 0.0731707, 0.0410959]

        test  = self.cover.conductance(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_normalizedcut(self):
        truth = [0.346236559, 0.277027027, 0.229166667]

        test  = self.cover.normalized_cut()
        self.assertListAlmostEquals(truth, test, 2)

    def test_wnormalizedcut(self):
        truth = [0.125586854, 0.081300813, 0.085430866]

        test  = self.cover.normalized_cut(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_TPR(self):
        #same for weighted and unweighted graphs
        truth = [0.9091,0.6, 0.9444444]

        test  = [ s.triangle_participation_ratio()
                  for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

    def test_MaxODF(self):
        truth = [.5,0.3333333, 0.5 ]

        test = circulo.metrics.cover.maximum_out_degree_fraction(self.cover)
        self.assertListAlmostEquals(truth, test, 2)

    def test_WMaxODF(self):
        truth = [0.222222222, 0.153846154, 0.2]

        test  = self.cover.maximum_out_degree_fraction(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_avgODF(self):
        truth = [0.138131313, 0.233333333, 0.117592593]

        test  = self.cover.average_out_degree_fraction()
        self.assertListAlmostEquals(truth, test, 2)

    def test_wavgODF(self):
        truth = [0.064922913, 0.080586081, 0.041399798]

        test  = self.cover.average_out_degree_fraction(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_FlakeODF(self):
        truth = [0,0,0]

        test = circulo.metrics.cover.flake_out_degree_fraction(self.cover)
        #test  = self.cover.flake_out_degree_fraction()
        self.assertListAlmostEquals(truth, test, 2)

    def test_WFLakeODF(self):
        truth = [0,0,0]

        test = circulo.metrics.cover.flake_out_degree_fraction(self.cover, weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_separability(self):
        truth = [1.6428571,1.5, 3.5]

        test = circulo.metrics.cover.separability(self.cover)
        self.assertListAlmostEquals(truth, test, 2)

    def test_wseparability(self):
        truth = [5.5, 6.3333333333, 11.666666667]

        test  = self.cover.separability(weights='weight')
        self.assertListAlmostEquals(truth, test, 2)

    def test_localclusteringcoefficient(self):
        #This averages the local clustering coefficient
        #Results are the same for weighted and unweighted graphs

        truth = [0.75310245, 0.33333333, 0.65153920]

        # Local Clustering Coeff is an igraph function
        from scipy import mean
        test  = [ mean(s.transitivity_local_undirected(mode='zero'))
                  for s in self.cover.subgraphs() ]
        self.assertListAlmostEquals(truth, test, 2)

    def test_cohesiveness(self):
        # TODO: Calculate cohesiveness "truth" cohesiveness truth
        self.skipTest("Not sure what truth values for this should be, skipping for now")
        truth = []

        test  = [ s.cohesiveness() for s in self.cover.subgraphs() ]

        self.assertListAlmostEquals(truth, test, 2)

    def assertListAlmostEquals(self, a, b, places=None, msg=None):
        self.assertEquals(np.round(a,places).tolist(),
                          np.round(b,places).tolist(), msg=msg)


if __name__ == '__main__' :
    unittest.main()

