import time
import random
import numpy as np
import Packet

class DynamicNetwork(object):
    def __init__(self, network, packets=None, rejections=0, deliveries=0, qtable=None):

        self._network = network
        self._packets = packets
        self._rejections = rejections
        self._deliveries = deliveries
        self._qtable = qtable
        self._avg_q_len_arr = []
        self._avg_perc_at_capacity_arr = []

    # Method declaration
    def randomGeneratePackets(self, num_packets_to_generate):
        tempList = []
        for index in range(num_packets_to_generate):
            notfull = list(range(self._network.number_of_nodes()))
            num_nodes = len(list(self._network.nodes()))#'sending_queue'
            startNode = random.randint(0, num_nodes-1)
            endNode = random.randint(0, num_nodes-1)
            # if the node is full then assign to another
            while (len(self._network.nodes[startNode]['sending_queue']) >= self._network.nodes[startNode]['max_receive_capacity']):
                notfull.remove(startNode)
                try:
                    startNode = random.choice(notfull)
                except:
                    print("Network cannot handle this many packets bruv")
            while (startNode == endNode):
                endNode = random.randint(0, num_nodes-1)

            # creat packet object, assign a 0 weight
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)

            # put curPack into startNode's queue
            self._network.nodes[startNode]['sending_queue'].append(
                curPack.get_index())
                
            tempList.append(curPack)

        # create Packets Object
        packetsObj = Packet.Packets(tempList)

        # Assign Packets Object to the network
        self._packets = packetsObj
