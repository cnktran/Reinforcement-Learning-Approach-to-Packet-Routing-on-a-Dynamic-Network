import networkx as nx
import matplotlib.pyplot as plt
import time
import random
import numpy as np
import Packet
import Packets
from router import Router
from queue import Queue
from random import sample
from itertools import combinations


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
            '''
            endPoints = sample(list(combinations(range(0,num_nodes),2)),1)
            startNode = endPoints[0][0]
            endNode = endPoints[0][1]
            '''
            startNode = random.randint(0, num_nodes-1)
            endNode = random.randint(0, num_nodes-1)

            # if the node is full then assign to another
            while (len(self._network.nodes[startNode]['p_queue'].queue) >= self._network.nodes[startNode]['max_capacity'] or (startNode == endNode)):
                startNode = random.randint(0, num_nodes-1)
                endNode = random.randint(0, num_nodes-1)
            # creat packet object, assign a 0 weight
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)

            # put curPack into startNode's queue
            self._network.nodes[startNode]['p_queue'].put(
                curPack.get_index(), 1)

            tempList.append(curPack)

        # create Packets Object
        packetsObj = Packets.Packets(tempList)

        # Assign Packets Object to the network
        self._packets = packetsObj


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
            '''
            endPoints = sample(list(combinations(range(0,num_nodes),2)),1)
            startNode = endPoints[0][0]
            endNode = endPoints[0][1]
            '''
            startNode = random.randint(0, num_nodes-1)
            endNode = random.randint(0, num_nodes-1)

            # if the node is full then assign to another
            while (len(self._network.nodes[startNode]['p_queue'].queue) >= self._network.nodes[startNode]['max_capacity'] or (startNode == endNode)):
                startNode = random.randint(0, num_nodes-1)
                endNode = random.randint(0, num_nodes-1)
            # creat packet object, assign a 0 weight
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)

            # put curPack into startNode's queue
            self._network.nodes[startNode]['p_queue'].put(
                curPack.get_index(), 1)

            tempList.append(curPack)

        # create Packets Object
        packetsObj = Packets.Packets(tempList)

        # Assign Packets Object to the network
        self._packets = packetsObj
