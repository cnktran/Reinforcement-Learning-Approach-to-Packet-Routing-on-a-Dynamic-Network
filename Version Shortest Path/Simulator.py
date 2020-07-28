import networkx as nx
import os
from dynetwork import *
from router import Router
import matplotlib.pyplot as plt
import math
from Animator import animate
import UpdateEdges as UE

import math

# default constructor in have an established NetworkX graph


class Simulator(object):
    def __init__(self, networkxObject, init_num_packets, max_initializations):
        G = DynamicNetwork(networkxObject, max_initializations)
        G.randomGeneratePackets(init_num_packets)
        self._dynetwork = G
        self._positions = nx.spring_layout(self._dynetwork._network)

        # save image of starting network
        node_labels = {}
        for node in self._dynetwork._network.nodes:
            node_labels[node] = len(self._dynetwork._network.nodes[node]['sending_queue']) + len(
                self._dynetwork._network.nodes[node]['receiving_queue'])
        nx.draw(self._dynetwork._network, pos=self._positions,
                labels=node_labels, font_weight='bold')
        edge_labels = nx.get_edge_attributes(
            self._dynetwork._network, 'edge_delay')
        nx.draw_networkx_edge_labels(
            self._dynetwork._network, pos=self._positions, edge_labels=edge_labels)
        script_dir = os.path.dirname(__file__)
        results_dir = os.path.join(script_dir, 'network_images/')
        if not os.path.isdir(results_dir):
            os.makedirs(results_dir)
        plt.figtext(0.1, 0.1, "total injections: "+str(init_num_packets))
        plt.savefig("network_images/dynet0.png")
        plt.clf()

