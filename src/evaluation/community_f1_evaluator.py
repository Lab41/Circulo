#!/usr/bin/env python

# based on "Overlapping Community Detection at Scale: A Nonnegative Matrix Factorization Apporach
# http://infolab.stanford.edu/~crucis/pubs/paper-nmfagm.pdf by Yang and Leskovec

import sys

def main(argv):


    if len(argv) != 2:
        print "f1_eval  <evaluated_results_file> <ground_truth_file>"
        return

    results_file = argv[0]
    truth_file = argv[1]

    ground_truth_list = list()
    results_list = list()

    with open(results_file) as f:
        results_list = [map(int, line.split()) for line in f]

    with open(truth_file) as f:
        ground_truth_list = [map(int, line.split()) for line in f]

    print "Evaluating F1 score"
    print "{} Communities in ground truth".format(len(ground_truth_list))
    print "{} Communities in results".format(len(results_list))

    f1_sum_0 = sum([get_highest_f1(x, results_list) for x in ground_truth_list])
    f1_sum_1 = sum([get_highest_f1(x, ground_truth_list) for x in results_list])
    
    final_score = .5 * (  1.0/float(len(ground_truth_list)) * f1_sum_0 + 1.0/float(len(results_list)) * f1_sum_1)
    
    print "F1 Score: {}".format(final_score)



def get_highest_f1(src_community, community_list):
    """
    Find the best matching community in the list using f1, then return highest score 

    :param src_community:   community to base search on
    :param community_list:  list of communities to search in 
    """
    
    max_f1 = 0.0

    for matchee in community_list:
        score = f1_score(src_community, matchee)
        if score > max_f1:
            max_f1 = score
    
    return max_f1



def f1_score(community_a, community_b):
    """
    according to http://en.wikipedia.org/wiki/F1_score
    
    F_1 = 2 * (precision * recall) / (precision + recall)
    
    where precision = #matched / len (set_a)
          recall = #matched / len(set_b)
    """

    intersect_set = set(community_a).intersection(community_b)
    overlap_len = len(intersect_set)
   
    if overlap_len > 0:
        precision = float(overlap_len) / float(len(community_a))
        recall = float(overlap_len) / float(len(community_b))
        return 2.0 * (precision * recall) /  (precision + recall)
    else:
        return 0.0

if __name__ == "__main__":
    main(sys.argv[1:])
