To view the research page for Circulo please visit [http://lab41.github.io/Circulo](http://lab41.github.io/Circulo/)

If you would like to contribute to the research page, please issue a pull request.


##Setup
Circulo uses a variety of frameworks. Below are instructions for installing them.

###iGraph
iGraph is the base Graph framework for Circulo. Currently, we are using a branch with modfications primarily related to metrics for evaluating clusters. To install follow the instructions below:

```
 git clone https://github.com/Lab41/igraph.git
 cd igraph
 git checkout working
 cd interfaces/python
 sudo apt-get install libxml2-dev libz-dev python-dev
	
 #requires libxml2-dev and libz-dev
 python setup.py install
```




