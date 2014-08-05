/**
 *
 *
 */

#include <iostream>
#include <fstream>
#include <stdio.h>
// TODO move to .h

#include "working_biSBM.h"

#define WRONG_OPTION_COUNT 1
#define UNKNOWN_GRAPH_TYPE 2
#define BAD_FILE 3
#define GRAPH_READ_FAILED 4


using namespace std;


void load_graph(igraph_t *graph, char* type, char* file_name){
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
  // add more!
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
  cout << "  ./working_biSBM [graph type] [path to graph]" << endl;
  cout << "  Where graph type is one of:" << endl;
  cout << "    gml" << endl;
  cout << "    graphml" << endl;
  //TODO: ADD SUPPORT FOR MORE
  cout << endl;
  exit(exitstatus);
}


int main(int argc, char *argv[]) {
  if (argc != 3)
    print_usage_and_exit(WRONG_OPTION_COUNT);
  igraph_t graph;
  load_graph(&graph, argv[1], argv[2]);
  return 0;
}

// /**
//  * Constructor: BipartiteSBM
//  * -------------------------
//  * TODOTODOTODO
//  */
// BipartiteSBM::BipartiteSBM(int argc, char *argv[]) {
  
// }

// *
//  * Destructor: ~BipartiteSBM
//  * -------------------------
//  * TODOTODOTODO
 
// BipartiteSBM::~BipartiteSBM() {

// }

// void BipartiteSBM::run() {
//   cout << "running" << endl;
//   cout << test(53) << endl;
// }

// int BipartiteSBM::test(int n) {
//   return n;
// }
