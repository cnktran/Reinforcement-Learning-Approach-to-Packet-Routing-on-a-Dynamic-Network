#!/usr/bin/env python
# coding: utf-8

# In[1]:


import networkx as nx
import dynetx as dn
import matplotlib.pyplot as plt
import time
import random
import numpy as np


class DynamicNetwork:
    def __init__(self, network, packets):
        self._network = None
        self._packets = None

# Method declaration


def randomGeneratePackets(self, num_packets):
    tempList = []
    for i in range(num_packets):
        # random node initialization
        startNode = self.nodes(randint(0, len(self)))
        endNode = self.nodes(randint(0, len(self)))

        while (startNode == endNode):
            endNode = self.nodes(randint(0, len(self)))

        # give weight 0 in the begining
        curPack = Packet(startNode, endNode, startNode, 0)

        tempList.append(curPack)

    # creat Packets Object
    packetsObj = Packets(tempList)

    # Assign Packets Object to the network
    self._packets = packetsObj


node_count = 100
edge_count = 5
max_capacity = 5
time_steps = 10


# Initialize a Network
G = nx.barabasi_albert_graph(node_count, edge_count)
H = nx.Graph()
nx.set_node_attributes(G, 0, 'current_queue')
nx.set_node_attributes(G, max_capacity, 'max_queue')


# use G.edges() to obtain a list of all edges
# use G.neighbors(n) to obtain neighbors of node n
# Dynamic Edge Change
a = 0
# At any given time step, remove up to b edges
b = 10


for i in time_steps:
    delete_edges = random.randint(a, b)
    remove_list = random.sample(G.edges(), k=delete_edges)
    G.remove_edges_from(remove_list)

  #add_edges = random.randint(a,b)

    add_edges = random.randint(a, b)
    add_list = sample(list(combinations(range(1, n), 2)), add_edges)G.add_edges_fromr(remove_list)

  # router outputs first node of shortest path for packet
    # check if you can send it to one of your nearest neighbors
    # if not, stay
    # else:
    # send 'packet' i.e add -1 to queue of sending node
    # receive 'packet' i.e add +1 to queue of sending node
    # return

  # plt.subplot()
#nx.draw(G, with_labels=True, font_weight='bold')
# plt.savefig("test.png")
# time.sleep(3)


# In[8]:


# In[ ]:
