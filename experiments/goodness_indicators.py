import sys
import matplotlib.pyplot as plt
import argparse
import json
import numpy as np


def main():
    parser = argparse.ArgumentParser(description='Experiment of Correlations in Goodness Metrics')
    parser.add_argument('metrics_file', help="path to metrics file")
    args = parser.parse_args()

    #read in metrics file
    json_f = open(args.metrics_file)
    j = json.load(json_f)
    json_f.close()
    metrics = j['metrics']

    l = list(zip(
            metrics['Separability']['results'],
            metrics['Conductance']['results'],
            metrics['Triangle Participation Ratio']['results'],
            metrics['Cohesiveness']['results'],
            metrics['Average Out Degree Fraction']['results'],
            metrics['Cut Ratio']['results'],
            metrics['Density']['results'],
            metrics['Expansion']['results'],
            metrics['Flake Out Degree Fraction']['results'],
            metrics['Fraction over a Median Degree']['results'],
            metrics['Normalized Cut']['results']
            ))

    test_separability(l, args.metrics_file)




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


from operator import itemgetter

def test_separability(metrics_list, dataset_name):

    k = min(100, len(metrics_list))
    x_values = range(k)

    #first sort by separability and truncate
    focus_sep = sorted(metrics_list, key = itemgetter(0), reverse=True)[:k]

    plt.subplot(111)

    plt.title(dataset_name)

    #separability
    plt.plot(x_values, running_avg([v[0] for v in focus_sep]))

    num_features = len(metrics_list[0])

    for i in range(1, num_features):
        s = sorted(metrics_list, key = itemgetter(i), reverse=True)
        plt.plot(x_values, running_avg([v[0] for v in s]))


    plt.legend(['S', 'C', 'tpr', 'Coh', 'ODF', 'CutR', 'Den', 'Exp', 'FODF', 'FOMD', 'NC'], loc='upper right')
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
    main()
