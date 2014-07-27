import numpy as np
import scipy
import scipy.sparse as sp

from igraph import Graph, VertexCover

def __reset_diagonal(A, sparse):
    '''
    input: matrix
    ouput: matrix object with diagonals set to 0
    '''

    if sparse:
        A = A - sp.dia_matrix((A.diagonal()[scipy.newaxis, :], [0]), shape=A.shape)
    else:
        A = A.copy()
        np.fill_diagonal(A, 0)
    return A

def __get_diagonal(A, sparse):
    '''
    input: Matrix
    output: vector with the diagonal entries
    '''
    if sparse:
        return A.diagonal()
    else:
        return np.diag(A)


def __get_matrix(vc, sparse):
    '''
    inputs: List of lists (vertexCover) object
    output: Node x Node matrix with the cell values indicating the number of clusters
            each pair of nodes shares
    '''
    n = len(vc) # number of nodes
    nc = max([max(i) for i in vc]) + 1 # number of clusters

    create_zero_matrix = sp.csr_matrix if sparse else np.zeros
    A = create_zero_matrix((n,n), dtype='int')
    for i in range(nc):
        # Create a Clique from Membership
        v = np.matrix([ (i in m)*1 for m in vc])
        if sparse:
            v = sp.csr_matrix(v)
        Ai = v.T*v
        A = A+Ai
    # DO NOT ZERO THE DIAGONALS HERE, __get_omega_e depends on them.
    return A.tocsr() if sparse else A

def __get_omega_u(A1, A2, sparse):
    '''
    inputs: Two __get_matrix results
    outputs: un-adjusted omega score

    '''
    n = A1.shape[0]
    M = n*(n-1)/2.0
    notA = __reset_diagonal((A1 != A2), sparse)
    rv = n*(n-1) - notA.sum()
    return rv/(2*M)

def __get_omega_e(A1, A2, sparse):
    '''
    inputs: Two __get_matrix results
    outputs: expected omega score

    '''
    n = A1.shape[0]
    M = n*(n-1)/2.0
    k = max(max((__get_diagonal(A1, sparse))), max(__get_diagonal(A2, sparse)))

    # The 0th iteration is done with a negation since it is a sparse matrix
    t_not0_1 = __reset_diagonal((A1 != 0), sparse)
    t_not0_2 = __reset_diagonal((A2 != 0), sparse)
    rv = n*(n-1) - t_not0_1.sum()
    rv *= n*(n-1) - t_not0_2.sum()
    for i in range(1, k+1):
        t_i_1 = __reset_diagonal((A1 == i), sparse)
        t_i_2 = __reset_diagonal((A2 == i), sparse)

        rv += t_i_1.sum()*t_i_2.sum()
    rv /= (2*M)**2
    return rv;

def omega_index(cover_membership_a, cover_membership_b, sparse=True):
    '''
    Uses the Omega Index metrics to compare two covers of a given domain, e.g. a Graph.
    @param cover_membership_a : A list of vertex to membership list.
            Example - a = [[0,1],[1],[0,2]]
    @param cover_membership_b : A list of vertex to membership list.
    @returns: Best match = 1, No match = 0
    '''

    A1 = __get_matrix(cover_membership_a, sparse)
    A2 = __get_matrix(cover_membership_b, sparse)
    omega_u = __get_omega_u(A1, A2, sparse)
    omega_e = __get_omega_e(A1, A2, sparse)

    return (omega_u - omega_e)/(1-omega_e)

