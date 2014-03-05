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
        for line in f:
            items = map(int, line.split())
            results_list.append(items)


    with open(truth_file) as f:
        for line in f:
            items = map(int, line.split())
            ground_truth_list.append(items)
  
    print "Evaluating F1 score"
    print "{} Communities in ground truth".format(len(ground_truth_list))
    print "{} Communities in results".format(len(results_list))


    #from the perspective of the ground truth communities
    f1_sum_0 = 0.0

    for ground_truth_comm in ground_truth_list:
        best_result_match = match_community(ground_truth_comm, results_list)
        if best_result_match is not None:
            f1_sum_0 += f1_score(ground_truth_comm, best_result_match)


    #from the perspective of the results communities
    f1_sum_1 = 0.0

    for result_comm in results_list:
        best_ground_truth_match = match_community(result_comm, ground_truth_list)
        
        if best_ground_truth_match is not None:
            f1_sum_1 += f1_score(result_comm, best_ground_truth_match)

    

    final_score = .5 * (  1.0/float(len(ground_truth_list)) * f1_sum_0 + 1.0/float(len(results_list)) * f1_sum_1)
    
    print "F1 Score: {}".format(final_score)



def match_community(src_community, community_list):
    """
    Find the best matching community in the list 

    :param src_community:   community to base search on
    :param community_list:  list of communities to search in 
    """
    
    max_f1 = 0
    best_matchee = None

    for matchee in community_list:
        score = f1_score(src_community, matchee)
        if score > max_f1:
            best_matchee = matchee

    
    return best_matchee

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
