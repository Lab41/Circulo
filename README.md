To view the research page for Circulo please visit [http://lab41.github.io/Circulo](http://lab41.github.io/Circulo/)

If you would like to contribute to the research page, please issue a pull request.


##Setup
Circulo uses a variety of frameworks. Below are instructions for installing them.

###iGraph
iGraph is the base Graph framework for Circulo. Currently, we are using a branch with modfications primarily related to metrics for evaluating clusters. To install follow the instructions below:

####Ubuntu
```
 git clone https://github.com/Lab41/igraph.git
 cd igraph
 git checkout working
 cd interfaces/python
 sudo apt-get install libxml2-dev libz-dev python-dev
 python setup.py install
```

####OS X
Refer to the iGraph homepage

Also will need py2cairo (for python 2.7.5)

To install with brew
    
    brew install cairo
    brew install py2cairo
- Note: Make sure you get cairo in your site-packages either by creating a symbolic link to the folder or adding the site-packages of brew to your system path


