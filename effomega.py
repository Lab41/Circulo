#!/usr/bin/python

import sys

def main(argv):
    
    #Command line inputs in the form of <ground truth file> <experimental file> <number of nodes being analyzed>
    f_ground = open(argv[0])
    f_experiment = open(argv[1])
    num_nodes = float((argv[2]))

    #Initialization of lists to be used for analysis
    gt_line = []
    exp_line = []
    my_dict = dict();

    #Reading in of the experimental file
    for line in f_experiment:
    
        #create list of elements in one line
        exp_line = map(int,line.split())

        #Find all pairs of vertices first by sorting array
        exp_line.sort()

        #Find each vertex pair and update  hashtable with counts
        for x in range (0, len(exp_line)):
            for y in range(x+1, len(exp_line)):
                #search rest of file for exp_line[x] and exp_line[y]
                if(exp_line[x], exp_line[y]) in my_dict:
                    my_dict[exp_line[x], exp_line[y]] += 1 
                else:
                    my_dict[exp_line[x],exp_line[y]] = 1;

    '''Ground Truth file analysis below'''

    #Reading in of the ground truth file
    for line in f_ground:
              
        #create list of elements in one line
        gt_line = map(int,line.split())

        #Find all pairs of vertices first by sorting array
        gt_line.sort()

        #Find each vertex pair and update hashtable with counts
        for i in range (0, len(gt_line)):
            for j in range (i+1, len(gt_line)):
                    if(gt_line[i], gt_line[j]) in my_dict:
                        my_dict[gt_line[i], gt_line[j]] -= 1

    #Count the number of commonalities between ground and experimental
    common_count = 0;
    for key in my_dict:
        if(my_dict[key] == 0):
            common_count+=1

    #Calculate omega score
    omega = (1/(num_nodes)**2) * common_count
    print ("The final omega score is:")
    print omega
    
if __name__ == "__main__":
        main(sys.argv[1:])
