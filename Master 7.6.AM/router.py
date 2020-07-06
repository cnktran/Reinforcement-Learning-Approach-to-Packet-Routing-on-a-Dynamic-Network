# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 16:46:11 2020

@author:
"""

import networkx as nx
import matplotlib.pyplot as plt


class Router:
    def __init__(self):
        pass
    # router using dijkstra

    def dijkstra_router(self, network):
        for pkt in network._packets:
            curr = pkt.get_curPos()
            dest = pkt.get_endPos()
            next_step = nx.dijkstra_path(network, curr, dest)[1]

            # if the next node is full
            if (network.isCapacity(next_step)):
                return curr
            else:
                network.send_packet(pkt, next_step)
                return next_step

    # router using floyd-warshall
    def fw_router(self, network):
        preds, _ = nx.floyd_warshall_predecessor_and_distance(network)
        for pkt in network._packets:
            curr = pkt.get_curPos()
            dest = pkt.get_endPos()
            next_step = nx.reconstruct_path(curr, dest, preds)[1]
            if self.is_capacity(network, next_step):
                return curr
            else:
                self.send_packet(network, pkt, next_step)
                return next_step

    # check if the node is at capacity
    def is_capacity(self, g, node):
        return len(g.nodes[node]['p_queue'][g.nodes[node]['p_queue'] != np.repeat(-1,  g.nodes[node]['max_capacity'])]) == np.repeat(-1, g.nodes[node]['max_capacity'])
        # return len(g.nodes[node]['p_queue']) == g.nodes[node]['max_capacity']

    # send the packet the new node and update the p_queue
    def send_packet(self, g, pkt, next_step):
        curr = pkt.get_curPos()
        g.nodes[curr]['p_queue'].pop(0)
        g.nodes[next_step]['p_queue'].append(pkt.index())
        #curr = pkt.get_curPos()
        # g.nodes[curr]['p_queue'].pop(0)
        # g.nodes[next_step]['p_queue'].append(pkt)
        pkt.set_curPos(next_step)


# #test router functions
# sample_g = nx.cycle_graph(5)
# nx.draw(sample_g)
# plt.savefig("sample.png")
