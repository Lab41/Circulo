import numpy as np
from scipy.sparse import dok_matrix, csc_matrix, diags, eye
from scipy.sparse.linalg import eigsh, inv, ArpackNoConvergence, eigs
from scipy.cluster.vq import vq, kmeans2, whiten
from igraph.clustering import VertexClustering

def __laplacian_and_diag(G):
    '''
    sourced from: section 3.2 normalized graph laplacian
    http://www.kyb.mpg.de/fileadmin/user_upload/files/publications/attachments/luxburg07_tutorial_4488%5b0%5d.pdf
    '''
    L = G.laplacian()
    #Extract the diagonal from the unnormalized L
    D = np.diag(L)

    # Convert them to sparse
    L = csc_matrix(L, dtype='d')
    D = diags(D, 0, dtype='d', format=L.format)

    return L, D

def __normalize_rows(U):
    '''
    Normalize the rows of the U matrix using the l2-norm (or Euclidean-norm)
    '''
    for row in U:
        norm = np.sqrt(np.sum(np.abs(row)**2))
        row /= norm


def unnormalized_spectral_clustering(G, k):
    L = csc_matrix(G.laplacian(), dtype='d')

    # Compute the k smallest eigenpairs
    la, U = eigsh(L, k, which='SM')

 	# Compute k-means on rows of U
    U = whiten(U)
    codebook, distortion = kmeans2(U, k)

	# We return the cluster
    code, distance = vq(U, codebook)
    return VertexClustering(G, code)

def normalized_spectral_clustering_rw(G,k):
    L,D = __laplacian_and_diag(G)

    la, U = eigsh(L, k, M=D, which='SM', tol=1e-8)

    U = whiten(U)
    codebook, distortion = kmeans2(U, k)

    code, distance = vq(U, codebook)
    return VertexClustering(G, code)

def normalized_spectral_clustering_sym(G,k):
    L = csc_matrix(G.laplacian(normalized=True), dtype='d')

    la, U = eigsh(L, k, which='SM', tol=1e-8)

    __normalize_rows(U)
    codebook, distortion = kmeans2(U, k)

    code, distance = vq(U, codebook)
    return VertexClustering(G,code)

def conductance(vc):
    '''
    Returns the conductance of a cut according to Wikipedia
    http://en.wikipedia.org/wiki/Conductance_(graph)
    '''
    if len(vc.sizes()) != 2:
        return float('inf')

    # Compute conductance of a cut
    edge_count_vc0 = 0.0
    edge_count_vc0_to_vc1 = 0.0
    for v in vc[0]:
        for n in vc.graph.neighbors(v):
            if n in vc[0]: #same cluster
                if n != v:
                    edge_count_vc0 +=.5
                else:  #self edge only is counted once
                    edge_count_vc0 += 1.0
            else: #outer edge
                edge_count_vc0_to_vc1 +=1.0

    edge_count_vc1 = 0.0
    for v in vc[1]:
        for n in vc.graph.neighbors(v):
            if n in vc[1]:
                if n != v:
                    edge_count_vc1 += .5
                else:
                    edge_count_vc1 += 1.0

    edge_count_vc0 += edge_count_vc0_to_vc1
    edge_count_vc1 += edge_count_vc0_to_vc1

    # Please check Wikipedia for conductance definition
    # http://en.wikipedia.org/wiki/Conductance_(graph)
    if min(edge_count_vc0, edge_count_vc1) == 0:
        return float('inf')
    else:
        return edge_count_vc0_to_vc1/min(edge_count_vc0, edge_count_vc1)

def min_conductance(G, tries=3):
    '''
    Returns the minimum conductance of a Graph by using spectral clustering to ``approximate'' the minimum ratio-cut.
    http://www.kyb.mpg.de/fileadmin/user_upload/files/publications/attachments/Luxburg07_tutorial_4488%5b0%5d.pdf
    '''
    (rv_val, rv_vc) = (float("inf"), None)
    for i in range(0,tries):
        try:
            #Obtain a cut of G, it should already be a minimum
            curr_vc = normalized_spectral_clustering_sym(G,2)
            curr_val = conductance(curr_vc)
            if curr_val < rv_val :
                (rv_val, rv_vc) = (curr_val, curr_vc)
        except:
            pass

    return rv_val, rv_vc


