/**
 * File: biSBM.c
 * -------------
 * See biSBM.h for detailed overview.
 */
#include "biSBM.h"

#define WRONG_OPTION_COUNT 1
#define UNKNOWN_GRAPH_TYPE 2
#define BAD_FILE 3
#define GRAPH_READ_FAILED 4
#define ILLEGAL_FORMAT 5

#define INTERCOMMUNITY(inter_comm, c_a, c_b, a) (MATRIX(inter_comm, c_a, c_b - a))


/**
 * TODO
 *     * change assert statements to something more graceful
 *     * possibly check for error code on all igraph calls. Bubble up error?
 *     * possibly replace c arrays with igraph_vector_t/igraph_vector_integer_t
 *     * implement non degree-corrected version
 *     * make things const when they need to be
 *     * do something to deal with degree 0 vertices (put them all in community -1 or something?)
 *     * make sure igraph_real_t always behaves nicely
 *     * possibly modify the algorithm to a weight corrected version
 *     * possibly return error codes from igraph_community_bipartite_SBM
 *     * parallelize on each vertex
 */


/**
 * Global: verbose
 * ---------------
 * If verbose == true, then logging statements are printed to standard out.
 */
bool verbose = true;


/**
 * Struct: Housekeeping
 * --------------------
 * This struct contains all information needed to calculate the scores
 * of a partition.
 */
typedef struct {
  // number of type a, number of type b, number of vertices
  int a, b, size; 
  // community membership list
  int *partition; 
  // true if we are using degree correction
  bool degree_correct; 
  // the graph in adjacency list format
  igraph_vector_t **adj_list; 
  // For each vertex i, false if types[i] is in group a, true if group b
  igraph_vector_bool_t *types; 
  // a matrix in which cell ab is the number of edges between community a and b
  igraph_matrix_t *inter_comm_edges;
  // For each community, the sum of the degree of all vertices in the community.
  igraph_real_t *comm_tot_degree; 
} Housekeeping;


/**
 * Struct: Swaprecord
 * ------------------
 * A Swaprecord contains the vertex id (v), its original community (src)
 * and the destination community (dest).
 */
typedef struct {
  int v, src, dest;
} Swaprecord;


/**
 * Function: score_partition
 * -------------------------
 * Given a partition stored in hk, scores the partition using the 
 * log-likelihood metric described in equation (16) of the paper. 
 *   Parameters:
 *     Housekeeping *hk: A struct Housekeeping containing all graph 
 *                       and community information
 *   Returns: 
 *     The score of the partition stored in hk.
 * 
 * TODO: implement non-degree corrected (equation 9).
 * TODO: implement change in score instead of total score for an optimization.
 * 
 */
static igraph_real_t score_partition(Housekeeping *hk){
  igraph_real_t score = 0;
  for (int c_a = 0; c_a < hk->a; c_a++){
    for (int c_b = hk->a; c_b < hk->a + hk->b; c_b++){
      igraph_real_t inter_community = INTERCOMMUNITY(*(hk->inter_comm_edges), c_a, c_b, hk->a);
      igraph_real_t c_a_sum = hk->comm_tot_degree[c_a];
      igraph_real_t c_b_sum = hk->comm_tot_degree[c_b];

      // todo: put in degree correction stuff here. currently hk->degree_correct
      if (!(int) inter_community || !(int) c_a_sum || !(int) c_b_sum) return -INFINITY;
      score += inter_community * log(inter_community / (c_a_sum * c_b_sum));
    }
  }
  return score;
}


/**
 * Function: make_swap
 * -------------------
 * Swaps vertex v from its current community to the new community  `to`.
 * All changes are reflected in hk.
 *   Parameters:
 *     Housekeeping *hk: A struct Housekeeping containing all graph 
 *                       and community information
 *     int v: The index of the vertex to be swapped.
 *     int to: the community to which v is to be swapped.
 */
