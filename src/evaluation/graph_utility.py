def compute_graph_utility(graph_chunks, vector_chunks):
    graph_set = set(graph_chunks)
    vector_set = set(vector_chunks)

    if not graph_set:
        return "FAILED"

    if graph_set == vector_set:
        return "UNCHANGED"

    if graph_set.issubset(vector_set):
        return "CONSTRAINED"

    if graph_set.issuperset(vector_set):
        return "EXPANDED"

    return "MIXED"
