import sys
import math
import igraph
import nimfa
import numpy as np
from numpy.linalg import lstsq
from numpy import dot
from scipy.cluster.vq import kmeans2, vq
from scipy.linalg import norm
from scipy.optimize import minimize

def main(argv):
    G = igraph.Graph.Read_GML(argv[0])

    if len(argv) > 1:
        roles = int(argv[1])
        model = extract_rolx_roles(G, roles=roles)
    else:
        model = extract_rolx_roles(G)

    H = model.basis()
    print("Node-role matrix is of dimensions %s by %s" % H.shape)
    print(H)

    K = make_sense(G, H)
    print("Role-feature matrix is of dimensions %s by %s" % K.shape)
    print(K)

    return H, K

def extract_rolx_roles(G, roles=2):
    print("Creating Vertex Features matrix")
    V = vertex_features(G)
    print("V is a %s by %s matrix." % V.shape)

    return get_factorization(V, roles)

def make_sense(G, H):
    features = [ 'betweenness', 'closeness', 'degree', 'diversity', 'eccentricity', 'pagerank', 'personalized_pagerank', 'strength' ]
    feature_fns = [ getattr(G, f) for f in features ]
    feature_matrix = [ func() for func in feature_fns ]
    feature_matrix = np.matrix(feature_matrix).transpose()
    print(feature_matrix)

    M = feature_matrix
    K = complete_factor(H, M, h_on_left=True)
    print(K)

    return K

def threshold(level):
    return 10.0**(-15+level)

def recursive_feature_array(G, func, n):
    attr_name = "_rolx_" + func.__name__ + "_" + str(n)

    if attr_name in G.vs.attributes():
        result = np.array(G.vs[attr_name])
        return result

    if n==0:
        stats = func(G) #must return a 
        result = np.array([[x] for x in stats]) # wrapping to create 2D-array
        result = result * 1.0 # ensure that we're using floating-points
        G.vs[attr_name] = result
        return result

    prev_stats = recursive_feature_array(G, func, n-1)
    all_neighbor_stats = [0] * G.vcount()
    for v in G.vs:
        neighbors = G.neighbors(v)
        degree = len(neighbors)
        if degree == 0: 
            neighbor_avgs = neighbor_sums = np.zeros(prev_stats[0].size)
        else: 
            prev_neighbor_stats = [prev_stats[x] for x in neighbors]
            neighbor_sums_vec = sum(prev_neighbor_stats)
            neighbor_avgs_vec = neighbor_sums_vec / degree

        all_neighbor_stats[v.index] = np.concatenate((neighbor_sums_vec, neighbor_avgs_vec), axis=0)

    G.vs[attr_name] = all_neighbor_stats
    return all_neighbor_stats

def recursive_feature(G, f, n):
    """
        G: iGraph graph with annotations
        func: string containing function name
        n: int, recursion level

        Computes the given function recursively on each vertex

        Current precondition: already have run the computation for G, func, n-1.
    """
    return np.matrix(recursive_feature_array(G,f,n))


def approx_linear_solution(w, A, threshold=1e-15):
    '''
    Checks if w is linearly dependent on the columns of A, this is done by solving the least squares problem (LSP)
        min || w - Ax ||_2^2
         x
    and checking if || w - Ax_star || <= threshold, where x_star is the arg_minimizer of the LSP

    w: column vector
    A: matrix
    threshold: int
    '''
    x0 = np.zeros(A.shape[1])
    x_star, residual, rank, s = lstsq(A, w)
    norm_residual = norm(residual)
    result = True if norm_residual <= threshold else False
    return (result, norm_residual, x_star)

def degree(G):
    return G.degree()

def vertex_egonet(G, v):
    ego_network = G.induced_subgraph(G.neighborhood(v))
    ego_edges = ego_network.ecount()
    return ego_edges

def egonet(G):
    return [vertex_egonet(G, v) for v in G.vs]

