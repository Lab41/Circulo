/**
 *
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>  // log
#include <float.h>
#include <assert.h>
// TODO move to .h

#include "working_biSBM.h"

#define WRONG_OPTION_COUNT 1
#define UNKNOWN_GRAPH_TYPE 2
#define BAD_FILE 3
#define GRAPH_READ_FAILED 4
#define ILLEGAL_FORMAT 5



#define INTERCOMMUNITY(inter_comm, c_a, c_b, a) (MATRIX(inter_comm, c_a, c_b - a))



typedef struct {
  int a, b, size;
  int *partition;
  igraph_matrix_t *adj_mat;
  igraph_vector_t **adj_list;
  igraph_matrix_t *inter_comm_edges;
  igraph_real_t *comm_tot_degree;
} Housekeeping;

typedef struct {
  int v, src, dest;
} Swaprecord;

/**
 * TODO
 *     * get rid of excessive allocation
 *     * store individual variables instead of whole arrays
 *     * check for null on malloc
 *     * free all allocated memory
 *     * check for error code on all igraph calls
 */


/**
 * Function: igraph_read_graph_generic
 * -----------------------------------
 * Takes a pointer to an empty graph along with the filetype
 * and path to file, and attempts to read the file in `file_name`
 * into the ifgraph_t graph `graph` using the `type` specified.
 */
void igraph_read_graph_generic(igraph_t *graph, char *type, char *file_name){
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
  // TODO: add more types!
  print_usage_and_exit(UNKNOWN_GRAPH_TYPE);
  
}


