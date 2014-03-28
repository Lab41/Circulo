#!/usr/bin/python

import sys

#Script takes number of nodes, edge list, and community list as inputs and calculates metrics



def main(argv):
    
    #num_nodes = Total number of nodes in graph
    #num_edges = Total number of edges in graph
    #n_s = Number of nodes in set community
    #m_s = Number of edges in set community
    #c_s = Number of edges on the boundry of set community 


    #Initializations
    f_edge_list = open(argv[1])
    f_comm = open(argv[2])
    num_nodes = int(argv[0])
    dim_a = num_nodes  + 1
    num_edges = 0.0
    s = set()
    a = [[0]*(dim_a) for x in xrange(dim_a)]
    
    #Pre-processing filling adjaceny matrix (fill in a 1 if edge exists between two nodes) 
    for line in f_edge_list:
        left,right = line.split()
        left = int(left) 
        right = int(right) 
        
        a[left][right] = 1
        a[right][left] = 1

        num_edges += 1
    
    #Iterating through community file
    for line in f_comm:
        comm_line = map(int, line.split())
        comm_line.sort()
        
        n_s = float(len(comm_line))
        m_s = 0.0
        c_s = 0.0
        s.clear()

        #Calculate m_s score per community
        for x in range(0, len(comm_line)):
            s.add(comm_line[x])
            for y in range(x+1,len(comm_line)):
                    if(a[comm_line[x]][comm_line[y]] == 1):
                            m_s += 1 

        #Calculate c_s score per community
        for i in range(0,len(comm_line)):
            j = comm_line[i]
            for k in range(1, len(a)):
                if(a[j][k] == 1 and ((k) not in s) ):
                    c_s += 1 

        #Different calculated metrics 
        internal_density = float(m_s / ((n_s*(n_s - 1)) / 2))
        print ("The internal density is: ")
        print internal_density
        
        edges_inside = m_s
        print("The edges inside is: ")
        print edges_inside

        avg_degree = (2 * m_s) / n_s
        print("The avg degree is: ")
        print avg_degree

        expansion = c_s/n_s
        print("The expansion is: ")
        print expansion

        cut_ratio = c_s / (n_s * (num_nodes - n_s))
        print("The cut ratio is: ")
        print cut_ratio

        conductance = c_s / ((2 * m_s) + c_s)
        print("The conductance is: ")
        print conductance

        norm_cut = conductance + c_s /((2*(num_edges - m_s)) + c_s)
        print("Norm cut is: ")
        print norm_cut

        separability = m_s/c_s
        print("The separability is: ")
        print separability

        density = m_s / n_s * (n_s - 1 )
        print("The density is: ")
        print m_s/ ((n_s * (n_s - 1)) / 2)
        
    
if __name__ == "__main__":
    main(sys.argv[1:])
