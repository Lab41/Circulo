import numpy as np
from numpy.linalg import norm
from scipy.sparse import csc_matrix, diags
from scipy.sparse.linalg import eigsh
from scipy.cluster.vq import vq, kmeans2

from igraph import Graph, VertexClustering

def __eigenvectors_to_vc(G, eigvc):
  centroid, label = kmeans2(eigvc, eigvc.shape[1], minit='points')
  return VertexClustering(G, label)

def __community_spectral_base(G, k, weights, normalized):
  L = csc_matrix(G.laplacian(weights=weights, 
                             normalized=normalized), 
                 dtype='d')
  eigvl, eigvc = eigsh(L, k, which='SM')
  if normalized:
    for row in eigvc:
      row /= norm(row)
  return __eigenvectors_to_vc(G, eigvc)

def __community_spectral_rw(G, k, weights):
  L = G.laplacian(weights=weights)
  D = np.diag(L)
  L = csc_matrix(L, dtype='d')
  D = diags(D, 0, dtype='d', format=L.format)

  eigvl, eigvc = eigsh(L, k, M=D, which='SM')

  return __eigenvectors_to_vc(G, eigvc)

def community_spectral(G, k=2, weights=None, which='NCut_rw'):
  '''
  Performs a relaxed version of Ratio or N-cut by performing k-means on 
  the (n, k)-matrix of eigenvectors from different versions of the Graph 
  Laplacian.
  @params
   G        : an igraph.Graph.
   k        : number of communities to cluster.
   weights  : A weight vector or the name of an edge property.
   which    : the type of cut to perform, one of RatioCut, NCut, or NCut_rw.
  @returns
   vc : VertexClustering with up to k clusters
  '''
  method = {
      'RatioCut'.lower()  : lambda g, c, w: __community_spectral_base(g, c, w, normalized=False),
      'NCut'.lower()      : lambda g, c, w: __community_spectral_base(g, c, w, normalized=True),
      'NCut_rw'.lower()   : lambda g, c, w: __community_spectral_rw(g, c, w)
  }

  # The default cut is accross components
  vc = G.components()
  if len(vc) >= k:
    membership = [ x%k for x in vc.membership ]
    vc = VertexClustering(G, membership)
  else:
    vc = method[which.lower()](G,k,weights)

  return vc

Graph.community_spectral = community_spectral