def vertex_egonet_out(G, v):
    neighbors = G.neighborhood(v)
    ego_network = G.induced_subgraph(neighbors)
    ego_edges = ego_network.ecount()
    degree_sum = sum([G.degree(v) for v in neighbors])
    out_edges = degree_sum - 2*ego_edges #Summing over degree will doublecount every edge within the ego network
    return out_edges

def egonet_out(G):
    return [vertex_egonet_out(G, v) for v in G.vs]

def threshold(level):
    return 10.0**(-15+level)

def vertex_features(g):
    """ 
    Constructs a vertex feature matrix using recursive 
    """
    G = g.copy()
    num_rows = G.vcount()

    features = [degree, egonet, egonet_out]
    V = np.matrix(np.zeros((num_rows, 16*len(features))))

    next_feature_col = 0
    for feature in features:
        base = recursive_feature(G, feature, 0)
        base = base/norm(base)
        V = add_col(V, base, next_feature_col)

        next_feature_col += 1
        level = 1

        accepted_features = True
        while accepted_features:
            accepted_features = False
            feature_matrix = recursive_feature(G, feature, level)
            rows, cols = feature_matrix.shape

            for i in range(cols):
                b = feature_matrix[:,i]
                b = b/norm(b)

                mat = V[:,:next_feature_col]
                (is_approx_soln, _, _) = approx_linear_solution(b, mat, threshold(level))
                if not is_approx_soln:
                    V = add_col(V, b, next_feature_col)
                    next_feature_col += 1
                    accepted_features = True
            level += 1

    return V[:, :next_feature_col]

def add_col(V, b, insert_col):
    rows, cols = V.shape
    if insert_col == cols: # need to resize V
        zeros = np.matrix(np.zeros((rows, 1)))
        V = np.concatenate((V, zeros), axis=1)
    V[:, insert_col] = b
    return V

def kmeans_quantize(M, bits):
    k = 2**bits

    obs = np.asarray(M).reshape(-1)
    centroid, label = kmeans2(obs, k)

    enc_M = [centroid[v] for v in label]
    enc_M = np.matrix(enc_M).reshape(M.shape)

    return enc_M, (bits * enc_M.size)

def log_bin_quantize(M, bits):
    pass

def kl_divergence(A,B):
    rv = 0
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if A[i,j] == 0:
                rv += B[i,j]
            else:
                rv += A[i,j]*(math.log(A[i,j]/B[i,j])-1) + B[i,j]

    return rv

def kl_divergence_2(A,B):
    a = np.asarray(A, dtype=np.float)
    b = np.asarray(B, dtype=np.float)

    return np.sum(np.where(a != 0, a * np.log(a / b), 0))

def description_length(V, fctr_res, bits=10):
    W = fctr_res.basis()
    H = fctr_res.coef()

    enc_W, enc_W_cost = kmeans_quantize(W, bits)
    enc_H, enc_H_cost = kmeans_quantize(H, bits)

    enc_cost = enc_W_cost + enc_H_cost
    err_cost = kl_divergence(V, dot(enc_W,enc_H))

    return enc_cost, err_cost

def standardize_rows(M):
    rv = np.matrix(M)
    for i in range(rv.shape[0]):
        mean = np.mean(M[i, :])
        stdev = np.std(M[i, :])
        rv[i, :]= (M[i, :]- mean)/stdev
    return rv

# def standardize(M):
#    m_flat = np.asarray(M).reshape(-1)
#    mean = np.mean(m_flat)
#    stdev = np.std(m_flat)
#    m_flat = (m_flat - mean)/stdev
#  
#    return m_flat.reshape(M.shape)

def get_factorization(V, num_roles):
    # http://nimfa.biolab.si/nimfa.methods.factorization.pmf.html?highlight=probabilistic
    # http://scikit-learn.org/stable/modules/generated/sklearn.decomposition.NMF.html
    fctr = nimfa.mf(V, rank=num_roles, method="nmf", max_iter=65, update='divergence', objective='div')
    fctr_res = nimfa.mf_run(fctr)
    return fctr_res

