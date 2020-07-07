from dynetwork import *

# default constructor in have an established NetworkX graph


class Simulator(object):
    def __init__(self, networkxObject, init_num_packets):
        G = DynamicNetwork(networkxObject)
        G.randomGeneratePackets(init_num_packets)

        self._dynetwork = G


# method to create Simulator with random generated graphs


    @classmethod
    def generateRandom(cls, node_count, edge_count, max_capacity, init_num_packets):

        # generate random Networkx Graph
        randomNetworkxGraph = Simulator.generateRandStaticGraph(
            node_count, edge_count, max_capacity)

        return Simulator(randomNetworkxGraph, init_num_packets)

    @staticmethod
    def generateRandStaticGraph(node_count, edge_count, max_capacity):
        # Initialize a Network using Networkx
        networkxGraph = nx.barabasi_albert_graph(node_count, edge_count)
        # Add "queue" to keep track of packets
        p_queue_dict = {}
        for i in range(node_count):
            temp = {'p_queue': Queue(max_capacity)}
            p_queue_dict.update({i: temp})
        del temp

        '''Attribute added'''
        nx.set_node_attributes(networkxGraph, max_capacity, 'max_capacity')
        nx.set_node_attributes(networkxGraph, p_queue_dict)

        return networkxGraph

    def start(self, time_steps, edge_removal_min, edge_removal_max, init_num_packets):
        # Dynamic Edge Change
        fixed_positions = nx.spring_layout(self._dynetwork._network)
        stripped_list = []
        r = Router()

        for i in range(1, time_steps):
            # delete some edges
            edges = self._dynetwork._network.edges()
            deletion_number = random.randint(
                edge_removal_min, min(edge_removal_max, len(edges) - 1))
            strip = random.sample(edges, k=deletion_number)
            self._dynetwork._network.remove_edges_from(strip)
            stripped_list.extend(strip)
            # restore some deleted edges
            restore_number = random.randint(0, len(stripped_list))
            restore = random.choices(stripped_list, k=restore_number)
            self._dynetwork._network.add_edges_from(restore)
            # perform routing
            r.dijkstra_router(self._dynetwork)
            # draw network
            node_queues = nx.get_node_attributes(
                self._dynetwork._network, 'p_queue')
            node_labels = {}

            for node, atr in node_queues.items():
                node_labels[node] = atr.qsize()

            nx.draw(self._dynetwork._network, pos=fixed_positions,
                    labels=node_labels, font_weight='bold')
            plt.savefig("network_images/dynet" + str(i) + ".png")
            plt.clf()

            if self._dynetwork._deliveries == init_num_packets:
                print("Simulation done in " + str(i))
                break
            print(self._dynetwork._deliveries)


def main():
    '''graph features'''
    node_count = 100
    edge_count = 5  # Note that this is a measure of edges per added node, not total number of edges
    max_capacity = 5
    init_num_packets = 100

    '''simulation features'''
    time_steps = 10
    edge_removal_min = 0
    edge_removal_max = 10

    dijkstraSimulator = Simulator.generateRandom(
        node_count, edge_count, max_capacity, init_num_packets)
    dijkstraSimulator.start(time_steps, edge_removal_min,
                            edge_removal_max, init_num_packets)


if __name__ == "__main__":
    main()
