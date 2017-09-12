import itertools
import networkx as nx
import graphviz
from collections import defaultdict

from scrape_most_depended_upon import get_first_n_depended_upon_packages
from picklehelper import unpickle

# Choose a file to unpickle here (generated in scrape_api.py)
num_packages = 72
graph = unpickle(f'top-{num_packages}-packages-no-dev.pickle')

base_packages = list(get_first_n_depended_upon_packages(num_packages))


def analyze(graph, base_packages):
    num_immediate_deps_broken_by_dependency = defaultdict(lambda: 0)
    base_packages_broken_by_dependency = defaultdict(set)

    for bp in base_packages:
        for id in graph[bp]:
            for dependency in nx.dfs_tree(graph, id).nodes():
                base_packages_broken_by_dependency[dependency].add(bp)
                num_immediate_deps_broken_by_dependency[dependency] += 1
    sorted_dependencies = sorted(graph.nodes(),
                    key=lambda d: (len(base_packages_broken_by_dependency[d]), num_immediate_deps_broken_by_dependency[d]),
                    reverse=True)
    # dependencies_with_scores = [
    #     (d, len(base_packages_broken_by_dependency[d]), num_immediate_deps_broken_by_dependency[d])
    #     for d in graph.nodes()
    # ]
    #
    # sorted_with_scores = sorted(dependencies_with_scores, key=lambda with_score: with_score[1:], reverse=True)
    # return sorted_with_scores
    return sorted_dependencies


def render_for_base_packages(graph, base_packages):
    new_graph = nx.DiGraph()
    for base_package in base_packages:
        for f, t in nx.bfs_edges(graph, base_package):
            new_graph.add_edge(f, t)
    render(new_graph, '-'.join(sorted(base_packages)))


def render_intersection(graph, package_1, package_2):
    subgraph_1 = subgraph_for_package(graph, package_1)
    subgraph_2 = subgraph_for_package(graph, package_2)
    shared = shared_nodes(subgraph_1, subgraph_2)
    gv_graph = graphviz.Digraph(engine='dot')
    union_graph = nx.DiGraph()
    union_graph.add_edges_from(subgraph_1.edges_iter())
    union_graph.add_edges_from(subgraph_2.edges_iter())

    for node in union_graph.nodes_iter():
        if node in shared:
            gv_graph.node(node, style='filled', fillcolor='pink')
        else:
            gv_graph.node(node)
    for from_node, to_node in union_graph.edges_iter():
        gv_graph.edge(from_node, to_node)
    graph_name = '-'.join(sorted([package_1, package_2]))
    with open(f'{graph_name}.png', 'wb') as graph_file:
        graph_file.write(gv_graph.pipe('png'))


def render(graph, name, highlights=set(), fmt='png', highlight_style={'fillcolor': 'pink'}):
    gv_graph = graphviz.Digraph(name, engine='neato')
    for node in graph.nodes_iter():
        if node in highlights:
            gv_graph.node(node, shape='point', **highlight_style)
        gv_graph.node(node, shape='point')
    for from_node, to_node in graph.edges_iter():
        gv_graph.edge(from_node, to_node)
    with open(f'{name}.{fmt}', 'wb') as graph_file:
        graph_file.write(gv_graph.pipe(fmt))



def subgraph_for_package(full_graph, package):
    new_graph = nx.DiGraph()
    new_graph.add_edges_from(nx.bfs_edges(full_graph, package))
    return new_graph


def shared_nodes(g1, g2):
    return set(g1.nodes_iter()) & set(g2.nodes_iter())


results = analyze(graph, base_packages)

results_names = [r[0] for r in results]
print(', '.join(r[0] for r in results[:5]))
print(results_names.index('supports-color'))
print(len(results))
for name, influence, impact in results[-5:]:
    print(f'{name} & {influence} & {impact}\\\\')
# render(graph, 'whole-graph', highlights=results[:10], fmt='svg')

def base_packages_using(dependency):
    return {b for b in base_packages if dependency in set(nx.dfs_tree(graph, b).nodes())}


# uses_inherits = {b for b in base_packages if 'inherits' in set(nx.dfs_tree(graph, b).nodes())}
#print(uses_inherits)
#render(graph, 'inherits-highlighted', set(nx.bfs_successors(graph, 'inherits')))
