# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 16:46:11 2020

@author: janes
"""

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np 
class Router:
    def __init__(self):
        pass
    
    #router using dijkstra
    def dijkstra_router(self, network, pkt):
        curr = pkt.get_curPos()
        dest = pkt.get_endPos()
        next_step = nx.dijkstra_path(network, curr, dest)[1] 
        if self.is_capacity(network, next_step):
            return curr
        else:
            self.send_packet(network, pkt, next_step)
            return next_step
            
    #router using floyd-warshall
    def fw_router(self, network, pkt):
        curr = pkt.get_curPos()
        dest = pkt.get_endPos()
        preds, _ = nx.floyd_warshall_predecessor_and_distance(network)
        next_step = nx.reconstruct_path(curr, dest, preds)[1]
        if self.is_capacity(network, next_step):
            return curr
        else:
            self.send_packet(network, pkt, next_step)
            return next_step
        
    #check if the node is at capacity
    def is_capacity(g, node):
        return len(g.nodes[node]['current_queue'][g.nodes[node]['current_queue'] != np.repeat(-1,  g.nodes[node]['max_queue'])] ) == np.repeat(-1, g.nodes[node]['max_queue'])
    
    #send the packet the new node and update the current_queues
    def send_packet(g, pkt, next_step):
        curr = pkt.get_curPos()
        g.nodes[curr]['current_queue'].pop(0)
        g.nodes[next_step]['current_queue'].append(pkt.index())

# #test router functions
# sample_g = nx.cycle_graph(5)
# nx.draw(sample_g)
# plt.savefig("sample.png")