/**
 * Function: print_usage_and_exit
 * ------------------------------
 * Prints the command line usage of the program,
 * and exits with exit status `exitstatus`.
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




igraph_real_t score_partition(Housekeeping *hk){
  igraph_real_t score = 0;
  for (int c_a = 0; c_a < hk->a; c_a++){
    for (int c_b = hk->a; c_b < hk->a + hk->b; c_b++){
      igraph_real_t inter_community = INTERCOMMUNITY(*(hk->inter_comm_edges), c_a, c_b, hk->a);
      igraph_real_t c_a_sum = hk->comm_tot_degree[c_a];
      igraph_real_t c_b_sum = hk->comm_tot_degree[c_b];
      if (!inter_community || !c_a_sum || !c_b_sum) return -INFINITY; // really raise an error.
      score += inter_community * log(inter_community / (c_a_sum * c_b_sum));
    }
  }
  return score;
}







void make_swap(Housekeeping *hk, int v, int to){
  int from = hk->partition[v];
  //if (from == to) return;
 // printf("to: %d, from: %d\n", to, from);
  hk->partition[v] = to;
  igraph_vector_t *neighbors = hk->adj_list[v];
  int degree = igraph_vector_size(neighbors);
  hk->comm_tot_degree[from] -= degree;
  hk->comm_tot_degree[to] += degree;
  int c_1 = from;
  for (int neigh = 0; neigh < degree; neigh++){
    int neighbor_comm = hk->partition[(int) VECTOR(*neighbors)[neigh]];
    int c_2 = neighbor_comm;
    if (c_1 < c_2){
      INTERCOMMUNITY(*(hk->inter_comm_edges), c_1, c_2, hk->a) -= 1;
      INTERCOMMUNITY(*(hk->inter_comm_edges), to, c_2, hk->a) += 1;
    }
    else{
      INTERCOMMUNITY(*(hk->inter_comm_edges), c_2, c_1, hk->a) -= 1;
      INTERCOMMUNITY(*(hk->inter_comm_edges), c_2, to, hk->a) += 1;
    }
  }
}

double score_swap(Housekeeping *hk, int v, int to){
  int tmp = hk->partition[v];
  make_swap(hk, v, to);
  double score = score_partition(hk);
  make_swap(hk, v, tmp);
  return score;
}


double score_swaps(Housekeeping *hk, int v, int *dest){
  int from = hk->partition[v];
  int begin = 0;
  int end = hk->a;
  if (from >= hk->a){
    begin = hk->a; 
    end = hk->a + hk->b;
  }
  double best_score = -INFINITY;
  for (int to = begin; to < end; to++){
    if (to == from) continue;
    //printf("Trying to switch from community %d to %d\n", hk->partition[v], to);
    double new_score = score_swap(hk, v, to);
    if (new_score > best_score){
      best_score = new_score;
      *dest = to;
    }
  }
  return best_score;
}



double make_best_swap(Housekeeping *hk, bool *used, Swaprecord *swaprecord, int i){
  int max_v = -1;
  double max_score = -INFINITY;
  int max_swap = -1;
  for (int v = 0; v < hk->size; v++){
    if (used[v]) continue;
    int dest;
    double score = score_swaps(hk, v, &dest);
    
    if (score > max_score){
      
      max_score = score;
      max_swap = dest;
      max_v = v;
    }
  }
  //printf("here\n");
  assert(max_v >= 0);
  assert(max_swap >= 0); 
  swaprecord[i].v = max_v;
  swaprecord[i].src = hk->partition[max_v];
  swaprecord[i].dest = max_swap;
  printf("Swapping. %f, vertex: %d, from: %d, to: %d\n", max_score, max_v, hk->partition[max_v], max_swap);
  make_swap(hk, max_v, max_swap);
  
  used[max_v] = true;
  return max_score;

}



void rewind_swaps(Housekeeping *hk, Swaprecord *swaprecord, int best_swap){
  for (int i = hk->size - 1; i > best_swap; i--){
    make_swap(hk, swaprecord[i].v, swaprecord[i].src);
  }
}



void run_iteration(Housekeeping *hk, double init_score){
  bool used[hk->size];
  Swaprecord swaprecord[hk->size];
  int best_swap = -1;
  for (int i = 0; i < hk->size; i++) used[i] = false;
  for (int i = 0; i < hk->size; i++){ 
    int new_score = make_best_swap(hk, used, swaprecord, i);
    if (new_score > init_score){
      init_score = new_score;
      best_swap = i;
    }
  }
  if (best_swap == -1){
    printf("Score has not improved. Terminating...");
    exit(0);
  }
  rewind_swaps(hk, swaprecord, best_swap);
  // need to save best state and go back to it before the next iteration.
}







double run_algorithm(Housekeeping *hk, int max_iters){
  double score = score_partition(hk);
  printf("Initial score: %f\n", score);
  for (int i = 0; i < max_iters; i++){
    printf("Beginning iteration %d\n", i + 1);
    run_iteration(hk, score);
    score = score_partition(hk);
    printf("Score after iteration %d: %f\n", i + 1, score);
  }
  return score;
}



/**
 * Function: initialize_groups
 * ---------------------------
 * Given group sizes `a` and `b`, randomly initializes each vertex to 
 * a group. If the vertex type is 0, it will be randomly placed into
 * a group in the range [0, a). If it is 1, it will be randomly
 * placed into a group in the range [a, a+b)
 */
void initialize_groups(int a, int b, igraph_vector_bool_t *types, int *partition){
  //int *groupings = malloc(sizeof(int) * igraph_vector_bool_size(types));
  igraph_rng_t *rng = igraph_rng_default();
  // assign seed to some constant for repeatable results.
  int seed = 1;//time(NULL); 
  igraph_rng_seed(rng, seed);
  for (int i = 0; i < igraph_vector_bool_size(types); i++){
    if (!VECTOR(*types)[i]) // type 0
      partition[i] = igraph_rng_get_integer(rng, 0, a - 1);
    else // type 1
      partition[i] = igraph_rng_get_integer(rng, a, a + b - 1);
  }
}


// add possibility for uncorrected
void initialize_degree_sums(int *partition, igraph_real_t *comm_degree, igraph_vector_t *deg){
  for (int v = 0; v < igraph_vector_size(deg); v++){
    comm_degree[partition[v]] += VECTOR(*deg)[v]; // += 1 for uncorrected.
  }
}


void initialize_inter_comm(igraph_matrix_t *inter_comm, int *partition, igraph_matrix_t *mat, int a, int size){
  igraph_matrix_null(inter_comm);
  for (int row = 0; row < size; row++){
    // just gets the lower triangular
    for (int col = row + 1; col < size; col++){
      if (MATRIX(*mat, row, col)){
        int group_r = partition[row];
        int group_c = partition[col];
        if (group_r < a && group_c >= a)
          MATRIX(*inter_comm, group_r, group_c - a)++;
        else if (group_r >= a && group_r < a)
          MATRIX(*inter_comm, group_c, group_r - a)++;
      }
    }
  }
}


