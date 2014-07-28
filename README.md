#Circulo


###Contribute
Contributors welcome!! If you would like to contribute to the research page, please issue a pull request.

###About
Circulo is an exploratory effort focusing on "Community Detection" in Graphs. Though there are many areas on the web that provide useful information on the subject matter, we found that there still lacked a single place where someone new to the field could learn.  The goal of this project, therefore, is to be a central place for advancing the field. We have divided the project into the following three areas:

- <b>Knowledge:</b>  Build a comprehensive knowledge base that includes details about the field of Community Detection, including but not limited to summaries of algorithms, references to academic literature, and general information about the field. To view the research page for Circulo please visit [http://lab41.github.io/Circulo](http://lab41.github.io/Circulo/)
- <b>Algorithms:</b> Implement algorithms using existing Graph frameworks such as iGraph. Many Graph frameworks today still do not implement Community Detection algorithms, or if they do, they only implement a narrow set of algorithms. The implementations can include weighted/unweighted, directed/undirected, and nonoverlapping/overlapping graphs to name a few.
- <b>Metrics:</b> Implement a set of evaulation metrics that can quantitativley assess the accuracy of a partitions of a Graph into communities. The metrics assess various attributes of Graph partitions including network-wide metrics and internal/external community metrics.


###Base Frameworks
Since we did not want to reimplement the notion of a graph, we decided to pick an existing framework as a backdrop for our work.  Though any of the popular graph frameworks could have been used, iGraph was chosen as our primary graph framework. iGraph offeres number of advantages:

- First and foremost, iGraph implements a number of community detection algorithms out of the box. It also provides two data structures for community detection: VertexClustering (non-overlapping communities) and VertexCover (overlapping communities)
- iGraph is written in C at its core making it fast
- iGraph has wrappers for Python and R
- iGraph is a mature framework

Other frameworks which could be used include GraphLab, SNAP, NetworkX.


###Setup
#####Requirements

-  python 3
-  igraph
-  matplotlib
-  cairo
-  scipy
-  scikit.learn
  


#####Circulo 
Below are instructions for using Circulo

	#clone Circulo repository
	git clone https://github.com/Lab41/circulo.git
	#set PYTHONPATH env variable
	export PYTHONPATH=/path/to/Circulo

#####iGraph
For Ubuntu

```
 sudo apt-get install igraph
 sudo apt-get install libxml2-dev libz-dev python-dev
```

For OS X, do the following. (NOTE: iGraph homepage is a good resource)
	
	#using brew install igraph
	brew install igraph
	
	#install Cairo
	#installs the core libraries for cairo
	brew install cairo 
	
	#installs the python site-packages. NOTE: pip does not work for pycairo. 
	#If you want to use pip, create sym links to the site packages in brew
	brew install py3cairo
