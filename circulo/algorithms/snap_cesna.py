'''
Incomplete due to complexity with attribute files. May finish later if needed
'''

def cesna(G,  f_attributes, f_attribute_names, data_prefix='snap_', nodes='', detect_comm=10, min_comm=3, max_comm=5, trials=5, threads=4, aw=0.5,lw=1, alpha=0.05, beta=0.3, mf=0):

    '''
    Parameters
    -----------
    G:                  An iGraph or edge list file
    f_attributes:       Input node attribute file name (Required)
    f_attribute_names:  Input file name for node attribute names (Required)
    nodes:              Input file name for node names (Node ID, Node label)
    detect_comm:         The number of communities to detect (-1: detect automatically) (default:10)
    min_comm:           Minimum number of communities to try (default:3)
    max_comm:           Maximum number of communities to try (default:20)
    trials:             How many trials for the number of communities (default:5)
    threads:            Number of threads for parallelization (default:4)
    aw:                 We maximize (1 - aw) P(Network) + aw * P(Attributes) (default:0.5)
    lw:                 Weight for l-1 regularization on learning the logistic model parameters (default:1)
    alpha:              Alpha for backtracking line search (default:0.05)
    beta:               Beta for backtracking line search (default:0.3)
    mf                  if the fraction of nodes with positive values for an attribute is smaller than this, we ignore that attribute (default:0)
    '''

    snap_home, graph_file = snap.setup(G)

    if graph_file is None:
        return

    path_cesna = os.path.join(snap_home, "examples", "cesna", "cesna")

    try:
        out = subprocess.Popen([path_cesna, "-o:"+data_prefix, "-i:"+graph_file, "-l:"+nodes, "-a:"+f_attributes, "-n:"+f_attribute_names,  "-c:"+str(detect_comm), "-mc:"+str(min_comm), "xc:"+str(max_comm), "-nc:"+str(trials), "-nt:"+str(threads), "-aw:"+str(aw), "-lw:"+str(lw), "-sa:"+str(alpha), "-sb:"+str(beta), "-mf:"+str(mf)]).wait()


    except TypeError as e:
        print("Error occurred: {}".format(e))
        return

    os.remove(graph_file)

    return read_communities(data_prefix + "cmtyvv.txt", G)



