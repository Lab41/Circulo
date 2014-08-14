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






// double calculate_term(int *partition, igraph_t *graph, igraph_matrix_t *mat, int r, int s, igraph_eit_t *eit){
//   int m_rs = 0;
//   int k_r = 0;
//   int k_s = 0;
//   igraph_real_t r_type[igraph_vcount(graph)];
//   int r_len = 0;
//   igraph_real_t s_type[igraph_vcount(graph)];
//   int s_len = 0;

//   for (int v = 0; v < igraph_vcount(graph); v++){
//     if (partition[v] == r){
//       r_type[r_len] = v;
//       r_len++;
//     }
//     else if (partition[v] == s){
//       s_type[s_len] = v;
//       s_len++;
//     }
//   }

//   //igraph_bool_t res;

//   for (int vr = 0; vr < r_len; vr++){
//     for (int vs = 0; vs < s_len; vs++){
//       // do something else, this is really slow.
//       if (MATRIX(*mat, (int) r_type[vr], (int) s_type[vs])){
//       //  printf("here\n");
//         m_rs++;
//       }
//       // igraph_are_connected(graph, r_type[vr], s_type[vs], &res);
//       // if (res)
//       //   m_rs++;
//     }
//   }

//   const igraph_vector_t r_view;
//   igraph_vector_view(&r_view, r_type, r_len);

//   const igraph_vector_t s_view;
//   igraph_vector_view(&s_view, s_type, s_len);

//   igraph_vector_t r_deg;
//   igraph_vector_t s_deg;
//   igraph_vector_init(&r_deg, r_len);
//   igraph_vector_init(&s_deg, s_len);

//   // assumes there are no loops, so it doesn't hurt to count them.
//   // also assumes undirected.
//   igraph_degree(graph, &r_deg, igraph_vss_vector(&r_view), IGRAPH_OUT, true);
//   igraph_degree(graph, &s_deg, igraph_vss_vector(&s_view), IGRAPH_OUT, true);

//   for (int i = 0; i < r_len; i++)
//     k_r += VECTOR(r_deg)[i];
//   for (int i = 0; i < s_len; i++)
//     k_s += VECTOR(s_deg)[i];
//   //printf("m_rs: %d, %d, %d\n", m_rs, k_r, k_s);
//   igraph_vector_destroy(&r_deg);
//   igraph_vector_destroy(&s_deg);
//   // // check
//   if (k_r * k_s == 0) return -INFINITY;
//   if (m_rs == 0) return -INFINITY;
 
//   double term_2 = log((double) m_rs / (double) (k_r * k_s));
//   //printf("term2: %f\n", term_2);
//   return m_rs * term_2;

//   // check to see if igraph_edge would be faster using the iterator below
//   // IGRAPH_EIT_RESET(eit);
//   // for (int e = 0; e < IGRAPH_EIT_SIZE(eit); e++){
//   //   IGRAPH_EIT_NEXT(eit);
//   //   IGRAPH_EIT_GET(eit);
//   // }
//   // TODO: check if igraph_es_fromto is implemented yet.

// }


// /**
//  * Function: score_partition
//  * -------------------------
//  * TODO
//  */
//  // TODO: should be able to score whole thing once then make minor modifications
//  // with individual switches.
// double score_partition_degree_corrected(int *partition, igraph_t *graph, igraph_matrix_t *mat, int a, int b){
//   //printf("scoring...\n");
//   double log_likelihood = 0;
//   igraph_es_t es;
//   igraph_es_all(&es, IGRAPH_EDGEORDER_FROM);
//   igraph_eit_t eit;
//   igraph_eit_create(graph, es, &eit);
//   for (int r = 0; r < a; r++){
//     for (int s = a; s < a + b; s++){
//       log_likelihood += calculate_term(partition, graph, mat, r, s, &eit);
//     }
//   }
//   igraph_eit_destroy(&eit);
//   return log_likelihood;
// }


// /**
//  * Function: swap_and_score
//  * ------------------------
//  * Scores the partition `partition` where partition[v] = group. 
//  * If the group assignment is illegal, returns -1. 
//  */
// double swap_and_score(int *partition, int v, int a, int b, int group, igraph_t *graph, igraph_matrix_t *mat){
//   // the swap wouldn't do anything or it would swap to the wrong type
//   if ((partition[v] == group) || (partition[v] < a && group >= a) || (partition[v] >= a && group < a)){
//     return -INFINITY;
//   }
//   int temp = partition[v];
//   partition[v] = group;
//   double score = score_partition_degree_corrected(partition, graph, mat, a, b);
//   partition[v] = temp;
//   return score;
// }


// // double compute_likelihood_change(int v, int from, int to){
// //   if (from == to) return 0;


// // }



// *
//  * Function: make_best_switch
//  * --------------------------
//  * Tries all possible switches between all vertices and groups of the same type.
//  * Modifies `partition` to reflect the best switch and `used` to store the vertex switched.
//  * Returns the score of the switch made.
 
