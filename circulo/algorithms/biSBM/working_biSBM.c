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

#define DOUBLE_ERROR .00000001


#define INTERCOMMUNITY(inter_comm, c_a, c_b, a) (MATRIX(inter_comm, c_a, c_b - a))



typedef struct {
  int a, b, size;
  int *partition;
  //igraph_matrix_t *adj_mat;
  igraph_vector_t **adj_list;
  igraph_vector_bool_t *types;
  igraph_matrix_t *inter_comm_edges;
  igraph_real_t *comm_tot_degree;
} Housekeeping;

typedef struct {
  int v, src, dest;
} Swaprecord;

/**
 * TODO
 *     * get rid of excessive allocation
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
    // As such, err isn't doing anything. There also seems to be a 
    // memory leak in this function.
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

  if (!strcmp(type, "edgelist")){
    printf("Attempting to read in edgelist file...\n");

    // TODO: this function aborts when it fails, so err isn't doing
    // anything.
    int err = igraph_read_graph_edgelist(graph, infile, 0, false);
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
      //printf("%d, %d, %d\n", (int) inter_community, (int) c_a_sum, (int) c_b_sum);
      if (!(int) inter_community || !(int) c_a_sum || !(int) c_b_sum) return -INFINITY; // really raise an error.
      score += inter_community * log(inter_community / (c_a_sum * c_b_sum));
    }
  }
  return score;
}







void make_swap(Housekeeping *hk, int v, int to){
  int from = hk->partition[v];
  if (to == from) return; // check if this line speeds things up
 // printf("to: %d, from: %d\n", to, from);
  hk->partition[v] = to;
  igraph_vector_t *neighbors = hk->adj_list[v];
  int degree = igraph_vector_size(neighbors);
  hk->comm_tot_degree[from] -= degree;
  hk->comm_tot_degree[to] += degree;
  int c_1 = from;
  // if degree correct
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
  // not degree correct suff would go here
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
  if (max_v == -1){
    // don't make any swaps -- we assume an empty community is illegal.
    // a little hackish here -- we just record an empty swap on vertex 0.
    swaprecord[i].v = 0;
    swaprecord[i].src = hk->partition[0];
    swaprecord[i].dest = hk->partition[0];
    return max_score;
  }
  swaprecord[i].v = max_v;
  swaprecord[i].src = hk->partition[max_v];
  swaprecord[i].dest = max_swap;
  make_swap(hk, max_v, max_swap);
  used[max_v] = true;
  return max_score;
}



void rewind_swaps(Housekeeping *hk, Swaprecord *swaprecord, int best_swap){
  for (int i = hk->size - 1; i > best_swap; i--){
    make_swap(hk, swaprecord[i].v, swaprecord[i].src);
  }
}



bool run_iteration(Housekeeping *hk, double init_score){
  bool used[hk->size];
  Swaprecord swaprecord[hk->size];
  int best_swap = -1;
  for (int i = 0; i < hk->size; i++) used[i] = false;
  for (int i = 0; i < hk->size; i++){ 
    double new_score = make_best_swap(hk, used, swaprecord, i);
    if (new_score > init_score + DOUBLE_ERROR){
      init_score = new_score;
      best_swap = i;
    }
  }
  rewind_swaps(hk, swaprecord, best_swap);
  if (best_swap == -1)
    return true;
  return false;
}


double run_algorithm(Housekeeping *hk, int max_iters){
  double score = score_partition(hk);
  printf("Initial score: %f\n", score);
  for (int i = 0; i < max_iters; i++){
    printf("Beginning iteration %d\n", i + 1);
    bool is_last_iteration = run_iteration(hk, score);
    score = score_partition(hk);
    printf("Score after iteration %d: %f\n", i + 1, score);
    if (is_last_iteration){
      printf("Score has not improved. Terminating...\n");
      return score;
    }
  }
  return score;
}


// /**
//  * Function: initialize_groups
//  * ---------------------------
//  * Given group sizes `a` and `b`, randomly initializes each vertex to 
//  * a group. If the vertex type is 0, it will be randomly placed into
//  * a group in the range [0, a). If it is 1, it will be randomly
//  * placed into a group in the range [a, a+b)
//  */
// void initialize_groups(int a, int b, igraph_vector_bool_t *types, int *partition){
//   //int *groupings = malloc(sizeof(int) * igraph_vector_bool_size(types));
//   igraph_rng_t *rng = igraph_rng_default();
//   // assign seed to some constant for repeatable results.
//   int seed = time(NULL); 
//   igraph_rng_seed(rng, seed);
//   for (int i = 0; i < igraph_vector_bool_size(types); i++){
//     if (!VECTOR(*types)[i]) // type 0
//       partition[i] = igraph_rng_get_integer(rng, 0, a - 1);
//     else // type 1
//       partition[i] = igraph_rng_get_integer(rng, a, a + b - 1);
//   }
// }