static void make_swap(Housekeeping *hk, int v, int to){
  int from = hk->partition[v];
  if (to == from) return;
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


/**
 * Function: score_swap
 * --------------------
 * A naive scoring method that actually makes the swap that we
 * aim to score, scores the partition, then swaps back. Returns
 * the score.
 *   Parameters:
 *     Housekeeping *hk: A struct Housekeeping containing all graph 
 *                       and community information
 *     int v: The index of the vertex to be swapped for scoring.
 *     int to: the community to which v is to be swapped for scoring.
 *   Returns: 
 *     The score of the partition after the swap specified by the parameters.
 *  
 * TODO: optimize this to not actually make the swaps.
 */
static double score_swap(Housekeeping *hk, int v, int to){
  int tmp = hk->partition[v];
  make_swap(hk, v, to);
  double score = score_partition(hk);
  make_swap(hk, v, tmp);
  return score;
}


/**
 * Function: score_swaps
 * ---------------------
 * Given a vertex v, populates dest with the best community to change to.
 * Returns the score if swapped to dest.
 *   Parameters:
 *     Housekeeping *hk: A struct Housekeeping containing all graph 
 *                       and community information
 *     int v: The index of the vertex to be swapped for scoring.
 *     int *dest: A pointer to an uninitialized int where the best swap will be stored.
 *   Returns: 
 *     The score of the optimal swap for v. 
 *  
 */
static double score_swaps(Housekeeping *hk, int v, int *dest){
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
    double new_score = score_swap(hk, v, to);
    if (new_score > best_score){
      best_score = new_score;
      *dest = to;
    }
  }
  return best_score;
}


/**
 * Function: make_best_swap
 * ------------------------
 * This function tries all possible swaps of all unused vertices to all communities,
 * then makes the best one. Returns the score after this optimal swap.
 * Takes a housekeeping struct, a bool array representing whether each vertex has been 
 * used, an array of swaprecords to give the ability to rewind to the best swap, and 
 * and int i representing the swap number that we're on. 
 *   Parameters:
 *     Housekeeping *hk: A struct Housekeeping containing all graph 
 *                       and community information
 *     bool *used: An array of length hk->size where used[i] is false if vertex i is in 
 *                 group a, true if group b.
 *     Swaprecord *swaprecord: An array of swaprecords in order, each representing one swap.
 *     int i: the number of vertices already swapped, and the swaprecord index.
 *   Returns:
 *     The score of the partition after the best swap.
 *  
 */
