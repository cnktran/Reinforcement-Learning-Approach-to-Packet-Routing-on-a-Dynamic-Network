import networkx as nx
import numpy as np


class Router:
    def __init__(self):
        self.preds = None
        self.qtable = None

    # router using dijkstra
    # dyNetwork is of class DynamicNetwork
    def router(self, dyNetwork, router_type='dijkstra'):
        if str.lower(router_type) != 'dijkstra':
            self.preds, _ = nx.floyd_warshall_predecessor_and_distance(
                dyNetwork._network)
        temp_node_queue_lens = [0]
        temp_num_node_at_capacity = 0
        # iterate all nodes
        for node in dyNetwork._network.nodes:
            # print("Node#: ", node)
            # provides pointer for queue of current node
            curr_queue = dyNetwork._network.nodes[node]['sending_queue']
            sending_capacity = dyNetwork._network.nodes[node]['max_send_capacity']

            queue_size = len(curr_queue)

            # Congestion Measure #1: max queue len
            if queue_size > dyNetwork._max_queue_len:
                dyNetwork._max_queue_len = queue_size

            # Congestion Measure #2: avg queue len pt1
            if(queue_size > 0):
                temp_node_queue_lens.append(queue_size)

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
                    break
                remaining, curr_queue, sent = self.handle_node_packet(
                    dyNetwork, curr_queue, remaining, router_type, i)
                if sent:
                    sendctr += 1

            # update receiving_queue for next turn
            dyNetwork._network.nodes[node]['receiving_queue'] = self.fixed_queue(
                dyNetwork, remaining, node)

        # dumps received packets into the sending queue
        for node in dyNetwork._network.nodes:
            dyNetwork._network.nodes[node]['sending_queue'] = dyNetwork._network.nodes[node]['receiving_queue']
            dyNetwork._network.nodes[node]['receiving_queue'] = []

        # Congestion Measure #2: avg queue len pt2
        if len(temp_node_queue_lens) > 1:
            dyNetwork._avg_q_len_arr.append(
                np.average(temp_node_queue_lens[1:]))

        # Congestion Measure #3: percent node at capacity
        dyNetwork._avg_perc_at_capacity_arr.append(temp_num_node_at_capacity)

    # no path is the remaining
    def fixed_queue(self, dyNetwork, no_path, node):

        curr_queue = dyNetwork._network.nodes[node]['sending_queue']
        receiving_queue = dyNetwork._network.nodes[node]['receiving_queue']

        toReturn = no_path + receiving_queue + curr_queue
        return toReturn

    def handle_node_packet(self, dyNetwork, curr_queue, remaining, router_type, i):
        pkt = curr_queue[0]  # current packet
        # increment packet delivery time stamp
        dyNetwork._packets.packetList[pkt].set_time(
            dyNetwork._packets.packetList[pkt].get_time() + 1)
        # gives current and destination nodes of packet
        currPos = dyNetwork._packets.packetList[pkt].get_curPos()
        destPos = dyNetwork._packets.packetList[pkt].get_endPos()
        sent = False
        try:
            # band aid fix in case we have a 'bad' packet
            if currPos == destPos:
                # print("bug")
                dyNetwork._deliveries += 1
                curr_queue.remove(pkt)

            else:
                next_step = self.get_next_step(
                    dyNetwork, currPos, destPos, router_type)
                if self.is_capacity(dyNetwork, next_step):
                    curr_queue.remove(pkt)
                    remaining.append(pkt)
                    dyNetwork._rejections += 1
                else:
                    curr_queue.remove(pkt)
                    self.send_packet(dyNetwork, pkt, next_step)
                    sent = True
        except (nx.NetworkXNoPath, KeyError):
            curr_queue.remove(pkt)
            remaining.append(pkt)
        return remaining, curr_queue, sent

    def get_next_step(self, dyNetwork, currPos, destPos, router_type):
        if str.lower(router_type) == 'dijkstra':
            return nx.dijkstra_path(dyNetwork._network, currPos, destPos)[1]
        else:
            return nx.reconstruct_path(currPos, destPos, self.preds)[1]
    # check if the node is at capacity

    def is_capacity(self, dyNetwork, target_node):
        # max_recieve_capacity is initialized with the value of the maximum queue any node can have
        total_queue_len = len(dyNetwork._network.nodes[target_node]['sending_queue']) + len(
            dyNetwork._network.nodes[target_node]['receiving_queue'])
        return total_queue_len == dyNetwork._network.nodes[target_node]['max_receive_capacity']

    # send the packet the new node and update the current_queues
    def send_packet(self, dyNetwork, pkt, next_step):
        dyNetwork._packets.packetList[pkt].set_curPos(next_step)

        # check when reached destinition
        if dyNetwork._packets.packetList[pkt].get_curPos() == dyNetwork._packets.packetList[pkt].get_endPos():
            dyNetwork._deliveries += 1
        else:
            dyNetwork._network.nodes[next_step]['receiving_queue'].append(pkt)