// //  TODO: add possibility for uncorrected
// void initialize_degree_sums(int *partition, igraph_real_t *comm_degree, igraph_vector_t *deg){
//   for (int v = 0; v < igraph_vector_size(deg); v++){
//     comm_degree[partition[v]] += VECTOR(*deg)[v]; // += 1 for uncorrected.
//   }
// }


// void initialize_inter_comm(igraph_matrix_t *inter_comm, int *partition, igraph_matrix_t *mat, int a, int size){
//   igraph_matrix_null(inter_comm);
//   for (int row = 0; row < size; row++){
//     // just gets the lower triangular
//     for (int col = row + 1; col < size; col++){
//       if (MATRIX(*mat, row, col)){
//         int group_r = partition[row];
//         int group_c = partition[col];
//         if (group_r < a && group_c >= a)
//           MATRIX(*inter_comm, group_r, group_c - a)++;
//         else if (group_r >= a && group_r < a)
//           MATRIX(*inter_comm, group_c, group_r - a)++;
//       }
//     }
//   }
// }


// void initialize_neighbors(igraph_t *graph, igraph_vector_t *neighbors[]){
//   igraph_vector_t *neigh = malloc(sizeof(igraph_vector_t) * igraph_vcount(graph));
//   for (int v = 0; v < igraph_vcount(graph); v++){
//     igraph_vector_init(&neigh[v], 0);
//     igraph_neighbors(graph, &neigh[v], v, IGRAPH_ALL);
//     neighbors[v] = &neigh[v];
//   }
// }



int delete_lonely_nodes(igraph_t *graph, igraph_vector_t *deg){
  igraph_vector_t lonely_ids;
  igraph_vector_init(&lonely_ids, 0);
  for (int i = 0; i < igraph_vcount(graph); i++){
    if (!VECTOR(*deg)[i])
      igraph_vector_push_back(&lonely_ids, i);
  }
  int num_lonely = igraph_vector_size(&lonely_ids);
  for (int i = 0; i < num_lonely; i++){
    igraph_vector_remove(deg, VECTOR(lonely_ids)[i]);
  }
  igraph_delete_vertices(graph, igraph_vss_vector(&lonely_ids));
  // free lonely ids
  return num_lonely;

}


void initialize_types(Housekeeping *hk, igraph_t *graph){
  //igraph_vector_bool_t types;
  printf("here\n");
  igraph_vector_bool_init(hk->types, hk->size);
  printf("here1\n");
  printf("Finding a bipartite mapping...\n");
  igraph_bool_t is_bipartite;
  igraph_is_bipartite(graph, &is_bipartite, hk->types);
  if (!is_bipartite){
    printf("Input graph is not bipartite. Exiting...\n");
    exit(ILLEGAL_FORMAT);
  }
  printf("Mapping successful.\n");
  //hk->types = &types;
  printf("373. there are %ld types\n", igraph_vector_bool_size(hk->types));
}


