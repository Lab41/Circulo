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
  
    if len(argv) != 2:
        print "Args <communities_file> <graph_edge_list>"
        sys.exit(0)


    G = nx.read_edgelist(argv[1], nodetype=int)

    ground_truth = cu.read_communities_by_community(argv[0],  G)
    
    if ground_truth is None:
        sys.exit(0)

    
    print "Total Number of Ground Truth Communities: {}".format(len(ground_truth))
    test = GoodnessIndicatorTests(G, ground_truth)
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


    def __init__(self, G, ground_truth):
        self.G = G
        self.ground_truth = ground_truth
        self.metrics_ground_truth = nx.get_community_metrics(ground_truth, G)
        

    def test_separability(self):

        k = min(100, len(self.ground_truth))
        x_values = range(k)    
        
        plt.subplot(111)
        
        #first we sort the ground truth based on separabiity, then plot
        self.metrics_ground_truth.sort(key=lambda x: x.separability, reverse=True) 
        sorted_separability = ([c.separability for c in self.metrics_ground_truth])
        plt.plot(x_values, running_avg(sorted_separability[:k]))
        
        #sort in place by conductance
        self.metrics_ground_truth.sort(key=lambda x: x.conductance, reverse=True) 
       
        plt.plot(x_values, running_avg([x.separability for x in self.metrics_ground_truth][:k]))
        
        #sort in place by tpr
        self.metrics_ground_truth.sort(key=lambda x: x.tpr, reverse=True) 
        plt.plot(x_values, running_avg([x.separability for x in self.metrics_ground_truth][:k]))
        
        #sort in place by density
        self.metrics_ground_truth.sort(key=lambda x: x.density, reverse=True)

        plt.plot(x_values, running_avg([x.separability for x in self.metrics_ground_truth][:k]))
        
        plt.legend(['U', 'c', 'tpr', 'density'], loc='upper right')        
        plt.ylabel("Separability")
        plt.xlabel("Rank, k")
        plt.show()

    def test_density(self):
        '''
        To Be Implemented
        '''
        
        pass


    def test_cohesiveness(self):
        '''
        To be Implemented
        '''
        
        pass


    def test_clustering_coefficient(self):
        '''
        To be implmented
        '''
        
        pass




if __name__ == "__main__":
    main(sys.argv[1:])
