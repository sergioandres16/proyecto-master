from pyvis.network import Network
import networkx as nx
nx_graph = nx.cycle_graph(10)
nx_graph.nodes[1]['title'] = 'Number 1'
nx_graph.nodes[1]['group'] = 1
nx_graph.nodes[3]['title'] = 'I belong to a different group!'
nx_graph.nodes[3]['group'] = 10



nx_graph.add_node(30, size=20, label='n-2', group=4, color="green")
nx_graph.add_node(31, size=20, label='n-3', group=4, color="green")
nx_graph.add_node(32, size=20, label='n-1', group=4, color="green")
nx_graph.add_node(33, size=20, label='n-4', group=4, color="green")
nx_graph.add_node(34, size=20, label='n-5', group=4, color="green")
nx_graph.add_edge(32, 31, weight=10)
nx_graph.add_edge(32, 30, weight=10)
nx_graph.add_edge(32, 33, weight=10)
nx_graph.add_edge(32, 34, weight=10)

nx_graph.add_node(35, size=20, label='n-6', group=4, color="blue")
nx_graph.add_node(36, size=20, label='n-7', group=4, color="blue")
nx_graph.add_node(37, size=20, label='n-8', group=4, color="blue")
nx_graph.add_edge(35, 36, weight=10)
nx_graph.add_edge(35, 37, weight=10)

nt = Network('1000px', '1000px')
nt.from_nx(nx_graph)
nt.show('nx.html')

unir = input("unir? ")
if unir=="si":
    nx_graph.add_edge(32, 35, weight=10, color="red")
    nt.from_nx(nx_graph)
    nt.show('nx.html')

eliminar = input("eliminar? ")
if eliminar=="si":
    nx_graph.de
    nt.from_nx(nx_graph)
    nt.show('nx.html')