static double make_best_swap(Housekeeping *hk, bool *used, Swaprecord *swaprecord, int i){
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


/**
 * Function: rewind_swaps
 * ----------------------
 * Given an array of Swaprecords along with the index in that array best_swap,
 * swaps vertices back and updates housekeeping to reflect the best swap for the
 * current iteration.
 */
static void rewind_swaps(Housekeeping *hk, Swaprecord *swaprecord, int best_swap){
  for (int i = hk->size - 1; i > best_swap; i--){
    make_swap(hk, swaprecord[i].v, swaprecord[i].src);
  }
}


/**
 * Function: run_iteration
 * -----------------------
 * Runs the algorithm one iteration forward. If it improves the score, 
 * return false, otherwise return true.
 */
static bool run_iteration(Housekeeping *hk, double init_score){
  bool used[hk->size];
  Swaprecord swaprecord[hk->size];
  int best_swap = -1;
  for (int i = 0; i < hk->size; i++) used[i] = false;
  for (int i = 0; i < hk->size; i++){ 
    double new_score = make_best_swap(hk, used, swaprecord, i);
    if (new_score > init_score){
      init_score = new_score;
      best_swap = i;
    }
  }
  rewind_swaps(hk, swaprecord, best_swap);
  if (best_swap == -1)
    return true;
  return false;
}


/**
 * Function: run_algorithm
 * -----------------------
 * Run the bipartite SBM algorithm a maximum of max_iters iterations.
 */
static double run_algorithm(Housekeeping *hk, int max_iters){
  double score = score_partition(hk);
  log_message("Initial score: %f\n", score);
  for (int i = 0; i < max_iters; i++){
    log_message("Beginning iteration %d\n", i + 1);
    bool is_last_iteration = run_iteration(hk, score);
    score = score_partition(hk);
    log_message("Score after iteration %d: %f\n", i + 1, score);
    if (is_last_iteration){
      log_message("Score has not improved. Terminating...\n");
      return score;
    }
  }
  return score;
}


/**
 * Function: initialize_types
 * --------------------------
 * Attempts to find a bipartite mapping of the graph, and loads such
 * a mapping (if it exists) into hk->types. 
 */
static void initialize_types(Housekeeping *hk, igraph_t *graph){
  igraph_vector_bool_init(hk->types, hk->size);
  log_message("Finding a bipartite mapping...\n");
  igraph_bool_t is_bipartite;
  igraph_is_bipartite(graph, &is_bipartite, hk->types);
  if (!is_bipartite){
    log_message("Input graph is not bipartite. Exiting...\n");
    exit(ILLEGAL_FORMAT);
  }
  log_message("Mapping successful.\n");
}


/**
 * Function: initialize_partition
 * ------------------------------
 * Randomly initializes hk->partition such that all vertices of type
 * a are assigned a community 0 < c < k_a and all vertices of type b
 * are assigned a community k_a <= c < k_b.
 */
static void initialize_partition(Housekeeping *hk){
  int *partition = malloc(sizeof(int) * hk->size);
  assert(partition != NULL);
  igraph_rng_t *rng = igraph_rng_default();
  // assign seed to some constant for repeatable results.
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


/**
 * Function: initialize_neighbors
 * ---------------------------
 * Assigns hk->adj_list as an adjacency list representation of the graph.
 */
static void initialize_neighbors(Housekeeping *hk, igraph_t *graph){
  igraph_vector_t **neighbors = malloc(sizeof(igraph_vector_t *) * hk->size);
  assert(neighbors != NULL);
  for (int v = 0; v < hk->size; v++){
    neighbors[v] = malloc(sizeof(igraph_vector_t));
    assert(neighbors[v] != NULL);
    igraph_vector_init(neighbors[v], 0);
    igraph_neighbors(graph, neighbors[v], v, IGRAPH_ALL);
  }
  hk->adj_list = neighbors;
}


/**
 * Function: initialize_inter_comm
 * -------------------------------
 * Initializes an A x B matrix hk->inter_comm_edges such that 
 * inter_comm_edges[A][B] = the number of intercommunity edges from A to B.
 * since the graph is undirected, only initializes the upper trianglular portion. 
 */
static void initialize_inter_comm(Housekeeping *hk, igraph_t *graph){
  igraph_matrix_t mat;
  igraph_matrix_init(&mat, hk->size, hk->size);
  igraph_get_adjacency(graph, &mat, IGRAPH_GET_ADJACENCY_UPPER, false);
  igraph_matrix_init(hk->inter_comm_edges, hk->a, hk->b);
  igraph_matrix_null(hk->inter_comm_edges);
  for (int row = 0; row < hk->size; row++){
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


/**
 * Function: initialize_degree_sums
 * --------------------------------
 * Initializes an array hk->comm_tot_degree where comm_tot_degree[i] = the total degree of all vertices
 * in community i.
 */
static void initialize_degree_sums(Housekeeping *hk){
  igraph_real_t *comm_degree = calloc(hk->a + hk->b, sizeof(igraph_real_t));
  assert(comm_degree != NULL);
  for (int v = 0; v < hk->size; v++){
    comm_degree[hk->partition[v]] += igraph_vector_size(hk->adj_list[v]);//VECTOR(*deg)[v]; // += 1 for uncorrected.
  }
  hk->comm_tot_degree = comm_degree;
}


/**
 * Function: initialize_housekeeping
 * ---------------------------------
 * Initializes all data structures needed to run the algorithm.
 * todo: allow the user to supply an id or something in community a, so they aren't assigned arbitrarily.
 */
static void initialize_housekeeping(Housekeeping *hk, igraph_t *graph, igraph_integer_t k_a, igraph_integer_t k_b){
  hk->a = k_a;
  hk->b = k_b;
  hk->size = igraph_vcount(graph);
  initialize_types(hk, graph);
  initialize_partition(hk);
  initialize_neighbors(hk, graph);
  initialize_inter_comm(hk, graph);
  initialize_degree_sums(hk);
}


/**
 * Function: free_housekeeping
 * ---------------------------
 * Frees all allocated memory in housekeeping.
 */
static void free_housekeeping(Housekeeping *hk){
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


/**
 * Function: igraph_community_bipartite_sbm
 * ----------------------------------------
 * Runs the algorithm. See biSBM.h for detailed overview.
 */
int igraph_community_bipartite_sbm(igraph_t *graph, igraph_vector_t *membership, 
                                   igraph_integer_t k_a, igraph_integer_t k_b, 
                                   igraph_integer_t max_iters, igraph_bool_t degree_correct){
  Housekeeping hk;
  igraph_vector_bool_t types;
  hk.types = &types;
  igraph_matrix_t inter_comm_edges;
  hk.inter_comm_edges = &inter_comm_edges;
  hk.degree_correct = degree_correct;
  initialize_housekeeping(&hk, graph, k_a, k_b);
  run_algorithm(&hk, max_iters);
  if (igraph_vector_size(membership) != hk.size)
    igraph_vector_resize(membership, hk.size);
  for (int i = 0; i < hk.size; i++)
    VECTOR(*membership)[i] = hk.partition[i];
  free_housekeeping(&hk);
  return 0;
}


/******************************************************************************
*******************************************************************************
*****************************COMMAND LINE INTERFACE****************************
*******************************************************************************
******************************************************************************/


/**
 * Struct: Arglist
 * ---------------
 * Struct containing all of the command line arguments.
 */
typedef struct {
  char *graph_type;
  char *path_to_graph;
  int k_a;
  int k_b;
  int max_iters;
  bool degree_correct;
} Arglist;


/**
 * Function: log_message
 * ---------------------
 * Same interface as printf, but only prints if verbose=true.
 */
int log_message(const char *message, ...){
  if (verbose){
    int retval;
    va_list args;
    va_start(args, message);
    retval = vprintf(message, args);
    va_end(args);
    return retval;
  }
  return 0;
}


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
    log_message("Could not open file: %s\n", file_name);
    print_usage_and_exit(BAD_FILE);
  }
  if (!strcmp(type, "gml")){
    log_message("Attempting to read in .gml file...\n");

    // TODO: this function segfaults when it fails. Submit a bugfix!
    // As such, err isn't doing anything. There also seems to be a 
    // memory leak in this function.
    int err = igraph_read_graph_gml(graph, infile);
    fclose(infile);
    if (err) exit(GRAPH_READ_FAILED);
    return;
  }
  if (!strcmp(type, "graphml")){
    log_message("Attempting to read in graphml file...\n");

    // TODO: this function aborts when it fails, so err isn't doing
    // anything.
    int err = igraph_read_graph_graphml(graph, infile, 0);
    fclose(infile);
    if (err) exit(GRAPH_READ_FAILED);
    return;
  }
  if (!strcmp(type, "edgelist")){
    log_message("Attempting to read in edgelist file...\n");

    // TODO: this function aborts the process when it fails, so err isn't doing
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
  printf("  ./working_biSBM [graph type] [path to graph] [K_a] [K_b] [max iterations] [degree correct] [verbose]\n");
  printf("  Where graph type is one of:\n");
  printf("    gml\n");
  printf("    graphml\n");
  printf("    edgelist\n");
  // //TODO: ADD SUPPORT FOR MORE
  printf("  K_a is the number of groups of type a\n");
  printf("  K_b is the number of groups of type b\n");
  printf("  max iterations is the maximum number of iterations that the algorithm will attempt.\n");
  printf("  degree correct (optional) is 1 to use degree correction and 0 otherwise. Default: 1.\n");
  printf("  verbose (optional) is 1 to activate logging and 0 otherwise. Default: 1.\n\n");
  exit(exitstatus);
}


/**
 * Function: parse_args
 * --------------------
 * Takes user input and returns an Arglist struct containing the
 * options specified. Note: does **not** do agressive error checking. 
 */
Arglist parse_args(int argc, char **argv){
  if (argc < 6){
    printf("Too few arguments.\n");
    print_usage_and_exit(WRONG_OPTION_COUNT);
  }
  if (argc > 8)
    printf("Ignoring extra arguments...");
  Arglist args;
  args.graph_type = argv[1];
  args.path_to_graph = argv[2];
  args.k_a = atoi(argv[3]);
  args.k_b = atoi(argv[4]);
  args.max_iters = atoi(argv[5]);
  args.degree_correct = true;
  if (argc >= 7)
    args.degree_correct = (bool) atoi(argv[6]);
  if (argc >= 8)
    verbose = (bool) atoi(argv[7]);
  return args;
}


/**
 * Function: print_membership
 * --------------------------
 * Prints the membership list.
 */
void print_membership(igraph_vector_t *membership, int size){
  log_message("Membership: ");
  for (int i = 0; i < size; i++){
    log_message("%d ", (int) VECTOR(*membership)[i]);
  }
  log_message("\n");
}


/**
 * Function: delete_lonely_nodes
 * -----------------------------
 * NOT CURRENTLY USED. Given a graph and a vector containing the degree
 * of each node, deletes all nodes with 0 degree. Returns the number of 
 * nodes deleted.
 */
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
  igraph_vector_destroy(&lonely_ids);
  return num_lonely;
}


int main(int argc, char *argv[]){
  Arglist args = parse_args(argc, argv);

  igraph_t graph;
  igraph_read_graph_generic(&graph, args.graph_type, args.path_to_graph);
  log_message("Graph with %d vertices and %d edges read successfully.\n"
            , igraph_vcount(&graph), igraph_ecount(&graph)); 

  igraph_vector_t membership;
  igraph_vector_init(&membership, 0);
  igraph_community_bipartite_sbm(&graph, &membership, args.k_a, args.k_b, args.max_iters, args.degree_correct);

  print_membership(&membership, igraph_vcount(&graph));

  igraph_vector_destroy(&membership);
  igraph_destroy(&graph);
  return 0;
}
