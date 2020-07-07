# -*- coding: utf-8 -*-
"""
Created on Wed Jul  1 16:46:11 2020

@author:
"""

#import Packet
from Packets import *
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


class Router:
    def __init__(self):
        pass

    # router using dijkstra
    # dyNetwork is of class DynamicNetwork
    def dijkstra_router(self, dyNetwork):
        # iterate all nodes
        for node in dyNetwork._network.nodes:
            # check if node contains packets to send
            for i in range(min(dyNetwork._network.nodes[node]['max_band'], dyNetwork._network.nodes[node]['p_queue'].qsize())):
                # pkt is the index of the packet
                pkt = dyNetwork._network.nodes[node]['p_queue'].queue[i]
                # adds the 'time'
                dyNetwork._packets.packetList[pkt].set_time(
                    dyNetwork._packets.packetList[pkt].get_time() + 1)
                # call dijkstra algorithm from NETWORKX
                currPos = dyNetwork._packets.packetList[pkt].get_curPos()
                destPos = dyNetwork._packets.packetList[pkt].get_endPos()
                next_step = nx.dijkstra_path(
                    dyNetwork._network, currPos, destPos)[1]

                # if the next node is full, increment # rejection
                if (self.is_capacity(dyNetwork, next_step)):
                    dyNetwork._rejections += 1
                else:
                    self.send_packet(dyNetwork, pkt, next_step)

    # router using floyd-warshall0
    def fw_router(self, dyNetwork):
        preds, _ = nx.floyd_warshall_predecessor_and_distance(
            dyNetwork._network)
        for node in dyNetwork._network.nodes:
            for i in range(min(dyNetwork._network.nodes[node]['max_band'], dyNetwork._network.nodes[node]['p_queue'].qsize)):
                pkt = dyNetwork._network.nodes[node]['p_queue'].queue[0]
                currPos = dyNetwork._packets.packetList[pkt].get_curPos()
                destPos = dyNetwork._packets.packetList[pkt].get_endPos()
                next_step = nx.reconstruct_path(currPos, destPos, preds)[1]
                if self.is_capacity(dyNetwork, next_step):
                    dyNetwork._rejections = dyNetwork._rejections + 1
                else:
                    self.send_packet(dyNetwork, pkt, next_step)

    # check if the node is at capacity
    def is_capacity(self, dyNetwork, target_node):
        return dyNetwork._network.nodes[target_node]['p_queue'].full()

    # send the packet the new node and update the current_queues
    def send_packet(self, dyNetwork, pkt, next_step):
        curr = dyNetwork._packets.packetList[pkt].get_curPos()
        dyNetwork._network.nodes[curr]['p_queue'].get()
        dyNetwork._packets.packetList[pkt].set_curPos(next_step)
        if next_step == dyNetwork._packets.packetList[pkt].get_endPos():
            dyNetwork._deliveries = dyNetwork._deliveries + 1
        else:
            dyNetwork._network.nodes[next_step]['p_queue'].put(pkt)
        # g.nodes[next_step]['current_queue'].append(pkt)
