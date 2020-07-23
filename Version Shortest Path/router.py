import networkx as nx
import numpy as np
import copy
from random import randint

class Router:
    def __init__(self):
        self.preds = None
        self.qtable = None

    # router using dijkstra
    # dyNetwork is of class DynamicNetwork
    def router(self, dyNetwork, router_type='dijkstra', weight='delay'):
        if str.lower(router_type) != 'dijkstra':
            if weight == 'delay':
                self.preds, _ = nx.floyd_warshall_predecessor_and_distance(
                    dyNetwork._network, weight='edge_delay')
            else:
                self.preds, _ = nx.floyd_warshall_predecessor_and_distance(
                    dyNetwork._network)
        temp_node_queue_lens = [0]
        temp_num_node_at_capacity = 0
        temp_num_nonEmpty_node = 0
        self.update_queues(dyNetwork)
        self.update_time(dyNetwork)

        # iterate all nodes
        for node in dyNetwork._network.nodes:
            # provides pointer for queue of current node
            curr_queue = dyNetwork._network.nodes[node]['sending_queue']
            sending_capacity = dyNetwork._network.nodes[node]['max_send_capacity']

            queue_size = len(curr_queue)

            # Congestion Measure #1: max queue len
            if(queue_size > dyNetwork._max_queue_length):
                dyNetwork._max_queue_length = queue_size

            # Congestion Measure #2: avg queue len pt1
            if(queue_size > 0):

                temp_node_queue_lens.append(queue_size)

                temp_num_nonEmpty_node += 1
                # Congestion Measure #3: avg percent at capacity
                if(queue_size > sending_capacity):
                    # increment number of nodes that are at capacity
                    temp_num_node_at_capacity += 1


            # stores packets which currently have no destination path
            remaining = []

            sendctr = 0
            for i in range(queue_size):
                # when node cannot send anymore packets break and move to next node
                if sendctr == sending_capacity:
                    dyNetwork._rejections +=(1*(len(dyNetwork._network.nodes[node]['sending_queue'])))
                    break
                remaining, curr_queue, sent = self.handle_node_packet(
                    dyNetwork, curr_queue, remaining, router_type, weight)
                if sent:
                    sendctr += 1

            dyNetwork._network.nodes[node]['sending_queue'] = remaining + \
                dyNetwork._network.nodes[node]['sending_queue']

        # Congestion Measure #2: avg queue len pt2
        if len(temp_node_queue_lens) > 1:
            dyNetwork._avg_q_len_arr.append(
                np.average(temp_node_queue_lens[1:]))

        # Congestion Measure #3: percent node at capacity
        dyNetwork._num_capacity_node.append(temp_num_node_at_capacity)

        dyNetwork._num_working_node.append(temp_num_nonEmpty_node)

    # takes packets which are now ready to be sent and puts them in the sending queue of the node
    def update_queues(self, dyNetwork):
        for nodeIdx in dyNetwork._network.nodes:
            node = dyNetwork._network.nodes[nodeIdx]
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

    def update_time(self, dyNetwork):
        for nodeIdx in dyNetwork._network.nodes:
            for elt in dyNetwork._network.nodes[nodeIdx]['receiving_queue']:
                # increment packet delivery time stamp
                pkt = elt[0]
                curr_time = dyNetwork._packets.packetList[pkt].get_time()
                dyNetwork._packets.packetList[pkt].set_time(curr_time + 1)
            for c_pkt in dyNetwork._network.nodes[nodeIdx]['sending_queue']:
                curr_time = dyNetwork._packets.packetList[c_pkt].get_time()
                dyNetwork._packets.packetList[c_pkt].set_time(curr_time + 1)

    # do whatever needs to be done to what is the first packet in current queue
    def handle_node_packet(self, dyNetwork, curr_queue, remaining, router_type, weight):
        pkt = curr_queue[0]  # current packet
        # gives current and destination nodes of packet
        currPos = dyNetwork._packets.packetList[pkt].get_curPos()
        destPos = dyNetwork._packets.packetList[pkt].get_endPos()
        sent = False
        try:

            if currPos == destPos:
                #print("bug")
                curr_queue.remove(pkt)
            else:
                next_step = self.get_next_step(
                    dyNetwork, currPos, destPos, router_type, weight)
                #print("not bug")
                if self.is_capacity(dyNetwork, next_step):
                    curr_queue.remove(pkt)
                    remaining.append(pkt)
                    dyNetwork._rejections += 1
                else:
                    self.send_packet(dyNetwork, pkt, currPos, next_step)
                    curr_queue.remove(pkt)
                    sent = True
        except (nx.NetworkXNoPath, KeyError):
            curr_queue.remove(pkt)
            remaining.append(pkt)
        return remaining, curr_queue, sent

    # routing packet and obtain next packet
    def get_next_step(self, dyNetwork, currPos, destPos, router_type, weight):
        if str.lower(router_type) == 'dijkstra' and weight == 'delay':
            return nx.dijkstra_path(dyNetwork._network, currPos, destPos, weight='edge_delay')[1]
        elif str.lower(router_type) == 'dijkstra':
            return nx.dijkstra_path(dyNetwork._network, currPos, destPos)[1]
        else:
            return nx.reconstruct_path(currPos, destPos, self.preds)[1]

    # check if the node is at capacity
    def is_capacity(self, dyNetwork, target_node):
        node = dyNetwork._network.nodes[target_node]
        total_queue_len = len(node['sending_queue']) + \
            len(node['receiving_queue'])
        return total_queue_len >= node['max_receive_capacity']

    # send the packet the new node and update the current_queues

    def send_packet(self, dyNetwork, pkt, curr, next_step):
        dyNetwork._packets.packetList[pkt].set_curPos(next_step)
        weight = dyNetwork._network[curr][next_step]['edge_delay']
        if dyNetwork._packets.packetList[pkt].get_curPos() == dyNetwork._packets.packetList[pkt].get_endPos():
            curr_time = dyNetwork._packets.packetList[pkt].get_time()
            dyNetwork._packets.packetList[pkt].set_time(curr_time + weight)
            new_time = dyNetwork._packets.packetList[pkt].get_time()
            dyNetwork._delivery_times.append(new_time)
            dyNetwork._deliveries += 1
            dyNetwork.GeneratePacket(pkt, randint(0, 5))
        else:
            dyNetwork._network.nodes[next_step]['receiving_queue'].append(
                (pkt, weight))
