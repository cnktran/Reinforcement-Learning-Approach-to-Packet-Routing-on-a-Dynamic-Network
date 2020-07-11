import networkx as nx
import os
from dynetwork import *
from router import Router
import matplotlib.pyplot as plt
from math import ceil
#from Animator import animate

# default constructor in have an established NetworkX graph


class Simulator(object):
    def __init__(self, networkxObject, init_num_packets):
        G = DynamicNetwork(networkxObject)
        G.randomGeneratePackets(init_num_packets)
        self._dynetwork = G

        '''Stats Measure results'''
        self._avg_deliv = 0
        self._max_queue_length = 0
        self._avg_queue_length = 0
        self._avg_perc_at_capacity = 0
# method to create Simulator with random generated graphs

    @classmethod
    def generateRandom(cls, node_count, edge_count, init_num_packets, max_queue, max_transmit, network_type):
        # generate random Networkx Graph
        randomNetworkxGraph = Simulator.generateRandStaticGraph(
            node_count, edge_count, max_queue, max_transmit, network_type)
        return Simulator(randomNetworkxGraph, init_num_packets)

    @staticmethod
    def generateRandStaticGraph(node_count, edge_count, max_queue=float('inf'), max_transmit=1, network_type='barabasi-albert'):
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
        nx.set_node_attributes(networkxGraph, receiving_queue_dict)
        nx.set_node_attributes(networkxGraph, sending_queue_dict)
        nx.set_edge_attributes(networkxGraph, 0, 'num_traversed')

        '''CongestM Attribute added'''
        nx.set_node_attributes(networkxGraph, 0, 'max_queue_len')
        nx.set_node_attributes(networkxGraph, 0, 'avg_q_len_array')

        return networkxGraph

    def start(self, time_steps, min_edge_removal, max_edge_removal, init_num_packets, router_type='dijkstra', plot_opt=True):
        r = Router()
        fixed_positions = nx.spring_layout(self._dynetwork._network)
        stripped_list = []
        # initialize with zeros so that plot starts at the origin
        step = [0]
        deliveries = [0]
        break_time = time_steps

        # iterate each simulation stamp
        for i in range(1, time_steps):
            # Dynamic Edges
            # First delete and add to stripped_list
            edges = self._dynetwork._network.edges()
            deletion_number = random.randint(
                min_edge_removal, min(max_edge_removal, len(edges) - 1))
            strip = random.sample(edges, k=deletion_number)
            self._dynetwork._network.remove_edges_from(strip)
            stripped_list.extend(strip)
            # Randomly restore deleted edges from stripped_list
            restore_number = random.randint(0, len(stripped_list))
            restore = random.choices(stripped_list, k=restore_number)
            self._dynetwork._network.add_edges_from(restore)

            # Route packages one step according to Router.py
            r.router(self._dynetwork, router_type)

            # Draw the current slice
            #node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
            if plot_opt:
                node_labels = {}
                for node in self._dynetwork._network.nodes:
                    node_labels[node] = len(
                        self._dynetwork._network.nodes[node]['sending_queue'])
                nx.draw(self._dynetwork._network, pos=fixed_positions,
                        labels=node_labels, font_weight='bold')
                script_dir = os.path.dirname(__file__)
                results_dir = os.path.join(script_dir, 'network_images/')
                if not os.path.isdir(results_dir):
                    os.makedirs(results_dir)
                sample_file_name = "sample"
                plt.savefig(results_dir + "dynet" + str(i) + ".png")
                plt.clf()

            # Generate data for graph of cumulative deliveries
            step.append(i)
            deliveries.append(self._dynetwork._deliveries)

            # If all packages have been delivered before we reach the number of time steps, terminate the simulation
            if self._dynetwork._deliveries == init_num_packets:
                break_time = i
                print('Package delivery finished in %i steps.' % break_time)
                break

        # After routing, use Animator.py to create animation.mp4
        if plot_opt:
            if break_time < 100:
                animate(break_time)
            else:
                "Cannot animate more than 100 time steps."

        # Calculate average delivery time across all packages
        print("Calculating average delivery time...")
        non_cum_step = step.copy()
        non_cum_deliv = []
        for i in range(len(deliveries) - 1):
            non_cum_deliv.append(deliveries[i+1] - deliveries[i])
        non_cum_step.pop(0)
        result = (
            sum([a * b for a, b in zip(non_cum_deliv, step)]))/init_num_packets
        self._avg_deliv = result
        print("Average Delivery Time:", result)

        # Generate plot for cumulative package deliveries over time
        if plot_opt:
            plt.clf()
            plt.plot(step, deliveries)
            plt.xlabel('Time Step')
            plt.xticks(np.arange(0, break_time+1, ceil(break_time/10)))
            plt.ylabel('Packages Delivered')
            plt.yticks(np.arange(0, init_num_packets +
                                 1, ceil(init_num_packets/10)))
            plt.savefig("package_delivery.png")


def main(
        node_count, edge_count, init_num_packets, max_transmit, max_queue, time_steps, min_edge_removal, max_edge_removal, network_type, router_type, plot_opt, dynetworkSimulator):
    # call start simulation
    (dynetworkSimulator.start(time_steps, min_edge_removal,
                              max_edge_removal, init_num_packets, router_type, plot_opt))

    # update congestion measures
    dynetworkSimulator._max_queue_length = dynetworkSimulator._dynetwork._network.nodes[
        0]['max_queue_len']
    dynetworkSimulator._avg_queue_length = np.average(
        dynetworkSimulator._dynetwork._avg_q_len_arr)

    dynetworkSimulator._avg_perc_at_capacity = np.average(
        dynetworkSimulator._dynetwork._avg_perc_at_capacity_arr)
