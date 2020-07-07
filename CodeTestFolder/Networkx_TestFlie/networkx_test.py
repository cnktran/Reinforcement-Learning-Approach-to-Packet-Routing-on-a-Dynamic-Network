# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 21:36:29 2020

@author: hltung
"""

import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from random import sample
from random import randint
import time

num_nodes = 10000
num_edges = 2500
min_weight = 1
max_weight = 10


#create list of edges
no_weights = sample(list(combinations(range(1,num_nodes),2)),num_edges)
e_list = []

for e in no_weights:
    e_list.append((e[0], e[1], randint(min_weight, max_weight)))

start = time.time()

DG = nx.DiGraph() #initialize graph
DG.add_nodes_from(list(range(100)))

DG.add_weighted_edges_from(e_list)

end = time.time()

print("Time it takes to manually create a graph and add edges without using the graph generating functions:")
print(end - start)

#draw graph and measure time it takes
start = time.time()
nx.draw(DG)
end = time.time()

plt.savefig("path.png")

print("Time it takes to draw a graph:")
print(end - start)

#create a random graph using netowrkx built in functions measure time
p = 0.01

start = time.time()
rand_g = nx.fast_gnp_random_graph(num_nodes, p, directed=False)
end = time.time()

print("Time it takes to create a G(n, p) graph with fast_gnp_random_graph")
print(end - start)

start = time.time()
rand_g = nx.gnp_random_graph(num_nodes, p, directed=False)
end = time.time()

print("Time it takes to create a G(n, p) graph with gnp_random_graph")
print(end - start)

start = time.time()
rand_g = nx.gnm_random_graph(num_nodes, num_edges, directed=True)
end = time.time()

print("Time it takes to create a G(n, m) graph with gnm_random_graph")
print(end - start)


