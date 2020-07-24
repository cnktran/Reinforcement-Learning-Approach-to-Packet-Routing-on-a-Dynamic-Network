"""Use environment_template.py as the reference for this document.
Used to fit network generation on multiple episodes"""

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
from our_agent import QAgent
import numpy as np


class dynetworkEnv(gym.Env):
    def __init__(self):
        self.nnodes = 50
        self.nedges = 3
        self.max_queue = 150
        self.max_transmit = 10
        self.npackets = 5000
        self.max_initializations = 100
        self.max_edge_weight = 10
        self.min_edge_removal = 0
        self.max_edge_removal = 10
        self.edge_change_type = 'sinusoidal'
        self.network_type = 'barabasi-albert'
        self.initial_dynetwork = None
        self.dynetwork = None
        self.packet = -1
        self.curr_queue = []
        self.remaining = []
        self.nodes_traversed = 0
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
        nx.set_node_attributes(network, copy.deepcopy(self.max_transmit), 'max_send_capacity')
        nx.set_node_attributes(network, copy.deepcopy(self.max_queue),'max_receive_capacity')
        nx.set_node_attributes(network, copy.deepcopy(self.max_queue), 'congestion_measure')
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

        self.initial_dynetwork = dynetwork.DynamicNetwork(copy.deepcopy(network), self.max_initializations)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'q-learning/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        nx.write_gexf(network, results_dir + "graph.gexf")
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        # use dynetwork class method randomGeneratePackets to populate the network with packets
        self.dynetwork.randomGeneratePackets(copy.deepcopy(self.npackets))

        # make a copy so that we can preserve the initial state of the network
        # set our current packet that we are focusing on to the first item in the dynetwork's packet list


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
        temp_purgatory = copy.deepcopy(self.dynetwork._purgatory)
        self.dynetwork._purgatory = []
        for (index, weight) in temp_purgatory:
            self.dynetwork.GeneratePacket(index, weight)

    # given an neighboring node (action) o
    #probably don't need curNode
    def step(self, action, curNode = None): #here, action would be a neigbor of packets current node
        reward = None
        pkt = self.dynetwork._packets.packetList[self.packet]
        curr = pkt.get_curPos()
        dest = pkt.get_endPos()
        #action is only None when the current node has 'no' neighbors ('no' because this just means that the connecting edges may have just dissapeared)
        if (action == None) or (self.is_capacity(self.dynetwork, action)):
        #self.packet is the dictionary label of the packet, pkt is the corresponding packet object
            self.curr_queue.remove(self.packet)
            self.remaining.append(self.packet)
            self.dynetwork._rejections += 1
        else:
            #put if part of block into  if in send_packet, make send packet return a reward
            reward = self.send_packet(action)
                # Reward = (doing one of the first steps in the shortest path) - (going to a congested node) - (weight)


        #print('Step successful!')
        return reward, self.remaining, self.curr_queue, action


    def is_capacity(self, dynetwork, target_node):
        node = dynetwork._network.nodes[target_node]
        total_queue_len = len(node['sending_queue']) + \
            len(node['receiving_queue'])
        return total_queue_len >= node['max_receive_capacity']

    def send_packet(self, next_step):
        reward = 0
        pkt = self.dynetwork._packets.packetList[self.packet]
        curr = copy.deepcopy(pkt.get_curPos())
        dest = copy.deepcopy(pkt.get_endPos())
        weight = self.dynetwork._network[curr][next_step]['edge_delay']
        pkt.set_curPos(next_step)
        if pkt.get_curPos() == dest:
            self.dynetwork._packets.packetList[self.packet].set_time(pkt.get_time() + weight)
            self.dynetwork._delivery_times.append(self.dynetwork._packets.packetList[self.packet].get_time())
            self.dynetwork._deliveries += 1
            reward = 1000
            self.dynetwork.GeneratePacket(self.packet, random.randint(0, 5))
            self.curr_queue.remove(self.packet)

        else:
            self.curr_queue.remove(self.packet)
            #"path length??" says no path between two
            try:
                path_len = nx.shortest_path_length(self.dynetwork._network, next_step, dest)
                queue_size = len(self.dynetwork._network.nodes[next_step]['sending_queue'])
                emptying_size = weight * self.max_transmit
                if queue_size > emptying_size:
                    fullness = (queue_size - emptying_size)
                else:
                    fullness = 0
                reward = - path_len - (fullness + weight)
            except nx.NetworkXNoPath:
                reward = -50  # adjust this number later
            self.dynetwork._network.nodes[next_step]['receiving_queue'].append(
                (self.packet, weight))
        return reward


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
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        self.dynetwork.randomGeneratePackets(self.npackets)
        print('Environment reset')
        #return reset
    
    def resetForTest(self,curLoad):
        #reset = False
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        self.npackets = curLoad
        self.dynetwork.randomGeneratePackets(self.npackets)
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

    def calc_avg_delivery(self):
        avg = sum(self.dynetwork._delivery_times)/len(self.dynetwork._delivery_times)
        
        return avg

    def router(self, agent, will_learn = True):

        temp_node_queue_lens = [0]
        temp_num_node_at_capacity = 0
        temp_num_nonEmpty_node = 0
        
        # iterate all nodes
        for nodeIdx in self.dynetwork._network.nodes:
            """ the self.nodes_traversed tracks the number of nodes we have looped over, guarunteeing that each packet will have the same epsilon at each time step"""
            self.nodes_traversed += 1
            if copy.deepcopy(self.nodes_traversed) == copy.deepcopy(self.nnodes):
                agent.config['update_epsilon'] = True
                self.nodes_traversed = 0
            node = self.dynetwork._network.nodes[nodeIdx]
            # provides pointer for queue of current node
            self.curr_queue = node['sending_queue']
            sending_capacity = node['max_send_capacity']
            queue_size = len(self.curr_queue)

            # Congestion Measure #1: max queue len
            if(queue_size > self.dynetwork._max_queue_length):
                self.dynetwork._max_queue_length = queue_size

            # Congestion Measure #2: avg queue len pt1
            if(queue_size > 0):

                temp_node_queue_lens.append(queue_size)
                temp_num_nonEmpty_node += 1
                # Congestion Measure #3: avg percent at capacity
                if(queue_size > sending_capacity):
                    # increment number of nodes that are at capacity
                    temp_num_node_at_capacity += 1


            # stores packets which currently have no destination path
            self.remaining = []
            sendctr = 0
            for i in range(queue_size):
                # when node cannot send anymore packets break and move to next node
                if sendctr == sending_capacity:
                    self.dynetwork._rejections +=(1*(len(node['sending_queue'])))
                    #INCREMENT PKT TIME
                    break
                self.packet = self.curr_queue[0]
                pkt_state = self.get_state(self.packet)
                nlist = list(self.dynetwork._network.neighbors(pkt_state[0]))
                action = agent.act(pkt_state, nlist)
                reward, self.remaining, self.curr_queue, action = self.step(action, pkt_state[0])
                if reward != None:
                    sendctr += 1
                if will_learn:
                    agent.learn(pkt_state, reward, action)

            node['sending_queue'] = self.remaining + node['sending_queue']

        # Congestion Measure #2: avg queue len pt2
        if len(temp_node_queue_lens) > 1:
            self.dynetwork._avg_q_len_arr.append(
                np.average(temp_node_queue_lens[1:])) #Kyle： why are we doing [1:]? 7/19 AM
    
        # Congestion Measure #3: percent node at capacity
        self.dynetwork._num_capacity_node.append(temp_num_node_at_capacity)
    
        self.dynetwork._num_working_node.append(temp_num_nonEmpty_node)

        # Congestion Mesure #4: percent empty nodes
        self.dynetwork._num_empty_node.append(self.dynetwork.num_nodes-temp_num_nonEmpty_node)
        #print(self.dynetwork.num_nodes-temp_num_nonEmpty_node)

    def updateWhole(self,agent, learn = True):
        self.change_network()
        self.purgatory()
        self.update_queues()
        self.update_time()
        #this will iterate through every packet, throughout all nodes and make them 'step ahead'
        self.router(agent, learn) 
            