void initialize_partition(Housekeeping *hk){
  int *partition = malloc(sizeof(int) * hk->size);
  igraph_rng_t *rng = igraph_rng_default();
  // assign seed to some constant for repeatable results.
  printf("381. there are %ld types\n", igraph_vector_bool_size(hk->types));
  int seed = time(NULL); 
  igraph_rng_seed(rng, seed);
  for (int i = 0; i < hk->size; i++){
    if (!VECTOR(*(hk->types))[i]) // type 0
      partition[i] = igraph_rng_get_integer(rng, 0, hk->a - 1);
    else // type 1
      partition[i] = igraph_rng_get_integer(rng, hk->a, hk->a + hk->b - 1);
  }
  hk->partition = partition;
}


void initialize_neighbors(Housekeeping *hk, igraph_t *graph){
  igraph_vector_t **neighbors = malloc(sizeof(igraph_vector_t *) * hk->size);
  
  //igraph_vector_t *neigh = malloc(sizeof(igraph_vector_t) * hk->size);
  for (int v = 0; v < hk->size; v++){
    neighbors[v] = malloc(sizeof(igraph_vector_t));
    igraph_vector_init(neighbors[v], 0);
    //igraph_vector_init(&neigh[v], 0);
    //igraph_neighbors(graph, &neigh[v], v, IGRAPH_ALL);
    igraph_neighbors(graph, neighbors[v], v, IGRAPH_ALL);
    //neighbors[v] = &neigh[v];
  }
  //free(neigh);
  hk->adj_list = neighbors;
}

void initialize_inter_comm(Housekeeping *hk, igraph_t *graph){
  igraph_matrix_t mat;
  igraph_matrix_init(&mat, hk->size, hk->size);
  // TOOD: check IGRAPH_GET_ADJACENCY_UPPER vs BOTH
  igraph_get_adjacency(graph, &mat, IGRAPH_GET_ADJACENCY_UPPER, false);
  igraph_matrix_init(hk->inter_comm_edges, hk->a, hk->b);
  igraph_matrix_null(hk->inter_comm_edges);

  for (int row = 0; row < hk->size; row++){
    // just gets the lower (upper? check) triangular
    for (int col = row + 1; col < hk->size; col++){
      if (MATRIX(mat, row, col)){
        int group_r = hk->partition[row];
        int group_c = hk->partition[col];
        if (group_r < hk->a && group_c >= hk->a)
          MATRIX(*(hk->inter_comm_edges), group_r, group_c - hk->a)++;
        else if (group_r >= hk->a && group_r < hk->a)
          MATRIX(*(hk->inter_comm_edges), group_c, group_r - hk->a)++;
      }
    }
  }
  igraph_matrix_destroy(&mat);
}


void initialize_degree_sums(Housekeeping *hk){
  igraph_real_t *comm_degree = calloc(hk->a + hk->b, sizeof(igraph_real_t));
  for (int v = 0; v < hk->size; v++){
    comm_degree[hk->partition[v]] += igraph_vector_size(hk->adj_list[v]);//VECTOR(*deg)[v]; // += 1 for uncorrected.
  }
  hk->comm_tot_degree = comm_degree;
}

// todo: allow the user to supply an id or something in community a, so they aren't assigned arbitrarily.
void initialize_housekeeping(Housekeeping *hk, igraph_t *graph, igraph_integer_t k_a, igraph_integer_t k_b){
  hk->a = k_a;
  hk->b = k_b;
  hk->size = igraph_vcount(graph);
  initialize_types(hk, graph);
  printf("449. there are %ld types\n", igraph_vector_bool_size(hk->types));
  initialize_partition(hk);
  initialize_neighbors(hk, graph);
  initialize_inter_comm(hk, graph);

  for (int a = 0; a < hk->a; a++){
    for (int b = hk->a; b < hk->a + hk->b; b++){
      printf("Matrix %d, %d: %d\n", a, b, (int) INTERCOMMUNITY(*(hk->inter_comm_edges), a, b, hk->a));
    }
  }
  // must be called after neighbors is initialized
  initialize_degree_sums(hk);
}


