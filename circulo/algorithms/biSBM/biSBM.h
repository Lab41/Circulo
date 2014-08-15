/**
 * TODO: main comment
 *
 *
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>  // log
#include <float.h>
#include <assert.h>
#include <igraph.h>


int igraph_community_bipartite_sbm(igraph_t *graph, igraph_vector_t *membership, 
                                   igraph_integer_t k_a, igraph_integer_t k_b, 
                                   igraph_integer_t max_iters, igraph_bool_t degree_correct);

int log_message(const char *message, ...);

void igraph_read_graph_generic(igraph_t *graph, char *type, char *file_name);

void print_usage_and_exit(int exitstatus);


