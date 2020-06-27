# -*- coding: utf-8 -*-
"""
Created on Thu Jun 25 21:53:06 2020

@author: janes
"""

from graph_tool.all import *
from itertools import combinations
from random import sample
from numpy.random import randint
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

g = Graph() #initialize graph
vlist = g.add_vertex(num_nodes) #create vertices

#add weights to edges
eweight = g.new_edge_property("int")
g.add_edge_list(e_list)
    
end = time.time()

print("Time it takes to manually create a graph and add edges without using the graph generating functions:")
print(end - start)

#time it takes to draw graph
start = time.time()
graph_draw(g, vertex_text=g.vertex_index)
end = time.time()
print("Time it takes to draw a graph:")
print(end - start)

