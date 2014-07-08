


def example0():
    """
    Performs the example outlined in the README. Draws the graph of one dataset.
    """
    g = ig.load("data/out_1.graphml") # whichever file you would like

    # Assigning colors to genders for plotting
    colorDict = {"M": "blue", "F": "pink", "Unknown": "black"}

    for vertex in g.vs:
        # each vertex is labeled as its classname and colored as its gender.
        vertex["label"] = vertex["classname"]
        vertex["color"] = colorDict[vertex["gender"]]


    layout = g.layout("fr") # Fruchterman-Reingold layout

    # If Cairo is improperly installed, raises TypeError: plotting not available
    try:
        ig.plot(g, layout=layout)
    except TypeError as e:
        print("It looks like Cairo isn't properly installed. Refer to the wiki.")
        exit(1)


