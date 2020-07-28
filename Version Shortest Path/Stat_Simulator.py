import networkx as nx
import os
from dynetwork import *
from router import Router
import matplotlib.pyplot as plt
import math
import UpdateEdges as UE

# default constructor in have an established NetworkX graph


class Simulator(object):
    def __init__(self, networkxObject, init_num_packets, max_initializations):
        self._dynetwork = DynamicNetwork(networkxObject, max_initializations)
        self._dynetwork.randomGeneratePackets(init_num_packets)
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

        '''Stats Measure results'''
        self._avg_deliv = 0
        self._max_queue_length = 0
        self._avg_queue_length = 0
        self._avg_perc_at_capacity = 0
        self._rejection_numbers = 0
        self._avg_perc_empty =0

# method to create Simulator with random generated graphs

    @classmethod
    def generateRandom(cls, node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type, max_initializations):
        # generate random Networkx Graph
        randomNetworkxGraph = Simulator.generateRandStaticGraph(
            node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type)
        return Simulator(randomNetworkxGraph, init_num_packets, max_initializations)

    @staticmethod
    def generateRandStaticGraph(node_count, edge_count, max_queue=float('inf'), max_transmit=10, network_type='barabasi-albert'):
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

        del temp
        del temp2
        '''Attribute added'''
        # deleted max node capacity
        nx.set_node_attributes(
            networkxGraph, max_transmit, 'max_send_capacity')
        nx.set_node_attributes(networkxGraph, max_queue,
                               'max_receive_capacity')
        nx.set_node_attributes(networkxGraph, max_queue, 'congestion_measure')
        nx.set_node_attributes(networkxGraph, receiving_queue_dict)
        nx.set_node_attributes(networkxGraph, sending_queue_dict)
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

    def clear_queues(self):
        for nodeIdx in self._dynetwork._network.nodes:
            self._dynetwork._network.nodes[nodeIdx]['receiving_queue'] = []
            self._dynetwork._network.nodes[nodeIdx]['sending_queue'] = []
        
    def start(self, time_steps, min_edge_removal, max_edge_removal, init_num_packets, router_type='dijkstra', weight_type='delay', plot_opt=False, edge_change_type='sinusoidal', print_edge_weights=False):
        r = Router()
        stripped_list = []
        # Initialize with zeros so that plot starts at the origin
        step = [0]
        deliveries = [0]
        break_time = time_steps
        # pEdge = UpdateEdges()
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
            # node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
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
            if self._dynetwork._deliveries >= init_num_packets:
                break_time = i
                print('Package delivery finished in %i steps.' % break_time)
                break

        # After routing, use Animator.py to create animation.mp4
        if plot_opt and time_steps < 100:
            animate(break_time)

        # Calculate average delivery time across all packages
        deliv_time = sum(self._dynetwork._delivery_times)/len(self._dynetwork._delivery_times)
        print("Average Delivery Time:", deliv_time)
        return(deliv_time)

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


def main(
        node_count, edge_count, init_num_packets, max_transmit, max_queue, time_steps, min_edge_removal,
        max_edge_removal, network_type, router_type, weight_type, edge_change_type, print_edge_weights, plot_opt, dynetworkSimulator):

    # call start simulation
    dynetworkSimulator._avg_deliv = dynetworkSimulator.start(time_steps, min_edge_removal,
                             max_edge_removal, init_num_packets, router_type, weight_type, plot_opt, edge_change_type, print_edge_weights)
                             
    # update congestion measures
    dynetworkSimulator._max_queue_length = dynetworkSimulator._dynetwork._max_queue_length
    dynetworkSimulator._avg_queue_length = np.average(
        dynetworkSimulator._dynetwork._avg_q_len_arr)

    dynetworkSimulator._avg_perc_at_capacity = np.sum(
        dynetworkSimulator._dynetwork._num_capacity_node)/np.sum(
        dynetworkSimulator._dynetwork._num_working_node)*100

    dynetworkSimulator._avg_perc_empty = np.average(dynetworkSimulator._dynetwork._num_empty_node)*100

    dynetworkSimulator._rejection_numbers = dynetworkSimulator._dynetwork._rejections