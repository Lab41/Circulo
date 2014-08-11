/**
 *
 *
 */

#include <iostream>
#include <fstream>
#include <vector>
#include <array>
#include <random>
#include <stdio.h>
#include <chrono>

// TODO move to .h

#include "working_biSBM.h"

#define WRONG_OPTION_COUNT 1
#define UNKNOWN_GRAPH_TYPE 2
#define BAD_FILE 3
#define GRAPH_READ_FAILED 4
#define ILLEGAL_FORMAT 5

using namespace std;

/**
 * Function: igraph_read_graph_generic
 * -----------------------------------
 * TODO
 */
void igraph_read_graph_generic(igraph_t *graph, char* type, char* file_name){
  FILE * infile;
  infile = fopen (file_name, "r");
  if (infile == NULL){
    cout << endl << "Could not open file: " << file_name << endl;
    print_usage_and_exit(BAD_FILE);
  }

  if (!strcmp(type, "gml")){
    cout << "Attempting to read in .gml file..." << endl;

    // TODO: this function segfaults when it fails. Submit a bugfix!
    // As such, err isn't doing anything.
    int err = igraph_read_graph_gml(graph, infile);
    fclose(infile);
    if (err) exit(GRAPH_READ_FAILED);
    return;
  }

  if (!strcmp(type, "graphml")){
    cout << "Attempting to read in graphml file..." << endl;

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
  cout << endl;
  cout << "Usage:" << endl;
  cout << "  ./working_biSBM [graph type] [path to graph] [K_a] [K_b] [max iterations]" << endl;
  cout << "  Where graph type is one of:" << endl;
  cout << "    gml" << endl;
  cout << "    graphml" << endl;
  //TODO: ADD SUPPORT FOR MORE
  cout << "  K_a is the number of groups of type a" << endl;
  cout << "  K_b is the number of groups of type b" << endl;
  cout << "  max iterations is the maximum number of iterations that the algorithm will attempt." << endl;
  cout << endl;
  exit(exitstatus);
}


int *initialize_groups(int a, int b, igraph_vector_bool_t *types){
  int *groupings = new int[igraph_vector_bool_size(types)];

  // assign seed to some constant for repeatable results.
  unsigned seed = chrono::system_clock::now().time_since_epoch().count();
  default_random_engine generator(seed);
  uniform_int_distribution<int> rand_a(0, a - 1);
  uniform_int_distribution<int> rand_b(a, a + K_b - 1);
  for (int i = 0; i < igraph_vector_bool_size(types); i++){
    if (!VECTOR(*types)[i])
      groupings[i] = rand_a(generator);
    else
      groupings[i] = rand_b(generator);
  return groupings;
}


int *run_algorithm(int *initialization, int a, igraph_vector_bool_t *types, igraph_t *graph, int max_iters){
  int *best_grouping = 
}


// vector<vector<vector<int> > > run_algorithm(vector<vector<vector<int> > > *random_initialization, 
//                                             igraph_vector_bool_t *types, igraph_t *graph,
//                                             double max_score){
//   int num_vertices = igraph_vcount(graph);
//   int iteration_max_score = 0;
//   int iteration_max_assignment = // TODO
//   vector<int> used;
//   used.reserve(num_vertices);
//   while (used.size() < num_vertices){
//     int curr_max = 0;
//     vector<vector<vector<int> > > curr_assignments;
//     for (int i = 0; i < igraph_vcount(graph); i++){
//       double score = score_best_move(); // WORKING HERE

//   }

//   return *random_initialization;
// }


int main(int argc, char *argv[]) {
  if (argc != 6) // TODO: check all arguments
    print_usage_and_exit(WRONG_OPTION_COUNT);
  igraph_t graph;
  igraph_read_graph_generic(&graph, argv[1], argv[2]);
  int a = stoi(argv[3]);
  int b = stoi(argv[4]);
  int max_iters = stoi(argv[5]);

  cout << "Graph with " << igraph_vcount(&graph) 
       << " vertices and " << igraph_ecount(&graph) 
       << " edges read successfully. " << endl;

  igraph_bool_t is_bipartite;
  igraph_vector_bool_t types;
  igraph_vector_bool_init(&types, igraph_vcount(&graph));

  cout << "Finding a bipartite mapping..." << endl;
  // TODO: check for error code
  igraph_is_bipartite(&graph, &is_bipartite, &types);
  if (!is_bipartite){
    cout << "Input graph is not bipartite. Exiting..." << endl;
    exit(ILLEGAL_FORMAT);
  }

  int *random_initialization = initialize_groups(a, b, &types);

  int *result = run_algorithm(random_initialization, a, &types, &graph, max_iters);

  return 0;
}