# method to create Simulator with random generated graphs
    @classmethod
    def generateRandom(cls, node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type, max_initializations):
        # generate random Networkx Graph
        randomNetworkxGraph = Simulator.generateRandStaticGraph(
            node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type)
        return Simulator(randomNetworkxGraph, init_num_packets, max_initializations)

    @staticmethod
    def generateRandStaticGraph(node_count, edge_count, init_num_packets, max_queue=float('inf'), max_transmit=1, network_type='barabasi-albert'):
        # Initialize a Network using Networkx
        if network_type == 'barabasi-albert':
            networkxGraph = nx.barabasi_albert_graph(node_count, edge_count)
        else:
            networkxGraph = nx.gnm_random_graph(node_count, edge_count)

        """ Add "queue" to keep track of packets received at time step and those to be sent"""
        receiving_queue_dict, sending_queue_dict = {}, {}

        for i in range(node_count):
            temp = {'receiving_queue': []}
            temp2 = {'sending_queue': []}
            receiving_queue_dict.update({i: temp})
            sending_queue_dict.update({i: temp2})
        del temp, temp2
        '''Attribute added'''
        # node attributes
        nx.set_node_attributes(
            networkxGraph, max_transmit, 'max_send_capacity')
        nx.set_node_attributes(networkxGraph, max_queue,
                               'max_receive_capacity')
        nx.set_node_attributes(networkxGraph, max_queue, 'congestion_measure')
        nx.set_node_attributes(networkxGraph, receiving_queue_dict)
        nx.set_node_attributes(networkxGraph, sending_queue_dict)
        # edge attributes
        nx.set_edge_attributes(networkxGraph, 0, 'num_traversed')
        nx.set_edge_attributes(networkxGraph, 0, 'edge_delay')
        nx.set_edge_attributes(networkxGraph, 0, 'sine_state')
        '''CongestM Attribute added'''
        nx.set_node_attributes(networkxGraph, 0, 'max_queue_len')
        nx.set_node_attributes(networkxGraph, 0, 'avg_q_len_array')

        # max_weight for edges
        max_edge = 10
        for s_edge, e_edge in networkxGraph.edges:
            networkxGraph[s_edge][e_edge]['edge_delay'] = random.randint(
                0, max_edge)
            networkxGraph[s_edge][e_edge]['sine_state'] = random.uniform(
                0, math.pi)

        return networkxGraph

    def start(self, time_steps, min_edge_removal, max_edge_removal, init_num_packets, router_type='dijkstra', weight_type='None', plot_opt=True, edge_change_type='none', print_edge_weights=False):
        r = Router()
        stripped_list = []
        # Initialize with zeros so that plot starts at the origin
        step = [0]
        deliveries = [0]
        break_time = time_steps
        #pEdge = UpdateEdges()
        for i in range(1, time_steps):
            if i % 10 == 0:
                print("Currently at time step ", i)
                print("Number of initializations:", self._dynetwork._initializations)

            # Dynamic Edge Change
            UE.Delete(self._dynetwork, min_edge_removal, max_edge_removal)
            UE.Restore(self._dynetwork)
            if edge_change_type == 'none':
                pass
            elif edge_change_type == 'sinusoidal':
                UE.Sinusoidal(self._dynetwork)
            else:
                UE.Random_Walk(self._dynetwork)
                
            # Inject new packets
            temp_purgatory = copy.deepcopy(self._dynetwork._purgatory)
            self._dynetwork._purgatory = []
            for (index, wait) in temp_purgatory:
                self._dynetwork.GeneratePacket(index, wait)


            # Route packages one step according to Router.py
            r.router(self._dynetwork, router_type, weight_type)

            # Draw the current slice
            #node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
            if plot_opt:
                node_labels = {}
                for node in self._dynetwork._network.nodes:
                    node_labels[node] = len(self._dynetwork._network.nodes[node]['sending_queue']) + len(
                        self._dynetwork._network.nodes[node]['receiving_queue'])
                nx.draw(self._dynetwork._network, pos=self._positions,
                        labels=node_labels, font_weight='bold')
                if print_edge_weights:
                    edge_labels = nx.get_edge_attributes(
                        self._dynetwork._network, 'edge_delay')
                    nx.draw_networkx_edge_labels(
                        self._dynetwork._network, pos=self._positions, edge_labels=edge_labels)
                plt.axis('off')
                plt.figtext(0.1, 0.1, "total injections: "+ str(init_num_packets + self._dynetwork._initializations))
                plt.savefig("network_images/dynet" + str(i) + ".png")
                plt.clf()

            # Generate data for graph of cumulative deliveries
            step.append(i)
            deliveries.append(self._dynetwork._deliveries)

            # If all packages have been delivered before we reach the number of time steps, terminate the simulation
            if self._dynetwork._deliveries >= init_num_packets + self._dynetwork._max_initializations:
                break_time = i
                print('Package delivery finished in %i steps.' % break_time)
                break

        # After routing, use Animator.py to create animation.mp4
        if plot_opt and time_steps < 100:
            animate(break_time)

        # Calculate average delivery time across all packages
        print("Average Delivery Time:", sum(self._dynetwork._delivery_times)/len(self._dynetwork._delivery_times))

        # Generate plot for cumulative package deliveries over time
        if plot_opt:
            plt.clf()
            plt.axis('on')
            plt.plot(step, deliveries)
            plt.xlabel('Time Step')
            plt.xticks(np.arange(0, break_time+1, math.ceil(break_time/10)))
            plt.ylabel('Packages Delivered')
            plt.yticks(np.arange(0, init_num_packets +
                                 1, math.ceil(init_num_packets/10)))
            plt.savefig("package_delivery.png")


def main():
    '''graph features'''
    node_count = 20
    # Note that this is a measure of edges per added node, for Barbarsi. #Total number of edge for Erdos
    edge_count = 3
    init_num_packets = 100
    # specifies maximum bandwith for each edge
    max_transmit = 10
    # specifies maximum queue size for each node
    max_queue = 10

    '''simulation features'''
    time_steps = 500
    edge_removal_min = 0
    edge_removal_max = 5
    edge_change_type = ['none', 'sinusoidal', 'random-walk']
    network_type = ['barabasi-albert', 'erdos-renyi']
    weight_type = ['none', 'delay']
    router_type = ['dijkstra', 'floyd-warshall']
    plot_opt = True
    print_edge_weights = True
    max_new_packets = 1000

    dijkstraSimulator = Simulator.generateRandom(
        node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type[0], max_new_packets)
    dijkstraSimulator.start(time_steps, edge_removal_min, edge_removal_max, init_num_packets,
                            router_type[0], weight_type[1], plot_opt, edge_change_type[2], print_edge_weights)


if __name__ == "__main__":
    main()