import igraph
import circulo
from circulo.wrappers import community
import sys
sys.path.append('/home/lab41/workspace/Circulo/experiments/setup/')
import run_algos

#Circle Graph Creation
circle = igraph.Graph.Ring(6)

#Barbell Graph Creation
barbell = igraph.Graph()
barbell.add_vertices([0,1,2,3,4,5,6,7,8])
barbell.add_edges([(0,1),(1,2),(0,2),(2,3),(3,4),(4,5),(5,6),(6,7),(6,8),(7,8)])

#Tree-like Graph Creation
tree = igraph.Graph()
tree.add_vertices([0,1,2,3,4,5,6,7,8,9,10,11])
tree.add_edges([(0,2),(1,2),(2,4),(3,4),(4,5),(5,6),(6,7),(7,8),(7,9),(6,10),(10,11)])
#tree.add_vertices([])


#Pass the graph you would like to test to create_graph_context
ctx = run_algos.create_graph_context(tree)

#BigClam
vc = community.comm_bigclam(ctx, '')()
print('BigClam')
print(vc.membership)

#BiSBM
print('BiSBM')

#Cesna

#Clauset-Newman-Moore
vc = community.comm_clauset_newman_moore(ctx, '')()
print('Clauset-Newman-Moore')
print(vc.membership)

#CoDA
vc = community.comm_coda(ctx, '')()
print('CoDA')
print(vc.membership)

#Congo
#vc = community.comm_congo(ctx, '')()
print('Congo')
#print(vc.as_cover().membership)

#Conga
vc = community.comm_conga(ctx, '')()
print(vc)
print('Conga')
print(vc.as_cover().membership)

#Spectral
print('Spectral')

#Edge Betweenness
#vc = community.comm_edge_betweenness(ctx, '')()
#print('Edge Betweenness')
#print(vc.as_clustering().membership)

#Leading Eigenvector
#vc = community.comm_leading_eigenvector(ctx, '')()
#print('Leading Eigenvector')
#print(vc.membership)


