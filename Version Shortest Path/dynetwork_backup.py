import time
import random
import numpy as np
import Packet
import copy
class DynamicNetwork(object):
    def __init__(self, network, max_initializations, packets=None, rejections=0, deliveries=0, qtable=None):

        self._network = network
        self._packets = packets
        self._rejections = rejections
        self._deliveries = deliveries
        self._qtable = qtable
        self._max_queue_length = 0
        self._avg_q_len_arr = []
        self.delayed_queue = []
        self._stripped_list = []
        self._num_capacity_node = []
        self._num_working_node = []
        self._delivery_times = []
        self._initializations = 0
        self._max_initializations = max_initializations
        self.num_nodes = None
        self._purgatory = []

    # Method declaration
    def randomGeneratePackets(self, num_packets_to_generate):
        tempList = {}
        self.num_nodes = len(list(self._network.nodes()))
        #'sending_queue'
        notfull = list(range(self.num_nodes))

        for index in range(num_packets_to_generate):
            curPack, notfull = self.GeneratePacket(index = index, wait = 0, midSim = False, notfull = notfull)
            # put curPack into startNode's queue
            self._network.nodes[curPack.get_startPos()]['sending_queue'].append(
                curPack.get_index())
            tempList[index] = curPack
        # create Packets Object
        packetsObj = Packet.Packets(tempList)

        # Assign Packets Object to the network
        self._packets = copy.deepcopy(packetsObj)
        del packetsObj
        
# Generate packets will either taken in a not full list, or it will just take nodes
    def GeneratePacket(self, index, wait = 0, midSim = True, notfull = None):
        if self._initializations >= self._max_initializations:
            pass
        elif wait <= 0:
            if midSim or notfull == None:
                notfull = list(range(self.num_nodes))
            startNode = random.randint(0, self._network.number_of_nodes() - 1)
            endNode = random.randint(0, self._network.number_of_nodes() - 1)
            #if the node is full then assign to another
            while (len(self._network.nodes[startNode]['sending_queue']) + len(self._network.nodes[startNode]['receiving_queue'])
                   >= self._network.nodes[startNode]['max_receive_capacity']):
                try:
                    notfull.remove(startNode)
                except:
                    pass
                startNode = random.choice(notfull)
            while (startNode == endNode):
                endNode = random.randint(0, self.num_nodes-1)
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)
            if midSim: 
                self._packets.packetList[index] = curPack
                self._initializations += 1
                self._network.nodes[curPack.get_startPos()]['receiving_queue'].append((curPack.get_index(), 0))
                try:
                    self._purgatory.remove((index, weight))
                except:
                    pass
                return
            return curPack, notfull
        else:
            self._purgatory.append((index, wait - 1))
