import igraph
import circulo.metrics

g = igraph.Graph.Famous('Zachary')

g.compute_metrics()
print(g.metrics)

cover = g.community_multilevel().as_cover()

cover.compute_metrics()
print(cover.metrics)

