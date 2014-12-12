The experiments are listed below:


#### Ground Truth Similarity Test
- File: __metrics_clustering.py__
- Goal: Determine if metrics applied to communities from Ground Truth are simialr when grouped with metrics of non Ground Truth communities. The experiemnt leverages kmeans clustering where the features are the metrics, and the observations are a set of features for a given community.
- __RUN__: python experiments/metrics_clustering.py metrics_dir dataset_name
- __RESULTS__:

#### Time vs Accuracy
- File: __metricsCharts.R__
- Function: plotRunOmega
- Goal: For a given data set with Ground Truth, measure how the result accuracy changes with certain algorithms, specifically taking into consideration executation time (time complexity)
- __RUN__: metrics <- getMetrics("/path/to/json/metrics", "dataset name (i.e. football)")
-          plotRunOmega(metrics)
- __RESULTS__:

#### Comparing algorithm results using Omega score
- File: __run_comparison.py__
- Goal: Creates csv files that use omega score to create a matrix of distances between the various results sets. Ground truth is treated as just another algorithm
- __RUN__: python3 run_comparison.py <Path to results json files> <output path for csv files> 
- __RESULTS__: 

#### Cluster Results of run_comparison.py
- File: cluster_omega_comparison.py
- Goal: Take results of run_comparison.py (distance matrix) and cluster results to find similar items
- __RUN__: python3 cluster_omega_comparison.py <path to csv file(s)> [--n <number of clusters desired>]

#### Histogram metrics across datasets
- File: histogram_metrics.py:
- Goal: This script allows you to compare the result of metrics across algorithms for a single dataset. It creates a histogram for each metric/algorithm pair showing the number of communities for that metric that fall into the specified bin. 
- __RUN__: python3 histogram_metrics.py <folder of your metrics json file> <Dataset desired i.e. amazon> [Optional: --metrics Density,Cohesiveness]
Results: 

#### Combine Results into single graphml file
- File: create_graphml.py
- Goal: Create a single graphml file that contains the results off the community detection algorithms as attributes on each vertex. This is useful for visualizing results in Gephi manually or running the java code in this directory to plot them automatically
- __RUN__: python3 create_graphml.py <path to results json files> <Path to graphs, typically circulo/circulo/data/GRAPHS> <output directory for new graphml files>
- __RESULTS__: Graphml files that have attritubes for each algorithm that describe which community they were placed in.




