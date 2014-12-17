#Circulo: A Community Detection Evaluation Framework

###Contribute
Contributors welcome! If you want to contribute, please issue a pull request.

##About
####The Framework:
<b>Circulo is a "Community Detection" Evaluation Framework</b> written primarily in Python.   The Framework performs statistical analysis against partitions of a Graph resulting from the execution of a given community detection algorithm.  The resulting quantitative measures can be used to drive experiments such as measuring algorithm efficacy against specific dataset types or comparing different algorithm execution results against the same dataset. The framework includes the following components:

- __Data ETL (Extract Transform Load) Engine__: Circulo includes functionality to incorporate existing datasets into the evaluation framework.  By default, the framework includes several dataset "downloaders" in the directory [circulo/data](circulo/data). To learn how to add a dataset, please see the data [README](circulo/data/README.md). We encourage users to issue pull requests for new datasets.
- __Algorithm Execution Engine:__  Circulo includes several algorithms by default which are located in the [algorithms](circulo/algorithms) directory. Using the framework, these algorithms can run in parallel against the included datasets by running the [run_algos.py](circulo/setup/run_algos.py) tool. Because some algorithms include parameters that can better cater execution to the type of input Graph (i.e directed and/or weighted), algorithm execution is wrapped in the file [community.py](circulo/wrappers/community.py). This enables the same algorithm to automatically operate differently depending on the dataset--enabling the algorithm to adapt to the dataset if allowed. To add an algorithm to the framework, add the files to [algorithms](circulo/algorithms) and update the wrapper [community.py](circulo/wrappers/community.py) appropriately.
- __Metrics Engine:__ The metrics engine provides quantitative analysis of a given partitionin g of a graph. The metrics include internal statistical measures of a community (i.e. density), external measurements (i.e. expansion), and network wide metrics (ground truth comparisons).  
- __Experiments Engine:__ Different types of experiments have been designed to find patterns in the metric results.  For example, how do algorithms compare when considering both time and accuracy. This component is meant to be a "playground" for experimentation on metric results. Experiments may vary significantly. Each file in the [experiments](experiments) directory is meant to be an independent experiment.  See the [README](experiment/README.md) for more information.

####The Research
 Prior to building the Circulo framework, Lab41 conducted a market survey into Community Detection algorithms and metrics. The survey was used to guide the development of Circulo. The survey includes, but is not limited to, summaries of algorithms, references to academic literature, and general information about the field. The survey can be found here: http://lab41.github.io/survey-community-detection/.


####The Underlying Graph Framework
Since we did not want to reimplement the notion of a graph, we decided to pick an existing Graph Framework as a backdrop for our work.  Though any of the popular graph frameworks could have been used, iGraph was chosen as our primary graph framework. iGraph offers a number of features:

- First and foremost, iGraph implements a number of community detection algorithms out of the box. It also provides two data structures for community detection: VertexClustering (non-overlapping communities) and VertexCover (overlapping communities)
- iGraph is written in C at its core making it fast
- iGraph has wrappers for Python and R
- iGraph is a mature framework

Other frameworks which could be used include GraphX, GraphLab, SNAP, NetworkX.


##Installation and Setup
####Package Requirements

-  git
-  python3
-  igraph (Refer to Appendix A for further instructions)
-  matplotlib
-  cairo (if you want to plot directly from igraph)
-  scipy
-  scikit.learn
  

####Installation
Below are instructions for using Circulo

	#clone Circulo repository (note: this also clone SNAP)
	git clone --recursive https://github.com/Lab41/circulo.git
	#set PYTHONPATH env variable
	export PYTHONPATH=/path/to/Circulo
    #make the snap code base
    pushd lib/snap; make; popd



#### Running the Evaluation Framework
At the core, the evaluation framework run various community detection algorithms against various datasets. 
	
	#To run your algorithms against the data
	python circulo/setup/run_algos [parameters ...]	
	#To run metrics against the results of run_algos
	python circulo/setup/run_metrics [parameters ...]

	

##Appendix
####Appendix A: iGraph Installation
#####Ubuntu

    sudo apt-get install igraph
    sudo apt-get install libxml2-dev libz-dev python-dev

#####OS X
	
	#using brew install igraph dylibs
	brew install homebrew/science/igraph
    
	#install Cairo
	#installs the core libraries for cairo
	brew install cairo 
	
	#installs the python site-packages. NOTE: pip does not work for pycairo. 
	#If you want to use pip, create sym links to the site packages in brew
	brew install py3cairo

    #install python igraph
    pip3 install python-igraph

