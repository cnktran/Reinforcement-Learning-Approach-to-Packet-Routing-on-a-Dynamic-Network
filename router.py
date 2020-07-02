# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 16:46:11 2020

@author: janes
"""

import networkx as nx
import matplotlib.pyplot as plt

#router using dijkstra
def dijkstra_router(network, curr, dest):
    next_step = nx.dijkstra_path(network, curr, dest)[1] 
    if is_capacity(network, next_step):
        return curr
    else:
        update(network, curr, next_step)
        return next_step
        
#router using floyd-warshall
def fw_router(network, curr, dest):
    preds, _ = nx.floyd_warshall_predecessor_and_distance(network)
    next_step = nx.reconstruct_path(curr, dest, preds)[1]
    if is_capacity(network, next_step):
        return curr
    else:
        update(network, curr, next_step)
        return next_step
    
def is_capacity(g, node):
    return g.nodes[node]['current_queue'] == g.nodes[node]['max_queue']

def update(g, curr, next_step):
    g.nodes[curr]['current_queue'] = g.nodes[curr]['current_queue'] - 1
    g.nodes[next_step]['current_queue'] = g.nodes[next_step]['current_queue'] + 1

# #test router functions
# sample_g = nx.cycle_graph(5)
# nx.draw(sample_g)
# plt.savefig("sample.png")
