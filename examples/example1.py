
def example1():
    g = ig.load("data/out_1.graphml") # whichever file you would like
    dend = g.community_fastgreedy()

    #get the clustering object
    c = dend.as_clustering()


    result = metrics.run_analysis(c)

    print(c)


