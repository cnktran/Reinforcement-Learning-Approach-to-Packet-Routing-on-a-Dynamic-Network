import networkx as nx
print("hi")
print("I am a talking computer")
G = nx.Graph()

#G.add_node(3)
G.add_edges_from([(1, 2), (5, 3)])
print(G.number_of_nodes())
print(G.number_of_edges())

# V simple random network generator
# See generated result in sidebar, folder icon > sample_network.pdf

from graph_tool.all import *
g = Graph()
node_count = 100
edge_count = 300
min_weight = 1
max_weight = 10