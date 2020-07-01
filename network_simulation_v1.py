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
p = 0.2
lam = p * (num_nodes - 1)/2
min_weight = 1
max_weight = 20
sim_time = 10

g = random_graph(num_nodes, lambda: (poisson(lam), poisson(lam)), directed = True)
num_edges = g.get_edges().shape[0]
randints = randint(min_weight, max_weight, size=num_edges)
weight = g.new_edge_property("int", vals=randints)

graph_draw(g, vertex_text=g.vertex_index, edge_pen_width=weight, )


for i in range(sim_time): 
    edges = g.get_edges()
    for e in g.edges():
      weight[e] = randint(min_weight, max_weight)
    graph_draw(g, vertex_text=g.vertex_index, edge_pen_width=weight, output="graph" + i + ".png")

  
#Using Floyd-Warshall on graph g. Distances are stored in EdgePropertyMap called f_dist_map
# f_dist_map = g.new_vp("int", numpy.inf)
# dist = shortest_distance(g, weights=weight, directed=True, dense=True, return_reached=True) 

# first_step = np.zeros(num_nodes)
# for i in range(num_nodes):
#     first_step[i] = np.argmin(dist[g.vertex(i)].a)
    