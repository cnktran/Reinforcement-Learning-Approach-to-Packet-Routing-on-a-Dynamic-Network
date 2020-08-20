import dynetwork
import Packet
import UpdateEdges as UE
from our_agent import QAgent

import gym
from gym import error
from gym.utils import closer
import networkx as nx

import copy
import numpy as np
import math
import os
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.image as mgimg
from matplotlib import animation
from random import randint


""" This class contains our gym environment which contains all of the necessary components for agents to take actions and receive rewards. file contains functions: 
    
    change_network: edge deletion/re-establish, edge weight change
    purgatory: queue to generate additional queues as previous packets are delivered
    step: obtain rewards for updating Q-table after an action
    is_capacity: check if next node is full and unable to receive packets
    send_packet: attempt to send packet to next node
    reset: reset environment after each episode
    resetForTest: reset environment for each trial (test for different network loads)
    get_state: obtain packet's position info
    update_queues: update each nodes packet holding queue
    update_time: update packet delivery time
    calc_avg_delivery: helper function to calculate delivery time
    router: used to route all packets in ONE time stamp
    updateWhole: helper function update network environment and packets status
    """
    
class dynetworkEnv(gym.Env):
    
    '''Initialization of the network'''
    def __init__(self):
        self.nnodes = 50
        self.nedges = 3
        self.max_queue = 150
        self.max_transmit = 10
        self.npackets = 5000
        self.max_initializations = 5000
        self.max_edge_weight = 10
        self.min_edge_removal = 0
        self.max_edge_removal = 10
        self.edge_change_type = 'sinusoidal'
        self.network_type = 'barabasi-albert'
        self.router_type = 'dijkstra'
        self.initial_dynetwork = None
        self.dynetwork = None
        self.print_edge_weights = True

        '''For Q-Learning'''
        '''current packet, i.e. first item in the dynetwork's packet list'''
        self.packet = -1 
        self.curr_queue = []
        self.remaining = []
        self.nodes_traversed = 0

        '''For Shortest Path'''
        self.sp_packet = -1
        self.sp_curr_queue = []
        self.sp_remaining = []
        self.sp_nodes_traversed = 0
        self.preds = None 

        '''Initialize a dynetwork object using Networkx and dynetwork.py'''
        
        if self.network_type == 'barabasi-albert':
            network = nx.barabasi_albert_graph(self.nnodes, self.nedges)
        else:
           network = nx.gnm_random_graph(self.nnodes, self.nedges)

        '''node attributes'''
        nx.set_node_attributes(network, copy.deepcopy(self.max_transmit), 'max_send_capacity')
        nx.set_node_attributes(network, copy.deepcopy(self.max_queue),'max_receive_capacity')

        '''Q-Learning specific'''
        receiving_queue_dict, sending_queue_dict = {}, {}
        for i in range(self.nnodes):
            temp = {'receiving_queue': []}
            temp2 = {'sending_queue': []}
            receiving_queue_dict.update({i: temp})
            sending_queue_dict.update({i: temp2})
        del temp, temp2
        nx.set_node_attributes(network, receiving_queue_dict)
        nx.set_node_attributes(network, sending_queue_dict)
        nx.set_node_attributes(network, 0, 'max_queue_len')
        nx.set_node_attributes(network, 0, 'avg_q_len_array')
        nx.set_node_attributes(network, 0, 'growth')
        
        '''Shortest Path specific'''
        sp_receiving_queue_dict, sp_sending_queue_dict = {}, {}
        for i in range(self.nnodes):
            temp = {'sp_receiving_queue': []}
            temp2 = {'sp_sending_queue': []}
            sp_receiving_queue_dict.update({i: temp})
            sp_sending_queue_dict.update({i: temp2})
        del temp, temp2
        nx.set_node_attributes(network, sp_receiving_queue_dict)
        nx.set_node_attributes(network, sp_sending_queue_dict)
        nx.set_node_attributes(network, 0, 'sp_max_queue_len')
        nx.set_node_attributes(network, 0, 'sp_avg_q_len_array')

        '''Edge attributes'''
        nx.set_edge_attributes(network, 0, 'edge_delay')
        nx.set_edge_attributes(network, 0, 'sine_state')
        for s_edge, e_edge in network.edges:
            network[s_edge][e_edge]['edge_delay'] = random.randint(2, self.max_edge_weight)
            network[s_edge][e_edge]['initial_weight'] = network[s_edge][e_edge]['edge_delay']
            network[s_edge][e_edge]['sine_state'] = random.uniform(0, math.pi)

        '''make a copy so that we can preserve the initial state of the network'''
        self.initial_dynetwork = dynetwork.DynamicNetwork(copy.deepcopy(network), self.max_initializations)
        
        '''Saves the graph into .gexf file'''
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'q-learning/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        nx.write_gexf(network, results_dir + "graph.gexf")
        
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        '''use dynetwork class method randomGeneratePackets to populate the network with packets'''
        self.dynetwork.randomGeneratePackets(copy.deepcopy(self.npackets), False)
        self._positions = nx.spring_layout(self.dynetwork._network)

    '''helper function to update learning environment in each time stamp''' 
    def updateWhole(self, agent, learn = True, q=True, sp = False, rewardfun='reward5', savesteps=False):
        self.change_network()
        
        if q:
            self.purgatory(False)
            self.update_queues(False)
            self.update_time(False)
            self.router(agent, learn, rewardfun, savesteps) 

        if sp:
            self.purgatory(True)
            self.update_queues(True)
            self.update_time(True)
            self.sp_router(self.router_type, 'delay', savesteps)
        
    '''Use to update edges in network'''
    def change_network(self):
        UE.Delete(self.dynetwork, self.min_edge_removal, self.max_edge_removal)
        UE.Restore(self.dynetwork)
        if self.edge_change_type == 'none':
            pass
        elif self.edge_change_type == 'sinusoidal':
            UE.Sinusoidal(self.dynetwork)
        else:
            UE.Random_Walk(self.dynetwork)
    
    '''Method for emptying 'purgatory' which holds indices of packets that have
       been delivered so they may be reused'''
    def purgatory(self, sp=False):
        if sp:
            temp_purgatory = copy.deepcopy(self.dynetwork.sp_purgatory)
            self.dynetwork.sp_purgatory = []
        else:
            temp_purgatory = copy.deepcopy(self.dynetwork._purgatory)
            self.dynetwork._purgatory = []
        for (index, weight) in temp_purgatory:
            self.dynetwork.GeneratePacket(index, sp, weight)
            
    '''Takes packets which are now ready to be sent and puts them in the sending queue of the node '''
    def update_queues(self, sp=False):
        if sp:
            sending_queue = 'sp_sending_queue'
            receiving_queue = 'sp_receiving_queue'
        else:
            sending_queue = 'sending_queue'
            receiving_queue = 'receiving_queue'

        for nodeIdx in self.dynetwork._network.nodes:
            node = self.dynetwork._network.nodes[nodeIdx]
            if not sp:
                node['growth'] = len(node[receiving_queue])
            queue = copy.deepcopy(node[receiving_queue])
            for elt in queue:
                '''increment packet delivery time step'''
                pkt = elt[0]
                if elt[1] == 0:
                    node[sending_queue].append(pkt)
                    node[receiving_queue].remove(elt)
                else:
                    idx = node[receiving_queue].index(elt)
                    node[receiving_queue][idx] = (pkt, elt[1] - 1)

    ''' Update time spent in queues for each packets '''
    def update_time(self, sp=False):
        if sp:
            sending_queue = 'sp_sending_queue'
            receiving_queue = 'sp_receiving_queue'
            packets = self.dynetwork.sp_packets
        else:
            sending_queue = 'sending_queue'
            receiving_queue = 'receiving_queue'
            packets = self.dynetwork._packets

        for nodeIdx in self.dynetwork._network.nodes:
            for elt in self.dynetwork._network.nodes[nodeIdx][receiving_queue]:
                '''increment packet delivery time step'''
                pkt = elt[0]
                curr_time = packets.packetList[pkt].get_time()
                packets.packetList[pkt].set_time(curr_time + 1)
            for c_pkt in self.dynetwork._network.nodes[nodeIdx][sending_queue]:
                curr_time = packets.packetList[c_pkt].get_time()
                packets.packetList[c_pkt].set_time(curr_time + 1)


    ''' -----------------Q-Learning Functions---------------- '''

    ''' return packet's position and destination'''
    def get_state(self, pktIdx):
        pkt = self.dynetwork._packets.packetList[self.packet]
        return (pkt.get_curPos(), pkt.get_endPos())
        
    def router(self, agent, will_learn = True, rewardfun='reward5', savesteps=False):
        node_queue_lengths = [0]
        num_nodes_at_capacity = 0
        num_nonEmpty_nodes = 0
        '''iterate all nodes'''
        for nodeIdx in self.dynetwork._network.nodes:
            """ the self.nodes_traversed tracks the number of nodes we have looped over, guarunteeing that each packet will have the same epsilon at each time step"""
            self.nodes_traversed += 1
            if self.nodes_traversed == self.nnodes:
                agent.config['update_epsilon'] = True
                self.nodes_traversed = 0
            node = self.dynetwork._network.nodes[nodeIdx]
            '''provides pointer for queue of current node'''
            self.curr_queue = node['sending_queue']
            sending_capacity = node['max_send_capacity']
            queue_size = len(self.curr_queue)

            '''Congestion Measure #1: max queue len'''
            if(queue_size > self.dynetwork._max_queue_length):
                self.dynetwork._max_queue_length = queue_size

            '''Congestion Measure #2: avg queue len pt1'''
            if(queue_size > 0):
                node_queue_lengths.append(queue_size)
                num_nonEmpty_nodes += 1
                ''' Congestion Measure #3: avg percent at capacity'''
                if(queue_size > sending_capacity):
                    '''increment number of nodes that are at capacity'''
                    num_nodes_at_capacity += 1

            '''stores packets which currently have no destination path'''
            self.remaining = []
            sendctr = 0
            for i in range(queue_size):
                '''when node cannot send anymore packets break and move to next node'''
                if sendctr == sending_capacity:
                    self.dynetwork._rejections +=(1*(len(node['sending_queue'])))
                    break
                self.packet = self.curr_queue[0]
                pkt_state = self.get_state(copy.deepcopy(self.packet))
                nlist = list(self.dynetwork._network.neighbors(pkt_state[0]))
                action = agent.act(pkt_state, nlist)
                reward, self.remaining, self.curr_queue, action = self.step(action, pkt_state[0], rewardfun, savesteps)
                if reward != None:
                    sendctr += 1
                if will_learn:
                    agent.learn(pkt_state, reward, action)

            node['sending_queue'] = self.remaining + node['sending_queue']

        '''Congestion Measure #2: avg queue length pt2'''
        if len(node_queue_lengths) > 1:
            self.dynetwork._avg_q_len_arr.append(np.average(node_queue_lengths[1:]))
        '''Congestion Measure #3: percent node at capacity'''
        self.dynetwork._num_capacity_node.append(num_nodes_at_capacity)
        self.dynetwork._num_working_node.append(num_nonEmpty_nodes)
        '''Congestion Mesure #4: percent empty nodes'''
        self.dynetwork._num_empty_node.append(self.nnodes - num_nonEmpty_nodes)
             
    """ given an neighboring node (action), will check if node has a available space in that queue. if it does not, the packet stays at current queue. else, packet is sent to action node's queue. """
    def step(self, action, curNode = None, rewardfun='reward5', savesteps=False):
        reward = None
        
        """ checks if action is None, in which case current node has no neighbors and also checks to see if target node has space in queue """
        
        if (action == None) or (self.is_capacity(action, False)):
            self.curr_queue.remove(self.packet)
            self.remaining.append(self.packet)
            self.dynetwork._rejections += 1
        else:
            reward = self.send_packet(action, rewardfun, savesteps)
        pkt = self.dynetwork._packets.packetList[self.packet]
        return reward, self.remaining, self.curr_queue, action

    ''' 
    Given next_step, send packet to next_step.
    Check if the node is full/other considerations beforehand. 
    '''
    def send_packet(self, next_step, rewardfun='reward5', savesteps=False):
        reward = 0
        pkt = self.dynetwork._packets.packetList[self.packet]
        curr_node = pkt.get_curPos()
        dest_node = pkt.get_endPos()
        weight = self.dynetwork._network[curr_node][next_step]['edge_delay']
        pkt.set_curPos(next_step)
        if savesteps:
            pkt.add_step(next_step)
        self.dynetwork._packets.packetList[self.packet].set_time(pkt.get_time() + weight)
        if pkt.get_curPos() == dest_node:
            """ if packet has reached destination, a new packet is created with the same 'ID' (packet index) but a new destination, which is then redistributed to another node """
            self.dynetwork._delivery_times.append(self.dynetwork._packets.packetList[self.packet].get_time())
            self.dynetwork._deliveries += 1
            self.dynetwork.GeneratePacket(self.packet, False, random.randint(0, 5))
            self.curr_queue.remove(self.packet)
            reward = 20*self.nnodes
        else:
            self.curr_queue.remove(self.packet)
            try:
                if rewardfun == 'reward1':
                    reward = self.reward1(next_step, dest_node, weight)
                if rewardfun == 'reward2':
                    reward = self.reward2(next_step, dest_node, weight)
                if rewardfun == 'reward3':
                    reward = self.reward3(next_step, dest_node)
                if rewardfun == 'reward4':
                    reward = self.reward4(next_step, weight)
                if rewardfun == 'reward5':
                    reward = self.reward5(next_step)
                if rewardfun == 'reward6':
                    reward = self.reward6(next_step)
                if rewardfun == 'reward7':
                    reward = self.reward7(next_step)
            except nx.NetworkXNoPath:
                """ if the node the packet was just sent to has no available path to dest_node, we assign a reward of -50 """
                reward = -50
            self.dynetwork._network.nodes[next_step]['receiving_queue'].append(
                (self.packet, weight))
        return reward

    '''-----------------------------Reward Functions----------------------------'''

    '''Hybrid function that penalizes proportional to queue size'''
    def reward1(self, next_step, dest_node, weight):
        """ we reward the packet for being sent to a node according to our current reward function """
        path_len = nx.shortest_path_length(self.dynetwork._network, next_step, dest_node)
        queue_size = len(self.dynetwork._network.nodes[next_step]['sending_queue']) + len(self.dynetwork._network.nodes[next_step]['receiving_queue'])
        return(- path_len - (queue_size + weight))

    '''Hybrid function that penalizes only if queue size exceeds a threshold'''
    def reward2(self, next_step, dest_node, weight):
        path_len = nx.shortest_path_length(self.dynetwork._network, next_step, dest_node)
        queue_size = len(self.dynetwork._network.nodes[next_step]['sending_queue']) + len(self.dynetwork._network.nodes[next_step]['receiving_queue'])
        emptying_size = weight * self.max_transmit
        if queue_size > emptying_size:
            fullness = (queue_size - emptying_size)
        else:
            fullness = 0
        return(- path_len - (fullness + weight))

    '''Function that only takes into account path length'''
    def reward3(self, next_step, dest_node):
        path_len = nx.shortest_path_length(self.dynetwork._network, next_step, dest_node)
        return -(path_len)

    '''Function similar to reward2 that does not use shortest path'''
    def reward4(self, next_step, weight):
        queue_size = len(self.dynetwork._network.nodes[next_step]['sending_queue']) + len(self.dynetwork._network.nodes[next_step]['receiving_queue'])
        emptying_size = weight * self.max_transmit
        if queue_size > emptying_size:
            fullness = (queue_size - emptying_size)
        else:
            fullness = 0
        return(-(fullness + weight))

    '''Function that penalizes proportional to difference in queue size and an equilibrium queue size,
       as well as growth rate of the queue'''
    def reward5(self, next_step):
        q = len(self.dynetwork._network.nodes[next_step]['sending_queue']) + len(self.dynetwork._network.nodes[next_step]['receiving_queue'])
        q_eq = 0.8*self.max_queue
        w = 5
        growth = self.dynetwork._network.nodes[next_step]['growth']
        return(-(q-q_eq+w*growth))

    '''Function that penalizes for exceeing equilibrium queue size, as well as growth rate of the queue'''
    def reward6(self, next_step):
        q = len(self.dynetwork._network.nodes[next_step]['sending_queue']) + len(self.dynetwork._network.nodes[next_step]['receiving_queue'])
        q_eq = 0.8*self.max_queue
        excess = q-q_eq
        w = 5
        growth = self.dynetwork._network.nodes[next_step]['growth']
        if excess > 0:
            return -(excess+w*growth)
        else:
            return -(w*growth)

    '''Extra reward function, change as desired to use in rewards.py'''
    def reward7(self, next_step):
        return 0

    '''--------------------SHORTEST PATH-----------------'''

    def sp_router(self, router_type='dijkstra', weight='delay', savesteps=False):
        if str.lower(router_type) != 'dijkstra':
            if weight == 'delay':
                self.preds, _ = nx.floyd_warshall_predecessor_and_distance(self.dynetwork._network, weight='edge_delay')
            else:
                self.preds, _ = nx.floyd_warshall_predecessor_and_distance(self.dynetwork._network)
        temp_node_queue_lens = [0]
        temp_num_nodes_at_capacity = 0
        temp_num_nonEmpty_node = 0
        self.update_queues(True)
        self.update_time(True)

        '''iterate all nodes'''
        for node in self.dynetwork._network.nodes:
            '''provides pointer for queue of current node'''
            curr_queue = self.dynetwork._network.nodes[node]['sp_sending_queue']
            sending_capacity = self.dynetwork._network.nodes[node]['max_send_capacity']
            queue_size = len(curr_queue)

            '''Congestion Measure #1: max queue length'''
            if(queue_size > self.dynetwork.sp_max_queue_length):
                self.dynetwork.sp_max_queue_length = queue_size
            '''Congestion Measure #2: average queue length'''
            if(queue_size > 0):
                temp_node_queue_lens.append(queue_size)
                temp_num_nonEmpty_node += 1

                '''Congestion Measure #3: average percentage of active nodes at capacity'''
                if(queue_size > sending_capacity):
                    temp_num_nodes_at_capacity += 1

            '''stores packets which currently have no path to destination'''
            remaining = []
            sendctr = 0

            for i in range(queue_size):
                '''when node cannot send anymore packets, break and move on to next node'''
                if sendctr == sending_capacity:
                    self.dynetwork.sp_rejections +=(len(self.dynetwork._network.nodes[node]['sp_sending_queue']))
                    break
                remaining, curr_queue, sent = self.handle_node_packet(curr_queue, remaining, router_type, weight, savesteps)
                if sent:
                    sendctr += 1
            self.dynetwork._network.nodes[node]['sp_sending_queue'] = remaining + self.dynetwork._network.nodes[node]['sp_sending_queue']

        '''Congestion Measure #2: average queue length'''
        if len(temp_node_queue_lens) > 1:
            self.dynetwork.sp_avg_q_len_arr.append(np.average(temp_node_queue_lens[1:]))

        '''Congestion Measure #3: percentage of nodes at capacity'''
        self.dynetwork.sp_num_capacity_node.append(temp_num_nodes_at_capacity)
        self.dynetwork.sp_num_working_node.append(temp_num_nonEmpty_node)
        self.dynetwork.sp_num_empty_node.append((self.nnodes - temp_num_nonEmpty_node)/self.nnodes)

    '''helper function to move packets to their corresponding queues'''
    def handle_node_packet(self, curr_queue, remaining, router_type, weight, savesteps=False):
        pkt = curr_queue[0]
        currPos = self.dynetwork.sp_packets.packetList[pkt].get_curPos()
        destPos = self.dynetwork.sp_packets.packetList[pkt].get_endPos()
        sent = False
        try:
            if currPos == destPos:
                curr_queue.remove(pkt)
            else:
                next_step = self.get_next_step(currPos, destPos, router_type, weight)
                if self.is_capacity(next_step, True):
                    curr_queue.remove(pkt)
                    remaining.append(pkt)
                    self.dynetwork.sp_rejections += 1
                else:
                    self.sp_send_packet(pkt, currPos, next_step, savesteps)
                    curr_queue.remove(pkt)
                    sent = True
        except (nx.NetworkXNoPath, KeyError):
            curr_queue.remove(pkt)
            remaining.append(pkt)
        return remaining, curr_queue, sent 

    '''return the node for packet to route to in the next step using shortest path algorithm'''
    def get_next_step(self, currPos, destPos, router_type, weight):
        if str.lower(router_type) == 'dijkstra' and weight == 'delay':
            return nx.dijkstra_path(self.dynetwork._network, currPos, destPos, weight='edge_delay')[1]
        elif str.lower(router_type) == 'dijkstra':
            return nx.dijkstra_path(self.dynetwork._network, currPos, destPos)[1]
        else:
            return nx.reconstruct_path(currPos, destPos, self.preds)[1]
            
    '''helper function to route one pacaket'''
    def sp_send_packet(self, pkt, curr, next_step, savesteps=False):
        if savesteps:
            self.dynetwork.sp_packets.packetList[pkt].add_step(next_step)
        self.dynetwork.sp_packets.packetList[pkt].set_curPos(next_step)
        weight = self.dynetwork._network[curr][next_step]['edge_delay']
        curr_time = self.dynetwork.sp_packets.packetList[pkt].get_time()
        self.dynetwork.sp_packets.packetList[pkt].set_time(curr_time + weight)
        if self.dynetwork.sp_packets.packetList[pkt].get_curPos() == self.dynetwork.sp_packets.packetList[pkt].get_endPos():
            new_time = self.dynetwork.sp_packets.packetList[pkt].get_time()
            self.dynetwork.sp_delivery_times.append(new_time)
            self.dynetwork.sp_deliveries += 1
            self.dynetwork.GeneratePacket(pkt, True, randint(0,5))
        else:
            self.dynetwork._network.nodes[next_step]['sp_receiving_queue'].append((pkt, weight))


    '''----SHARED FUNCTIONS BETWEEN Q-LEARNING AND SHORTEST PATH----'''

    """ checks to see if there is space in target_nodes queue """
    def is_capacity(self, target_node, sp = False):
        if sp:
            sending_queue = 'sp_sending_queue'
            receiving_queue = 'sp_receiving_queue'
        else:
            sending_queue = 'sending_queue'
            receiving_queue = 'receiving_queue'

        total_queue_len = len(self.dynetwork._network.nodes[target_node][sending_queue]) + \
            len(self.dynetwork._network.nodes[target_node][receiving_queue])
        return total_queue_len >= self.dynetwork._network.nodes[target_node]['max_receive_capacity']

    """ this function resets the environment """
    def reset(self, curLoad, sp):
        self.dynetwork = copy.deepcopy(self.initial_dynetwork)
        if curLoad != None:
            self.npackets = curLoad
        self.dynetwork.randomGeneratePackets(self.npackets, sp)
        print('Environment reset')
        
    '''helper function to calculate delivery times'''
    def calc_avg_delivery(self, sp = False):
        if sp:
            delivery_times = self.dynetwork.sp_delivery_times
        else:
            delivery_times = self.dynetwork._delivery_times
        return(sum(delivery_times)/len(delivery_times))

    ''' Save an image of the current state of the network'''
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
        script_dir1 = os.path.dirname(__file__)
        results_dir1 = os.path.join(script_dir1, 'network_images/')
        if not os.path.isdir(results_dir1):
            os.makedirs(results_dir1)
        plt.axis('off')
        plt.figtext(0.1, 0.1, "total injections: "+ str(self.max_initializations + self.dynetwork._initializations))
        plt.savefig("network_images/dynet" + str(i) + ".png")
        plt.clf()

    '''helper function to generate animations of the routing process'''
    def routing_example(self, agent, curLoad):
        
        '''create directory'''
        script_dir = os.path.dirname(__file__)
        anim_dir = os.path.join(script_dir, 'animations/')
        if not os.path.isdir(anim_dir):
            os.makedirs(anim_dir)

        '''track the first packet'''
        t1 = 0
        t2 = 0
        try:
            q_first_packet = self.dynetwork._packets.packetList[(self.dynetwork._network.nodes[0]['sending_queue'])[-1]]
            sp_first_packet = self.dynetwork.sp_packets.packetList[(self.dynetwork._network.nodes[0]['sp_sending_queue'])[-1]]
            q_current_node = q_first_packet.get_startPos()
            sp_current_node = sp_first_packet.get_startPos()
            destination = q_first_packet.get_endPos()
            q_nodes = []
            s_nodes = []
            edges = []
            edge_labels = []
            q_traversed = []
            s_traversed = []
            q_current = [q_current_node]
            s_current = [sp_current_node]
            
            '''keep on routing until both Q-learning and SP finish'''
            while (q_current_node is not destination) or (sp_current_node is not destination):
                '''I should really use a dictionary instead of a million lists of size t...'''
                self.updateWhole(agent, learn=False, q=True, sp=True, rewardfun='reward5', savesteps=True)
                if q_current_node is not destination:
                    t1+=1
                if sp_current_node is not destination:
                    t2+=1
                q_current_node = q_first_packet._steps[-1]
                sp_current_node = sp_first_packet._steps[-1]
                q_current.append(q_first_packet.get_curPos())
                s_current.append(sp_first_packet.get_curPos())
                e = self.dynetwork._network.edges
                edges.append(e)
                q_node_label = {}
                sp_node_label = {}
                for node in self.dynetwork._network.nodes:
                    q_node_label[node] = str(node) + ":" + str(len(self.dynetwork._network.nodes[node]['sending_queue']) + len(self.dynetwork._network.nodes[node]['receiving_queue']))
                    sp_node_label[node] = str(node) + ":" + str(len(self.dynetwork._network.nodes[node]['sp_sending_queue']) + len(self.dynetwork._network.nodes[node]['sp_receiving_queue']))
                q_nodes.append(q_node_label)
                s_nodes.append(sp_node_label)
                temp = zip(q_first_packet._steps, q_first_packet._steps[1:])
                path = []
                for (a,b) in temp:
                    if a > b:
                        path.append((b,a))
                    else:
                        path.append((a,b))
                q_traversed.append([x for x in list(path) if x in e])
                temp1 = zip(sp_first_packet._steps, sp_first_packet._steps[1:])
                path1 = []
                for (a,b) in temp1:
                    if a > b:
                        path1.append((b,a))
                    else:
                        path1.append((a,b))
                s_traversed.append([x for x in list(path1) if x in e])
                if self.print_edge_weights:
                    edge_labels.append(nx.get_edge_attributes(self.dynetwork._network, 'edge_delay'))


            print("Packet %i traversed from Node %i to Node %i." % (q_first_packet.get_index(), q_first_packet.get_startPos(), q_first_packet.get_endPos()))
            print("Q-Learning: %i time steps" % (1+q_first_packet.get_time()))
            print(q_first_packet._steps)
            print("Shortest Path: %i time steps" % sp_first_packet.get_time())
            print(sp_first_packet._steps)
            
            '''animate traversal process for both'''
            fig = plt.figure(figsize=(9.6, 7.2))
            plt.clf()
            plt.axis('off')

            def q_animate(i):
                plt.clf()
                plt.title("Q-Learning for Load of "+str(curLoad))
                plt.figtext(0, 0, "Path:" + str(q_first_packet._steps) + "\nTime: "+ str(1+q_first_packet.get_time()), fontsize='x-large')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, node_color='#CCE5FF')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, nodelist=[0, destination], node_color='#FFB266')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, nodelist=[q_current[i+1]], node_size=500)
                nx.draw_networkx_labels(self.dynetwork._network, pos=self._positions, labels=q_nodes[i], font_weight = 'bold')
                nx.draw_networkx_edges(self.dynetwork._network, pos=self._positions, edgelist=edges[i])
                nx.draw_networkx_edges(self.dynetwork._network, pos=self._positions, edgelist=q_traversed[i], width=3.0)
                if self.print_edge_weights:
                    nx.draw_networkx_edge_labels(self.dynetwork._network, pos=self._positions, edge_labels=edge_labels[i])

            anim = animation.FuncAnimation(fig, q_animate, frames=t1, interval=50, repeat_delay=1000)
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=2, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(anim_dir+"q_load"+str(curLoad)+".mp4", writer=writer)

            fig = plt.figure(figsize=(9.6, 7.2))
            plt.clf()
            plt.axis('off')

            def s_animate(i):
                plt.clf()
                plt.title("Shortest Path for Load of "+str(curLoad))
                plt.figtext(0, 0, "Path:" + str(sp_first_packet._steps) + "\nTime: "+ str(sp_first_packet.get_time()), fontsize='x-large')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, node_color='#CCE5FF')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, nodelist=[0, destination], node_color='#FFB266')
                nx.draw_networkx_nodes(self.dynetwork._network, pos=self._positions, nodelist=[s_current[i+1]], node_size=500)
                nx.draw_networkx_labels(self.dynetwork._network, pos=self._positions, labels=s_nodes[i], font_weight = 'bold')
                nx.draw_networkx_edges(self.dynetwork._network, pos=self._positions, edgelist=edges[i])
                nx.draw_networkx_edges(self.dynetwork._network, pos=self._positions, edgelist=s_traversed[i], width=3.0)
                if self.print_edge_weights:
                    nx.draw_networkx_edge_labels(self.dynetwork._network, pos=self._positions, edge_labels=edge_labels[i])

            anim = animation.FuncAnimation(fig, s_animate, frames=t2, interval=50, repeat_delay=1000)
            Writer = animation.writers['ffmpeg']
            writer = Writer(fps=2, metadata=dict(artist='Me'), bitrate=1800)
            anim.save(anim_dir+"sp_load"+str(curLoad)+".mp4", writer=writer)

        except:
            pass