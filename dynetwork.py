import networkx as nx
import matplotlib.pyplot as plt
import time
import random
import numpy as np
import Packet
import Packets

# Question: Can I directly use functions in packet if I import Packets which included Packet
'''PERSON class import WALLET， WALLET import MONEY. 
In PERSON class directly use MONEY function '''


class DynamicNetwork(object):
    def __init__(self, network, packets, rejections=0):
        self._network = network
        self._packets = packets
        self._rejections = rejections

    # Method declaration
    def randomGeneratePackets(self, num_packets_to_generate):
        tempList = []
        for _ in range(num_packets_to_generate):
            # random nodes initialization
            startNode = self._network.nodes(
                random.randint(0, len(self._network)))
            endNode = self._network.nodes(
                random.randint(0, len(self._network)))

            # if the node is full then assign to another
            while(startNode['p_queue'].length() > startNode['max_capacity']):
                startNode = self._network.nodes(
                    random.randint(0, len(self._network)))

            # distinct starting and ending node
            while (startNode == endNode):
                endNode = self._network.nodes(
                    random.randint(0, len(self._network)))

            # creat packet object
            # assign a 0 weight
            curPack = Packet.Packet(startNode, endNode, startNode, 0)

            tempList.append(curPack)

        # create Packets Object
        packetsObj = Packets.Packets(tempList)

        # Assign Packets Object to the network
        self._network._packets = packetsObj


# -----------Below can be in the main funciton----------------------
node_count = 100
# Note that this is a measure of edges per added node, not total number of edges
edge_count = 5
max_capacity = 5
time_steps = 10
edge_removal_min = 0
edge_removal_max = 10
init_num_packets = 100

# Initialize a Network using Networkx
# Add attributes "capacity" and "queue" to keep track of packets
G = nx.barabasi_albert_graph(node_count, edge_count)
nx.set_node_attributes(G, max_capacity, 'max_capacity')

#Used List instead of array for packet_queue#
#https://www.geeksforgeeks.org/queue-in-python/#
p_queue = [-1]*max_capacity
nx.set_node_attributes(G, p_queue, 'p_queue')
#nx.set_node_attributes(G, np.repeat(-1, max_capacity), 'p_queue')

# store in DynamicNetwork class
initPackets = None
G = DynamicNetwork(G, initPackets)

# random generate packets for network
G.randomGeneratePackets(init_num_packets)

'''
store packet index from Packets list
for i in range(init_num_packets):
    # temp is array: -1 * max_capacity
    temp = np.repeat(-1, G._network.nodes[G._packets[i].startPos]['max capacity'])
    #Question: pos is a boolean? Kyle 7/5/20
    pos = (G._network.nodes[G._packets[i].startPos]['p_queue'] == temp)
    G._network.nodes[G._packets[i].startPos]['p_queue'][pos][0] = i

del temp
del pos
'''

# Dynamic Edge Change
r = Router()
fixed_positions = nx.spring_layout(G)
stripped_list = []
for i in range(1, time_steps):
    # delete some edges
    edges = G.edges()
    deletion_number = random.randint(
        edge_removal_min, min(edge_removal_max, len(edges) - 1))
    strip = random.sample(edges, k=deletion_number)
    G.remove_edges_from(strip)
    stripped_list.extend(strip)
    # restore some deleted edges
    restore_number = random.randint(0, len(stripped_list) - 1)
    restore = random.choices(stripped_list, k=restore_number)
    G.add_edges_from(restore)
    nx.draw(G, pos=fixed_positions, with_labels=True, font_weight='bold')
    plt.savefig("network_images/dynet" + str(i) + ".png")
    plt.clf()

    for pkt in G._packets:
        r.dijkstra_router(G._network, pkt)
