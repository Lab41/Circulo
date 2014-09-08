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




def graph_goodness_v2(comm_metrics):
    '''
    Graphs the change in the specified metric across communities relative to conductance
    '''

    metrics = [(c.conductance, c.density, c.degree_avg, c.fomd, c.degree_boundary_avg, c.cut_ratio, c.normalized_cut) for c in comm_metrics]

    metrics_sorted = metrics.sort(key=lambda x: x[0], reverse=True)

    c, d, a, f, e, cr, n  = zip(*metrics)

    plt.subplot(331)
    plt.plot(c)
    plt.title("Conductance")
    plt.subplot(332)
    plt.plot(d)
    plt.title("Density")
    plt.subplot(333)
    plt.plot(a)
    plt.title("Average Degree")
    plt.subplot(334)
    plt.plot(f)
    plt.title("FOMD")
    plt.subplot(336)
    plt.plot(e)
    plt.title("Expansion")
    plt.subplot(337)
    plt.plot(cr)
    plt.title("Cut Ratio")
    plt.subplot(338)
    plt.plot(n)
    plt.title("Normalized Cut")


    plt.show()





def graph_goodness(comm_metrics):
    '''
    Graphs the change in the specified metric across communities
    '''

    plt.subplot(331)
    plt.plot(sorted([c.density for c in comm_metrics ], reverse=True))
    plt.ylabel("Density")

    plt.subplot(332)
    plt.plot(sorted([c.degree_avg for c in comm_metrics ], reverse=True))
    plt.ylabel("Average Degree")

    plt.title("Each graph is sorted highest to lowest y-value")
    plt.subplot(333)
    plt.plot(sorted([c.fomd for c in comm_metrics ], reverse=True))
    plt.ylabel("FOMD")

    plt.subplot(334)
    plt.plot(sorted([c.tpr[1] for c in comm_metrics ], reverse=True))
    plt.ylabel("TPR")

    plt.subplot(335)
    plt.plot(sorted([c.degree_boundary_avg for c in comm_metrics ], reverse=True))
    plt.ylabel("Expansion")

    plt.subplot(336)
    plt.plot(sorted([c.cut_ratio for c in comm_metrics ], reverse=True))
    plt.ylabel("Cut-Ratio")

    plt.subplot(337)
    plt.plot(sorted([c.conductance for c in comm_metrics ], reverse=True))
    plt.ylabel("Conductance")

    plt.subplot(338)
    plt.plot(sorted([c.normalized_cut for c in comm_metrics ], reverse=True))
    plt.ylabel("Normalized Cut")

    plt.subplot(339)
    plt.plot(sorted([c.separability for c in comm_metrics ], reverse=True))
    plt.ylabel("Separability")

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
