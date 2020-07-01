# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 11:20:16 2020

@author: janes
"""
from graph_tool.all import *
import time
import numpy as np
from numpy.random import *
import random

#create graph g
num_nodes = 15
p = 0.25
lam = max(0, p * (num_nodes - 1)/2 - 1)
min_weight = 1
max_weight = 20
sim_time = 10

#setting up the initial state of the network
g = random_graph(num_nodes, lambda: (1 + poisson(lam), 1 + poisson(lam)), directed = True)
num_edges = g.get_edges().shape[0]
randints = randint(min_weight, max_weight, size=num_edges)
weight = g.new_edge_property("int", vals=randints)

pos = sfdp_layout(g)
graph_draw(g, vertex_text=g.vertex_index, edge_pen_width=weight)


removed = []

for i in range(sim_time): 
    remove = []
    for old_e in removed:
       new_removed = removed
       if uniform(0, 1) < 0.5:
         new_e = g.add_edge(old_e[0], old_e[1])
         new_removed.remove(old_e) 
         weight[new_e] = randint(min_weight, max_weight)
       removed = new_removed
    for e in g.edges():
      prob = uniform(0, 1)
      if (prob < 0.4):
        weight[e] = randint(min_weight, max_weight)
      elif prob < 0.5:
        remove.append(e)
        removed.append((e.source(), e.target()))
    for e in remove:
      g.remove_edge(e)
      
    fn = "graph" + str(i) + ".png"
    graph_draw(g, pos=pos, vertex_text=g.vertex_index, edge_pen_width=weight, output=fn)
    

  
#Using Floyd-Warshall on graph g. Distances are stored in EdgePropertyMap called f_dist_map
# f_dist_map = g.new_vp("int", numpy.inf)
# dist = shortest_distance(g, weights=weight, directed=True, dense=True, return_reached=True) 

# first_step = np.zeros(num_nodes)
# for i in range(num_nodes):
#     first_step[i] = np.argmin(dist[g.vertex(i)].a)
    