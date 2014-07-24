# Goal is to annotate a vertex cover with dictionary representing various cluster metrics

from igraph import Cover

def compute_metrics(cover):
    cover.metrics = { }
    pass

Cover.compute_metrics = compute_metrics
