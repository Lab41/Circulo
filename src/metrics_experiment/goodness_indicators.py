# This file is meant to show how generic metrics correlate to core goodness metric


#The following tests are based on the test discussed in  Jaewon Yang and Jure Leskovec, Defining and Evaluating Network Communities based on Ground-truth


#Data sets that have been tested thus far:
# 1. (none)
# 2.


import networkx as nx
import sys
import networkx.utils.community_utils as cu
import matplotlib.pyplot as plt

def main(argv):
   
    #arg0 --> communities file
    f_ground_truth_comms = argv[0]
    f_edge_list = argv[1]

    G = nx.read_edgelist(f_edge_list, nodetype=int)
    ground_truth = cu.read_communities_by_community(f_ground_truth_comms, G)

    #found_comms = nx.bigclam(G, detect_comm=5000)
    found_comms = cu.read_communities_by_community("snap_cmtyvv.txt", G)
    print "found size: {}".format(len(found_comms))
    test = GoodnessIndicatorTests(G, ground_truth, found_comms)
    test.test_separability()

    
    
def running_avg(l):
    r = list()
    
    first = True
    cnt = 1.0
    prev = 0.0

    for i in l:
        r.append( (prev+i)/cnt)
        cnt+=1.0
        prev+=i

    return r

class GoodnessIndicatorTests:
    '''
    The purpose of this experiment is to confirm the findings in the referenced paper regarding how general community detection metrics are indicators of the 4 goodness metrics. conduct a test, select an algorithm / dataset pair 
    '''


    def __init__(self, G, ground_truth, found_comms):
        self.G = G
        self.ground_truth = ground_truth
        self.found_comms = found_comms
        
        print "Analyzing the found communities"
        self.metrics_found = nx.get_community_metrics(found_comms, G)
        print "Analyzing the ground truth"
        self.metrics_ground_truth = nx.get_community_metrics(ground_truth, G)
       


    def test_separability(self):

        k = 100

        #first we sort the ground truth based on separabiity, then plot
        self.metrics_ground_truth.sort(key=lambda x: x.separability, reverse=True) 
        plt.subplot(111)
        
        sorted_separability = [c.separability for c in self.metrics_ground_truth]
        

        k = min(k, len(self.metrics_found), len(self.ground_truth))


        #then we get the found communities and sort by conductance 
        self.metrics_found.sort(key=lambda x: x.conductance)
        by_conductance = [list(t) for t in zip(*sorted( zip( [x.conductance for x in self.metrics_found[:k]], sorted_separability), key=lambda x: x[0]))]
        by_tpr = [list(t) for t in zip(*sorted( zip( [x.tpr for x in self.metrics_found[:k]], sorted_separability), key=lambda x: x[0]))]
        by_density = [list(t) for t in zip(*sorted( zip( [x.density for x in self.metrics_found[:k]], sorted_separability), key=lambda x: x[0]))]
          
       
        #calculate the running average
        
        

        
        x_values = range(k)    
        plt.plot(x_values, running_avg(sorted_separability[:k]))
        plt.plot(x_values, running_avg(by_conductance[1][:k]))
        plt.plot(x_values, running_avg(by_tpr[1][:k]))

        plt.plot(x_values, running_avg(by_density[1][:k])) 
        plt.legend(['U', 'c', 'tpr', 'density'], loc='upper right')        
        plt.ylabel("Separability")
        plt.xlabel("Rank, k")
        plt.show()

    def test_density(self):
        pass


    def test_cohesiveness(self):
        pass


    def test_clustering_coefficient(self):
        pass




if __name__ == "__main__":
    main(sys.argv[1:])
