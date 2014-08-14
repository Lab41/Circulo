import importlib
from igraph import plot
from circulo import metrics

'''
Senate Community Example

'''

#get the graph from the data holding
senate_mod = importlib.import_module("data.congress_voting.run")

G = senate_mod.get_graph()
ground_truth = senate_mod.get_ground_truth(G)

clustering = G.community_leading_eigenvector(weights="weight")

cover = clustering.as_cover()

cover.print_metrics()


#cover.compute_metrics(weights="weight")
#for k,v in cover.metrics.items():
#    print("{}      {}".format(k,v))

#score = metrics.f1(clustering, ground_truth)


#result = VertexCoverMetric.run_analysis(clustering.as_cover())

#result.report()
#result.to_json()
#metrics.run_analysis(clustering, ground_truth, "metric.txt")

#print(score)
