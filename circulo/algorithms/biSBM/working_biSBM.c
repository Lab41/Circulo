/**
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>

// TODO move to .h

#include "working_biSBM.h"

#define WRONG_OPTION_COUNT 1
#define UNKNOWN_GRAPH_TYPE 2
#define BAD_FILE 3
#define GRAPH_READ_FAILED 4
#define ILLEGAL_FORMAT 5


/**
 * Function: igraph_read_graph_generic
 * -----------------------------------
 * TODO
 */
void igraph_read_graph_generic(igraph_t *graph, char* type, char* file_name){
  FILE * infile;
  infile = fopen (file_name, "r");
  if (infile == NULL){
    printf("Could not open file: %s\n", file_name);
    print_usage_and_exit(BAD_FILE);
  }

  if (!strcmp(type, "gml")){
    printf("Attempting to read in .gml file...\n");

    // TODO: this function segfaults when it fails. Submit a bugfix!
    // As such, err isn't doing anything.
    int err = igraph_read_graph_gml(graph, infile);
    fclose(infile);
    if (err) exit(GRAPH_READ_FAILED);
    return;
  }

  if (!strcmp(type, "graphml")){
    printf("Attempting to read in graphml file...\n");

    // TODO: this function aborts when it fails, so err isn't doing
    // anything.
    int err = igraph_read_graph_graphml(graph, infile, 0);
    fclose(infile);
    if (err) exit(GRAPH_READ_FAILED);
    return;
  }
  // add more types!
  print_usage_and_exit(UNKNOWN_GRAPH_TYPE);
  
}

/**
 * Function: print_usage_and_exit
 * ------------------------------
 * Prints the command line usage of the program,
 * and exits with exit status exitstatus.
 */
void print_usage_and_exit(int exitstatus){
  printf("\nUsage:\n");
  printf("  ./working_biSBM [graph type] [path to graph] [K_a] [K_b] [max iterations]\n");
  printf("  Where graph type is one of:\n");
  printf("    gml\n");
  printf("    graphml\n");
  // //TODO: ADD SUPPORT FOR MORE
  printf("  K_a is the number of groups of type a\n");
  printf("  K_b is the number of groups of type b\n");
  printf("  max iterations is the maximum number of iterations that the algorithm will attempt.\n\n");
  exit(exitstatus);
}



int *initialize_groups(int a, int b, igraph_vector_bool_t *types){
  int *groupings = malloc(sizeof(int) * igraph_vector_bool_size(types));
  igraph_rng_t *rng = igraph_rng_default();
  // assign seed to some constant for repeatable results.
  int seed = time(NULL); 
  igraph_rng_seed(rng, seed);
  for (int i = 0; i < igraph_vector_bool_size(types); i++){
    if (!VECTOR(*types)[i])
      groupings[i] = igraph_rng_get_integer(rng, 0, a - 1);
    else
      groupings[i] = igraph_rng_get_integer(rng, a, a + b - 1);
  }
  return groupings;
}


double score_partition(int *partition, igraph_t *graph){
  return 0.0;
}

double iterate_once(int *partition, int a, igraph_vector_bool_t *types, igraph_t *graph){
  return score_partition(partition, graph);
}

double run_algorithm(int *partition, int a, igraph_vector_bool_t *types, igraph_t *graph, int max_iters){
  int *latest_grouping = malloc(sizeof(int) * igraph_vector_bool_size(types));
  memcpy(latest_grouping, partition, sizeof(int) * igraph_vector_bool_size(types));
  double score = score_partition(partition, graph);
  for (int i = 0; i < max_iters; i++){
    double new_score = iterate_once(latest_grouping, a, types, graph);
    if (new_score <= score) break;
    score = new_score;
    memcpy(partition, latest_grouping, sizeof(int) * igraph_vector_bool_size(types));
  }
  return score;
}


int main(int argc, char *argv[]) {
  if (argc != 6) // TODO: check all arguments
    print_usage_and_exit(WRONG_OPTION_COUNT);
  igraph_t graph;
  igraph_read_graph_generic(&graph, argv[1], argv[2]);
  int a = atoi(argv[3]);
  int b = atoi(argv[4]);
  int max_iters = atoi(argv[5]);


  printf("Graph with %d vertices and %d edges read successfully.\n"
            , igraph_vcount(&graph), igraph_ecount(&graph)); 

  igraph_bool_t is_bipartite;
  igraph_vector_bool_t types;
  igraph_vector_bool_init(&types, igraph_vcount(&graph));

  printf("Finding a bipartite mapping...\n");
  // TODO: check for error code
  igraph_is_bipartite(&graph, &is_bipartite, &types);
  if (!is_bipartite){
    printf("Input graph is not bipartite. Exiting...\n");
    exit(ILLEGAL_FORMAT);
  }
  printf("Mapping successful.\n");

  int *partition = initialize_groups(a, b, &types);

  double best_score = run_algorithm(partition, a, &types, &graph, max_iters);

  printf("%f\n", best_score);
  // result is stored in partition
  return 0;
}
