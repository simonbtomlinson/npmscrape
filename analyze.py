import pickle
import networkx as nx
import graphviz

def unpickle(file):
    with open(file, 'rb') as pickle_file:
        return pickle.load(pickle_file)

# Choose a file to unpickle here (generated in scrape_api.py)
graph = unpickle('top-packages-no-dev.pickle')

# Do some analysis
ec = nx.eigenvector_centrality(graph)

print(sorted(graph.nodes(), key=lambda node: -ec[node])[0:30])
print(len(graph.nodes()))


def render(graph, name):
    gv_graph = graphviz.Digraph(name, engine='neato')
    for node in graph.nodes_iter():
        gv_graph.node(node, shape='point')
    for from_node, to_node in graph.edges_iter():
        gv_graph.edge(from_node, to_node)
    with open(f'{name}.svg', 'wb') as graph_file:
        graph_file.write(gv_graph.pipe('svg'))

render(graph, 'top-packages')