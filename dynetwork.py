from itertools import combinations
from random import sample
from queue import Queue
import router as r
import Packets
import Packet
import numpy as np
import random
import time
import matplotlib.pyplot as plt
import networkx as nx
\documentclass[12pt]{article}
\usepackage[utf8]{inputenc}
\begin{document}
\end{document}


class DynamicNetwork(object):
    def __init__(self, network, packets=None, rejections=0, deliveries=0, qtable=None):

        self._network = network
        self._packets = packets
        self._rejections = rejections
        self._deliveries = deliveries
        self._qtable = qtable

    # Method declaration
    def randomGeneratePackets(self, num_packets_to_generate):
        tempList = []
        for index in range(num_packets_to_generate):
            num_nodes = len(list(self._network.nodes()))
            endPoints = sample(list(combinations(range(0, num_nodes), 2)), 1)
            startNode = endPoints[0][0]
            endNode = endPoints[0][1]
            # if the node is full then assign to another
            while (len(self._network.nodes[startNode]['p_queue'].queue) >= self._network.nodes[startNode]['max_capacity']):
                endPoints = sample(
                    list(combinations(range(0, num_nodes), 2)), 1)
                startNode = endPoints[0][0]
                endNode = endPoints[0][1]

            startNode = self._network.nodes[startNode]
            endNode = self._network.nodes[endNode]
            # creat packet object, assign a 0 weight
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)

            # put curPack into startNode's queue
            startNode['p_queue'].queue.append(curPack.get_index())

            tempList.append(curPack)

        # create Packets Object
        packetsObj = Packets.Packets(tempList)

        # Assign Packets Object to the network
        self._network._packets = packetsObj


# -----------Below can be in the main funciton----------------------
node_count = 100
# # Note that this is a measure of edges per added node, not total number of edges
edge_count = 5
max_capacity = 5
time_steps = 2
edge_removal_min = 0
edge_removal_max = 10
init_num_packets = 100

# Initialize a Network using Networkx
# Add attributes "capacity" and "queue" to keep track of packets
networkxGraph = nx.barabasi_albert_graph(node_count, edge_count)
p_queue = Queue(max_capacity)
nx.set_node_attributes(networkxGraph, max_capacity, 'max_capacity')
nx.set_node_attributes(networkxGraph, p_queue, 'p_queue')

# store in DynamicNetwork class
G = DynamicNetwork(networkxGraph)
G.randomGeneratePackets(init_num_packets)
# Dynamic Edge Change
fixed_positions = nx.spring_layout(G._network)
stripped_list = []
for i in range(1, time_steps):
    # delete some edges
    edges = G._network.edges()
    deletion_number = random.randint(
        edge_removal_min, min(edge_removal_max, len(edges) - 1))
    strip = random.sample(edges, k=deletion_number)
    G._network.remove_edges_from(strip)
    stripped_list.extend(strip)
    # restore some deleted edges
    restore_number = random.randint(0, len(stripped_list) - 1)
    restore = random.choices(stripped_list, k=restore_number)
    G._network.add_edges_from(restore)
    # perform routing
    r.dijkstra_router(G)
    # draw network
    node_queues = nx.get_node_attributes(G._network, 'p_queue')
    node_labels = {}
    for node, atr in node_queues.items():
        node_labels[node] = atr.qsize()
    nx.draw(G._network, pos=fixed_positions,
            labels=node_labels, font_weight='bold')
    plt.savefig("network_images/dynet" + str(i) + ".png")
    plt.clf()
    if G._deliveries == init_num_packets:
        print("Simulation done in " + str(i))
        break
