import circulo.metrics
import circulo.algorithms.spectral
from igraph import Graph

def min_conductance(G, tries=3):
    '''
    Returns the minimum conductance of a Graph by using spectral clustering to ``approximate'' the minimum ratio-cut.
    http://www.kyb.mpg.de/fileadmin/user_upload/files/publications/attachments/Luxburg07_tutorial_4488%5b0%5d.pdf
    '''
    (rv_val, rv_vc) = (float("inf"), None)
    for i in range(0,tries):
        try:
            #Obtain a cut of G, it should already be a minimum
            curr_vc = G.community_spectral(k=2, which='NCut')
            curr_val = curr_vc.as_cover().conductance()
            if curr_val < rv_val :
                (rv_val, rv_vc) = (curr_val, curr_vc)
        except:
            pass


    return rv_val, rv_vc

Graph.min_conductance = min_conductance