def get_optimal_factorization(V, min_roles=2, max_roles=6, min_bits=1, max_bits=10):
    max_roles = min(max_roles, V.shape[1]) # Can't have more possible roles than features

    num_role_options = max_roles - min_roles
    num_bit_options = max_bits - min_bits

    mat_enc_cost = np.zeros((num_role_options, num_bit_options))
    mat_err_cost = np.zeros((num_role_options, num_bit_options))
    mat_fctr_res = [] * num_role_options

    # Setup and run the factorization problem
    for i in range(num_role_options):
        rank = min_roles + i
        fctr_res = get_factorization(V, rank)
        mat_fctr_res[i] = fctr_res

        for j in range(num_bit_options):
            bits = min_bits + j
            enc_cost, err_cost = description_length(V, fctr_res, bits)
            mat_enc_cost[i,j] = enc_cost
            mat_err_cost[i,j] = err_cost

    mat_std_enc_cost = standardize_rows(mat_enc_cost)
    mat_std_err_cost = standardize_rows(mat_err_cost)

    mat_total_cost = mat_enc_cost + mat_err_cost
    mat_total_std_cost = mat_std_enc_cost + mat_std_err_cost

   # print mat_total_cost
    print('min cost @', idx, ' or at ', min_coord)

    print("rank, bits, enc_cost, err_cost, total_cost, std_enc_cost, std_err_cost, std_total_cost") 
    for i in range(num_role_options):
        for j in range(num_bit_options):
            rank = min_roles + i
            bits = min_bits + j

            enc_cost       = mat_enc_cost[i,j]
            err_cost       = mat_err_cost[i,j]

            std_enc_cost   = mat_std_enc_cost[i,j]
            std_err_cost   = mat_std_err_cost[i,j]

            total_cost     = mat_total_cost[i,j]
            total_std_cost = mat_total_std_cost[i,j]

            print("%s, %s, (%s, %s, %s), (%s, %s, %s)" % (rank, bits, 
                    enc_cost, err_cost, total_cost, std_enc_cost, std_err_cost, total_std_cost))

    min_idx = mat_total_std_cost.argmin()
    min_coord = np.unravel_index(min_idx, mat_total_std_cost.shape)
    min_role_index, min_bit_index = min_coord

    min_role_value = min_role_index + min_roles
    min_bit_value = min_bit_index + min_bits
    
    min_std_enc_cost = mat_std_enc_cost[min_coord]
    min_std_err_cost = mat_std_err_cost[min_coord]
    min_total_std_cost = mat_total_std_cost[min_coord]
    print("%s, %s, (%s, %s, %s)" % (min_role_value, min_bit_value, min_std_enc_cost, min_std_err_cost, min_total_std_cost))

    return mat_fctr_res[min_role_index]


def sense_residual_left_factor(W, H, M):
    W = np.matrix(W).reshape((M.shape[0], H.shape[0]))
    return norm(M - W*H)

def sense_residual_right_factor(K, H, M):
    K = np.matrix(K).reshape((H.shape[1], M.shape[1]))
    return norm(M - H*K)

def complete_factor(H, M, h_on_left=True):
    """Given nonnegative matrix M and a nonnegative factor H of M, finds the other (nonnegative) factor of M.
       H: known factor of matrix M.
       M: product matrix.
       h_on_left: boolean, true if H is the left factor of M, false if H is the right factor.

       If H is left factor, find the matrix K such that HK=M. If H is the right factor, finds W such that WH=M
       Result is an appropriately-sized matrix. """

    if h_on_left:
        shape = (H.shape[1], M.shape[1])
        residual = sense_residual_right_factor
    else:
        shape = (M.shape[0], H.shape[0])
        residual = sense_residual_left_factor

    size = shape[0] * shape[1]
    guess = np.zeros(size)
    bounds = [(0, None)] * size # (all elements of matrix must be nonnegative)
    result = minimize(residual, guess, args=(H, M), method='L-BFGS-B', bounds=bounds)

    x = result["x"]
    G = np.matrix(x).reshape(shape)
    return G

if __name__ == "__main__":
    main(sys.argv[1:])