// double make_best_switch(int *partition, int a, int b, igraph_vector_bool_t *types, igraph_t *graph, igraph_matrix_t *mat, bool *used){
//   int best_switch_vertex = -1;
//   int best_switch_group = -1;
//   double best_switch_score = -INFINITY; 
//   for (int v = 0; v < igraph_vector_bool_size(types); v++){
//     if (used[v]){ // can't swap because we've already swapped this vertex.
//       continue; // meh. don't do it this way. TODO
//     }
//     double best_curr_score = -INFINITY;
//     int best_curr_group = -1;
//     for (int group = 0; group < a + b; group++){
//       // Try swapping with all other groups
//       double score = swap_and_score(partition, v, a, b, group, graph, mat);
//       if (score >= best_curr_score){
//         best_curr_score = score;
//         best_curr_group = group;
//       }
//     }
//     if (best_curr_score >= best_switch_score){
//       best_switch_vertex = v;
//       best_switch_group = best_curr_group;
//       best_switch_score = best_curr_score;
//     }
//   }
//   // modify partition to reflect the best swap.
//   partition[best_switch_vertex] = best_switch_group;
//   used[best_switch_vertex] = true;
//   return best_switch_score;
// }


// /**
//  * Function: iterate_once
//  * ----------------------
//  * Given some initial state described in `partition`, moves all vertices once to attempt to maximize
//  * the MLE described in the paper. Returns the maximum score, and stores the grouping that yields
//  * that score in `partition`.
//  */
// double iterate_once(int *partition, int a, int b, igraph_vector_bool_t *types, igraph_t *graph, igraph_matrix_t *mat){
//   //int *working_partition = malloc(sizeof(int) * igraph_vector_bool_size(types)); // TODO: allocate on stack
//   int working_partition[igraph_vector_bool_size(types)];
//   memcpy(working_partition, partition, sizeof(int) * igraph_vector_bool_size(types));

//   double max_score = -INFINITY;
//   int num_used = 0;

//   // initialize to 0
//   bool used[igraph_vector_bool_size(types)];
//   for (int i = 0; i < igraph_vector_bool_size(types); i++) used[i] = false;
//   // bool *used = calloc(igraph_vector_bool_size(types), sizeof(bool)); // TODO: allocate on stack

//   while (num_used < igraph_vector_bool_size(types)){
//     double new_score = make_best_switch(working_partition, a, b, types, graph, mat, used);
//     if (new_score > max_score){
//       max_score = new_score;
//       memcpy(partition, working_partition, sizeof(int) * igraph_vector_bool_size(types));
//     }
//     num_used++;
//     printf("Used: %d\n", num_used);
//   }
//   return max_score;
// }


// /**
//  * Function: run_algorithm
//  * -----------------------
//  * Attempts to run the biSBM algorithm from the initialization state `partition` for a maximum of
//  * max_iters iterations. See the paper for more information.
//  * http://danlarremore.com/pdf/2014_LCJ_EfficientlyInferringCommunityStructureInBipartiteNetworks_PRE.pdf
//  */
// double run_algorithm(int *partition, int a, int b, igraph_vector_bool_t *types, igraph_t *graph, igraph_matrix_t *mat, int max_iters){
//   int latest_grouping[igraph_vector_bool_size(types)];

//   memcpy(latest_grouping, partition, sizeof(int) * igraph_vector_bool_size(types));

//   double score = score_partition_degree_corrected(partition, graph, mat, a, b);
//   printf("Initial score: %f\n", score);
//   for (int i = 0; i < max_iters; i++){
//     printf("Performing iteration %d...\n", i);
//     double new_score = iterate_once(latest_grouping, a, b, types, graph, mat);


//     if (new_score <= score) {
//       printf("Score has not improved. Terminating algorithm.\n");
//       // partition is not changed
//       return score;
//     }
//     printf("new score: %f\n", new_score);

//     score = new_score;
//     // partition is improved to latest_grouping!
//     memcpy(partition, latest_grouping, sizeof(int) * igraph_vector_bool_size(types));
//   }
//   return score;
// }













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
  printf("to: %d, from: %d\n", to, from);
  hk->partition[v] = to;
  igraph_vector_t *neighbors = hk->adj_list[v];
  int degree = igraph_vector_size(neighbors);
  hk->comm_tot_degree[from] -= degree;
  hk->comm_tot_degree[to] += degree;
  int c_1 = v;
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
  make_swap(hk, v, to);
  double score = score_partition(hk);
  make_swap(hk, to, v);
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
    double new_score = score_swap(hk, v, to);
    if (new_score > best_score){
      best_score = new_score;
      *dest = to;
    }
  }
  return best_score;
}



void make_best_swap(Housekeeping *hk, bool *used){
  int max_v = -1;
  int max_score = -INFINITY;
  int max_swap = -1;
  for (int v = 0; v < hk->size; v++){
    if (used[v]) continue;
    int dest;
    double score = score_swaps(hk, v, &dest);
    printf("New score: %f, vertex: %d, from: %d, to: %d\n", score, v, hk->partition[v], dest);
    if (score > max_score){
      
      max_score = score;
      max_swap = dest;
      max_v = v;
    }
  }
  printf("here\n");
  make_swap(hk, max_v, max_swap);
  assert(max_v >= 0);
  assert(max_swap >= 0); 
  used[max_v] = true;

}


void run_iteration(Housekeeping *hk){
  bool used[hk->size];
  for (int i = 0; i < hk->size; i++) used[i] = false;
  for (int i = 0; i < hk->size; i++){ 
    make_best_swap(hk, used);
  }
}







double run_algorithm(Housekeeping *hk, int max_iters){
  double score = score_partition(hk);
  printf("Initial score: %f\n", score);
  for (int i = 0; i < max_iters; i++){
    printf("Beginning iteration %d\n", i + 1);
    run_iteration(hk);
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
  int seed = time(NULL); 
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
