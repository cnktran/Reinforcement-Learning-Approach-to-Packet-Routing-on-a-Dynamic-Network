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

num_nodes = 1000
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


print(end - start)

start = time.time()
nx.draw(DG)
end = time.time()

plt.savefig("path.png")

print(end - start)