void initialize_neighbors(igraph_t *graph, igraph_vector_t *neighbors[]){
  igraph_vector_t *neigh = malloc(sizeof(igraph_vector_t) * igraph_vcount(graph));
  for (int v = 0; v < igraph_vcount(graph); v++){
    igraph_vector_init(&neigh[v], 0);
    igraph_neighbors(graph, &neigh[v], v, IGRAPH_ALL);
    neighbors[v] = &neigh[v];
  }
}



int main(int argc, char *argv[]) {
  if (argc != 6) // TODO: check all arguments
    print_usage_and_exit(WRONG_OPTION_COUNT);
  igraph_t graph;
  igraph_read_graph_generic(&graph, argv[1], argv[2]);
  int a = atoi(argv[3]);
  int b = atoi(argv[4]);
  int max_iters = atoi(argv[5]);
  int size = igraph_vcount(&graph);

  printf("Graph with %d vertices and %d edges read successfully.\n"
            , size, igraph_ecount(&graph)); 

  igraph_vector_bool_t types;
  igraph_vector_bool_init(&types, size);

  printf("Finding a bipartite mapping...\n");
  igraph_bool_t is_bipartite;
  igraph_is_bipartite(&graph, &is_bipartite, &types);
  if (!is_bipartite){
    printf("Input graph is not bipartite. Exiting...\n");
    exit(ILLEGAL_FORMAT);
  }
  printf("Mapping successful.\n");

  igraph_matrix_t mat;
  igraph_matrix_init(&mat, size, size);
  // TOOD: use IGRAPH_GET_ADJACENCY_UPPER instead, perhaps last param true?
  igraph_get_adjacency(&graph, &mat, IGRAPH_GET_ADJACENCY_BOTH, false);

  igraph_vector_t deg;
  igraph_vector_init(&deg, size);
  igraph_degree(&graph, &deg, igraph_vss_all(), IGRAPH_ALL, true);

  //igraph_vector_t partition;
  //igraph_vector_init(&partition, size);
  printf("Initializing to random groups...\n");
  int partition[size];
  initialize_groups(a, b, &types, partition);
  printf("Initialization successful.\n");

  igraph_matrix_t inter_comm;
  igraph_matrix_init(&inter_comm, a, b);
  initialize_inter_comm(&inter_comm, partition, &mat, a, size);


  igraph_real_t comm_degree[a + b];
  initialize_degree_sums(partition, comm_degree, &deg);

  igraph_vector_t *neighbors[size];
  initialize_neighbors(&graph, neighbors);

// todo: replace all degree by neighbors

  Housekeeping hk;
  hk.a = a;
  hk.b = b;
  hk.size = size;
  hk.partition = partition;
  hk.adj_list = neighbors;
  hk.adj_mat = &mat;
  hk.inter_comm_edges = &inter_comm;
  hk.comm_tot_degree = comm_degree;

  printf("Running algorithm...\n");
  run_algorithm(&hk, max_iters);







  // for each swap in possible swaps, score the swap and choose the best one. make the best swap
  // and repeat until all vertices have been swapped once. Take the best partition from 
  // that and iterate.



  // for (int i = 0; i < a; i++){
  //   for (int j = a; j < a+b; j++){
  //     printf("inter %d - %d: %d\n", i, j, (int) INTERCOMMUNITY(inter_comm, i, j, a));
  //   }
  // }

  // printf("Running algorithm...\n");
  // double best_score = run_algorithm(partition, a, b, &types, &graph, &mat, max_iters);
  // printf("Algorithm completed successfully.\n");

  // printf("%f\n", best_score);
  // for (int i = 0; i < igraph_vcount(&graph); i++){
  //   printf("Vertex %d: group %d\n", i, partition[i]);
  // }
  // free(partition);
  // igraph_vector_bool_destroy(&types);
  // igraph_destroy(&graph);
  return 0;

}
