import time
import random
import numpy as np
import Packet
import copy

''' 
    Class created to store network and network attributes as well as generate packets 
    File contains functions:
        randomGeneratePackets: initialize packets to network in the beginning 
        GeneratePacket: generate additional packets as previous packets are delivered to keep network working in specified load
'''

class DynamicNetwork(object):
    def __init__(self, network, max_initializations=1000, packets=None, rejections=0, deliveries=0,):

        '''shared attributes'''
        self._network = copy.deepcopy(network)
        self._num_nodes = None
        self._max_initializations = max_initializations

        '''q_learning attributes'''
        self._packets = packets
        self._rejections = rejections
        self._deliveries = deliveries
        self.delayed_queue = []
        self._stripped_list = []
        self._delivery_times = []
        self._initializations = 0
        self._max_queue_length = 0
        self._purgatory = []        
        self._avg_q_len_arr = []
        self._num_empty_node=[]
        self._num_capacity_node = []
        self._num_working_node = []

        '''shortest path attributes'''
        self.sp_packets = packets
        self.sp_rejections = rejections
        self.sp_deliveries = deliveries
        self.sp_delayed_queue = []
        self.sp_stripped_list = []
        self.sp_delivery_times = []
        self.sp_initializations = 0
        self.sp_max_queue_length = 0
        self.sp_purgatory = []
        self.sp_avg_q_len_arr = []
        self.sp_num_capacity_node = []
        self.sp_num_working_node = []
        self.sp_num_empty_node=[]

    ''' Function used to generate packets
        handle both first initialization or later additional injections '''
    def randomGeneratePackets(self, num_packets_to_generate, sp):
        tempList = {}
        self.num_nodes = len(list(self._network.nodes()))
        notfull = list(range(self.num_nodes))
        for index in range(num_packets_to_generate):
            curPack, notfull = self.GeneratePacket(index = index, wait = 0, midSim = False, notfull=copy.deepcopy(notfull))
            '''put curPack into startNode's queue'''
            self._network.nodes[curPack.get_startPos()]['sending_queue'].append(curPack.get_index())
            if sp:
                self._network.nodes[curPack.get_startPos()]['sp_sending_queue'].append(curPack.get_index())
            tempList[index] = curPack
        '''create Packets Object'''
        packetsObj = Packet.Packets(tempList)

        '''Assign Packets Object to the network'''
        self._packets = copy.deepcopy(packetsObj)
        if sp:
            self.sp_packets = copy.deepcopy(packetsObj)
        del packetsObj
        del tempList
        
        
    """ called by randomGeneratePackets 
        when generating additional packets after previous packets are delivered """     
    def GeneratePacket(self, index, sp=False, wait = 0, midSim = True, notfull=None):
        """checks to see if we have exceed the maximum number of packets allotted in the simulation"""
        if sp:
            initializations = self.sp_initializations
            sending_queue = 'sp_sending_queue'
            receiving_queue = 'sp_receiving_queue'
            packets = self.sp_packets
            purgatory = self.sp_purgatory
        else:
            initializations = self._initializations
            sending_queue = 'sending_queue'
            receiving_queue = 'receiving_queue'
            packets = self._packets
            purgatory = self._purgatory

        if initializations >= self._max_initializations:
            pass
        elif wait <= 0:
            """ creates a list of not full nodes to check during new packet creation """ 
            if midSim:
                notfull = list(range(self.num_nodes))
            startNode = random.choice(notfull)
            endNode = random.randint(0, self._network.number_of_nodes() - 1)
            """ searches through notfull list until an available node is located for initial packet assignment """ 
            while (len(self._network.nodes[startNode][sending_queue]) + len(self._network.nodes[startNode][receiving_queue])
                   >= self._network.nodes[startNode]['max_receive_capacity']):
                notfull.remove(startNode)
                try:
                    startNode = random.choice(notfull)
                except:
                    print("Error: All Nodes are Full")
                    return
            """ searches through notfull list until an available node is located for initial packet assignment """ 
            
            """ assigns the packet different delivery destination than starting point """ 
            while (startNode == endNode):
                endNode = random.randint(0, self.num_nodes-1)
                
            curPack = Packet.Packet(startNode, endNode, startNode, index, 0)
            if midSim:
                """ appends newly generated packet to startNodes queue """ 
                packets.packetList[index] = curPack
                if sp:
                    self.sp_initializations += 1
                else:
                    self._initializations += 1
                self._network.nodes[curPack.get_startPos()][receiving_queue].append((curPack.get_index(), 0))
                try: 
                    purgatory.remove((index, wait))
                except: 
                    pass
                return
            return curPack, notfull
        else:
            purgatory.append((index, wait - 1))