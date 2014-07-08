import importlib
import igraph
import os

school_data_path = "../examples/school/data/out_1.graphml"


if !os.path.exists(school_data_path):
    f = importlib.import_module("examples.school.do_example")
    f.download()
    f.prepare()




G = igraph.load(school_data_path)

