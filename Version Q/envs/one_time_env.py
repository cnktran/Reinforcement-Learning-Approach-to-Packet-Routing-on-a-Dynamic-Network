    """Use environment_template.py as the reference for this document."""

import gym
import UpdateEdges as UE
import Packet
import dynetwork
from gym import error
from gym.utils import closer
import networkx as nx
import copy
import random
import math
import os
import matplotlib.pyplot as plt

class dynetworkEnv(gym.Env):
    def __init__(self):
        self.nnodes = 20
        self.nedges = 3
        self.npackets = 20
        self.max_edge_weight = 10
        self.min_edge_removal = 0
        self.max_edge_removal = 5
        self.edge_change_type = 'sinusoidal'
        self.max_queue = float('inf')
        self.max_transmit = 5
        self.network_type = 'barabasi-albert'
        self.initial_dynetwork = None
        self.dynetwork = None
        
        # create a dynetwork type object
        if self.network_type == 'barabasi-albert': 
            network = nx.barabasi_albert_graph(self.nnodes, self.nedges)
        else:
           network = nx.gnm_random_graph(self.nnodes, self.nedges)
        receiving_queue_dict, sending_queue_dict = {}, {}
        for i in range(self.nnodes):
            temp = {'receiving_queue': []}
            temp2 = {'sending_queue': []}
            receiving_queue_dict.update({i: temp})
            sending_queue_dict.update({i: temp2})
        del temp, temp2
        
        '''Attribute added'''
        # node attributes
        nx.set_node_attributes(network, self.max_transmit, 'max_send_capacity')
        nx.set_node_attributes(network, self.max_queue,'max_receive_capacity')
        nx.set_node_attributes(network, self.max_queue, 'congestion_measure')
        nx.set_node_attributes(network, receiving_queue_dict)
        nx.set_node_attributes(network, sending_queue_dict)
        # edge attributes
        nx.set_edge_attributes(network, 0, 'num_traversed')
        nx.set_edge_attributes(network, 0, 'edge_delay')
        nx.set_edge_attributes(network, 0, 'sine_state')
        #CongestM Attribute added
        nx.set_node_attributes(network, 0, 'max_queue_len')
        nx.set_node_attributes(network, 0, 'avg_q_len_array')
        # max_weight for edges
        for s_edge, e_edge in network.edges:
            network[s_edge][e_edge]['edge_delay'] = random.randint(0, self.max_edge_weight)
            network[s_edge][e_edge]['sine_state'] = random.uniform(0, math.pi)
        self.initial_dynetwork = dynetwork.DynamicNetwork(network, self.npackets)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'q-learning/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        nx.write_gexf(network, results_dir + "graph.gexf")
        
        # use dynetwork class method randomGeneratePackets to populate the network with packets
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        self.dynetwork.randomGeneratePackets(self.npackets)
        
        # make a copy so that we can preserve the initial state of the network
        # set our current packet that we are focusing on to the first item in the dynetwork's packet list
        self.packet = 0
        self.curr_queue = []        
        self.remaining = []
        
        #display stuff
        self._positions = nx.spring_layout(self.dynetwork._network)

        self.print_edge_weights = True

    # Dynamic Edge Change
    def change_network(self):
        UE.Delete(self.dynetwork, self.min_edge_removal, self.max_edge_removal)
        UE.Restore(self.dynetwork)
        if self.edge_change_type == 'none':
            pass
        elif self.edge_change_type == 'sinusoidal':
            UE.Sinusoidal(self.dynetwork)
        else:
            UE.Random_Walk(self.dynetwork)
            
    def purgatory(self):
        temp_purgatory = copy.deepcopy(self._dynetwork._purgatory)
        self._dynetwork._purgatory = []
        for (index, weight) in temp_purgatory:
            self._dynetwork.GeneratePacket(index, weight)
       
    # given an neighboring node (action) o
    #probably don't need curNode
    def step(self, action, curNode): #here, action would be a neigbor of packets current node
        reward = None
        pkt = self.dynetwork._packets.packetList[self.packet]
        curr = pkt.get_curPos()
        dest = pkt.get_endPos()
        

        #action is only None when the current node has no available edges
        if (action == None) or (self.is_capacity(self.dynetwork, action)):
            self.curr_queue.remove(self.packet)
            self.remaining.append(self.packet)
            self.dynetwork._rejections += 1
            
        else:
            weight = self.dynetwork._network[curr][action]['edge_delay']
            if curr == dest:
                curr_time = pkt.get_time()
                pkt.set_time(curr_time + weight)
                self.dynetwork._deliveries += 1
                reward = 1000
                self.curr_queue.remove(self.packet)
                self.dynetwork.GeneratePacket(self.packet, random.randint(0, 5))
            else:
                self.send_packet(action)
                self.curr_queue.remove(self.packet)
                # Reward = (doing one of the first steps in the shortest path) - (going to a congested node) - (weight)
                try:
                    path_len = nx.shortest_path_length(self.dynetwork._network, action, dest)
                    reward = - path_len - (len(self.dynetwork._network.nodes[action]['sending_queue']) + weight)
                except nx.NetworkXNoPath:
                    reward = -30 #adjust this number later

        #print('Step successful!')
        return reward, self.remaining, self.curr_queue, action

    def render(self, i = 0):
        node_labels = {}
        for node in self.dynetwork._network.nodes:
            node_labels[node] = len(self.dynetwork._network.nodes[node]['sending_queue']) + len(
                self.dynetwork._network.nodes[node]['receiving_queue'])
        nx.draw(self.dynetwork._network, pos=self._positions,
                labels=node_labels, font_weight='bold')
        if self.print_edge_weights:
            edge_labels = nx.get_edge_attributes(
                self.dynetwork._network, 'edge_delay')
            nx.draw_networkx_edge_labels(
                self.dynetwork._network, pos=self._positions, edge_labels=edge_labels)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'network_images/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        plt.axis('off')
        plt.figtext(0.1, 0.1, "total injections: "+ str(init_num_packets + self._dynetwork._initializations))
        plt.savefig("network_images/dynet" + str(i) + ".png")
        plt.clf()
    
    def is_capacity(self, dynetwork, target_node):
        node = dynetwork._network.nodes[target_node]
        total_queue_len = len(node['sending_queue']) + \
            len(node['receiving_queue'])
        return total_queue_len >= node['max_receive_capacity']
    
    def send_packet(self, next_step):
        pkt = self.dynetwork._packets.packetList[self.packet]
        curr = pkt.get_curPos()
        dest = pkt.get_endPos()
        
        weight = self.dynetwork._network[curr][next_step]['edge_delay']
        pkt.set_curPos(next_step)
        if curr == dest:
            self.dynetwork._packets.packetList[pkt].set_time(pkt.get_time() + weight)
            new_time = self.dyNetwork._packets.packetList[pkt].get_time()
            self.dyNetwork._delivery_times.append(new_time)
            self.dynetwork._deliveries += 1
            self.dynetwork.GeneratePacket(pkt, random.randint(0, 5))
        else:
            self.dynetwork._network.nodes[next_step]['receiving_queue'].append(
                (self.packet, weight))
        
    def get_next_step(self, dynetwork, currPos, destPos, router_type, weight, action = None):
        if str.lower(router_type) == 'q-learning':
            return action
        elif str.lower(router_type) == 'dijkstra' and weight == 'delay':
            return nx.dijkstra_path(dynetwork._network, currPos, destPos)[1]
        elif str.lower(router_type) == 'dijkstra':
            return nx.dijkstra_path(dynetwork._network, currPos, destPos)[1]
        else:
            return nx.reconstruct_path(currPos, destPos, self.preds)[1]

    def reset(self):
        #reset = False
        self.dynetwork = copy.deepcopy(self.initial_network)
        self.dynetwork.randomGeneratePackets(self.npackets)
        print('Environment reset')
        #return reset
    
    def get_state(self, pktIdx):
        pkt = self.dynetwork._packets.packetList[self.packet]
        return (pkt.get_curPos(), pkt.get_endPos())                #reward = nx.shortest_path(G = self.dynetwork._network, source = action, target = dest) - len(self.dynetwork._network.nodes[dest]['sending_queue']) - weight
        
    # takes packets which are now ready to be sent and puts them in the sending queue of the node
    def update_queues(self):
        for nodeIdx in self.dynetwork._network.nodes:
            node = self.dynetwork._network.nodes[nodeIdx]
            receiving_queue = copy.deepcopy(node['receiving_queue'])
            for elt in receiving_queue:
                # increment packet delivery time stamp
                pkt = elt[0]
                if elt[1] == 0:
                    node['sending_queue'].append(pkt)
                    node['receiving_queue'].remove(elt)
                else:
                    idx = node['receiving_queue'].index(elt)
                    node['receiving_queue'][idx] = (pkt, elt[1] - 1)

    def update_time(self):
        for nodeIdx in self.dynetwork._network.nodes:
            for elt in self.dynetwork._network.nodes[nodeIdx]['receiving_queue']:
                # increment packet delivery time stamp
                pkt = elt[0]
                curr_time = self.dynetwork._packets.packetList[pkt].get_time()
                self.dynetwork._packets.packetList[pkt].set_time(curr_time + 1)
            for c_pkt in self.dynetwork._network.nodes[nodeIdx]['sending_queue']:
                curr_time = self.dynetwork._packets.packetList[c_pkt].get_time()
                self.dynetwork._packets.packetList[c_pkt].set_time(curr_time + 1)

    def generateAdditionalPackets(self,index):
        self.dynetwork.GeneratePacket(index)
        
    def calc_avg_delivery(self):
        return(sum(self._dynetwork._delivery_times)/len(self._dynetwork._delivery_times))