void free_housekeeping(Housekeeping *hk){
  free(hk->partition);
  for (int i = 0; i < hk->size; i++){
    igraph_vector_destroy(hk->adj_list[i]);
    free(hk->adj_list[i]);
  }
  free(hk->adj_list);
  igraph_vector_bool_destroy(hk->types);
  igraph_matrix_destroy(hk->inter_comm_edges);
  free(hk->comm_tot_degree);

}


// TODO: do something better about degree 0 vertices.

 // TODO: include degree uncorrected option, modify algorithm to include weights.
int igraph_community_bipartite_sbm(igraph_t *graph, igraph_vector_t *membership, 
                                   igraph_integer_t k_a, igraph_integer_t k_b, 
                                   igraph_integer_t max_iters){
  Housekeeping hk;
  igraph_vector_bool_t types;
  hk.types = &types;
  igraph_matrix_t inter_comm_edges;
  hk.inter_comm_edges = &inter_comm_edges;

  initialize_housekeeping(&hk, graph, k_a, k_b);

  run_algorithm(&hk, max_iters);

  

  if (igraph_vector_size(membership) != hk.size)
    igraph_vector_resize(membership, hk.size);
  // todo: only use igraph_vector_t instead
  for (int i = 0; i < hk.size; i++)
    VECTOR(*membership)[i] = hk.partition[i];
  free_housekeeping(&hk);
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

  igraph_vector_t membership;
  igraph_vector_init(&membership, 0);
  igraph_community_bipartite_sbm(&graph, &membership, a, b, max_iters);



//   igraph_vector_t deg;
//   igraph_vector_init(&deg, igraph_vcount(&graph));
//   igraph_degree(&graph, &deg, igraph_vss_all(), IGRAPH_ALL, true);

//   printf("Deleting all vertices of degree 0...\n");
//   int num_lonely = delete_lonely_nodes(&graph, &deg);
//   printf("Deletion successful. %d nodes deleted.\n", num_lonely);

//   int size = igraph_vcount(&graph);

//   igraph_vector_bool_t types;
//   igraph_vector_bool_init(&types, size);

//   printf("Finding a bipartite mapping...\n");
//   igraph_bool_t is_bipartite;
//   igraph_is_bipartite(&graph, &is_bipartite, &types);
//   if (!is_bipartite){
//     printf("Input graph is not bipartite. Exiting...\n");
//     exit(ILLEGAL_FORMAT);
//   }
//   printf("Mapping successful.\n");

//   igraph_matrix_t mat;
//   igraph_matrix_init(&mat, size, size);
//   // TOOD: use IGRAPH_GET_ADJACENCY_UPPER instead, perhaps last param true?
//   igraph_get_adjacency(&graph, &mat, IGRAPH_GET_ADJACENCY_UPPER, false);



//   igraph_vector_t *neighbors[size];
//   initialize_neighbors(&graph, neighbors);

//   //igraph_vector_t partition;
//   //igraph_vector_init(&partition, size);
//   printf("Initializing to random groups...\n");
//   int partition[size];
//   initialize_groups(a, b, &types, partition);
//   printf("Initialization successful.\n");

//   igraph_matrix_t inter_comm;
//   igraph_matrix_init(&inter_comm, a, b);
//   initialize_inter_comm(&inter_comm, partition, &mat, a, size);


//   igraph_real_t comm_degree[a + b];
//   initialize_degree_sums(partition, comm_degree, &deg);



// // todo: replace all degree by neighbors

//   Housekeeping hk;
//   hk.a = a;
//   hk.b = b;
//   hk.size = size;
//   hk.partition = partition;
//   hk.adj_list = neighbors;
//   //hk.adj_mat = &mat;
//   hk.inter_comm_edges = &inter_comm;
//   hk.comm_tot_degree = comm_degree;

//   printf("Running algorithm...\n");
//   run_algorithm(&hk, max_iters);


  for (int i = 0; i < igraph_vcount(&graph); i++){
    printf("%d: %d\n", i, (int) VECTOR(membership)[i]);
  }


  igraph_vector_destroy(&membership);
  igraph_destroy(&graph);

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
