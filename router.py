# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 16:46:11 2020

@author: janes
"""

import networkx as nx
import matplotlib.pyplot as plt

#router using dijkstra
def dijkstra_router(network, curr, dest):
    path = nx.dijkstra_path(network, curr, dest) 
    return path[1]

#router using floyd-warshall
def fw_router(network, curr, dest):
    preds, _ = nx.floyd_warshall_predecessor_and_distance(network)
    path = nx.reconstruct_path(curr, dest, preds)
    return path[1]

# #test router functions
# sample_g = nx.cycle_graph(5)
# nx.draw(sample_g)
# plt.savefig("sample.png")
