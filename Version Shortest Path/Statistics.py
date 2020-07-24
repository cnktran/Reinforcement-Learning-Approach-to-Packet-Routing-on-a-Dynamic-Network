import Stat_Simulator
import matplotlib.pyplot as plt
import copy
import sys
import os
import numpy as np
import networkx as nx 

'''graph features'''
node_count = 50
# Note that this is a measure of edges per added node, for Barbarsi. #Total number of edge for Erdos
edge_count = 3
# specifies maximum bandwith for each edge
max_transmit = 10
# specifies maximum queue size for each node
max_queue = 15

'''simulation features'''
time_steps = 1000
edge_removal_min = 0
edge_removal_max = 10
edge_change_type = ['none', 'sinusoidal', 'random-walk']
network_type = ['barabasi-albert', 'erdos-renyi']
router_type = ['dijkstra', 'floyd-warshall']
weight_type = ['none', 'delay']
print_edge_weights = True
trials = 5
plot_opt = False
max_new_packets = 700 # maximum additional packets injection after initialization certain number of packets

# Different packet number 
network_load = np.arange(50, 550, 50)
#network_load = [2000]

'''statistics option'''
calculate_delivery_time = True
calculate_congestion_max_q_len = True
calculate_congestion_avg_q_len = True
calculate_congestion_perc_at_capacity = True
calculate_congestion_rejection = True
calculate_perc_empty = True

# Same networkX network
networkX = Stat_Simulator.Simulator.generateRandStaticGraph(
    node_count, edge_count, max_queue, max_transmit, network_type[0])
#fixed_positions = nx.spring_layout(networkX)



if max(network_load) >= node_count * max_queue:
    print("Too many packets, increase max_queue.")
    sys.exit()

avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []
avg_perc_empty_nodes =[]

for i in range(len(network_load)):
    
    curLoad = network_load[i]
    print("")
    print("Current load: ",curLoad)

    for curTri in range(trials):
        # create simulator object that has same network with different loads

        reset_network = copy.deepcopy(networkX)
        #print(len(reset_network.nodes))
        receiving_queue_dict, sending_queue_dict = {}, {}
        for j in range(node_count):
            temp = {'receiving_queue': []}
            temp2 = {'sending_queue': []}
            receiving_queue_dict.update({j: temp})
            sending_queue_dict.update({j: temp2})
        del temp
        del temp2
        nx.set_node_attributes(reset_network, receiving_queue_dict)
        nx.set_node_attributes(reset_network, sending_queue_dict)
        
        dynetworkSimulator = Stat_Simulator.Simulator(copy.deepcopy(reset_network), curLoad, max_new_packets)
    
        # run simulation (by main())
        Stat_Simulator.main(node_count, edge_count, curLoad, max_transmit, max_queue, time_steps,
                            edge_removal_min, edge_removal_max, network_type[0],
                            router_type[1], weight_type[1], edge_change_type[1], print_edge_weights, plot_opt, dynetworkSimulator)
    
        # store all measures
        avg_deliv.append(dynetworkSimulator._avg_deliv)
        maxNumPkts.append(dynetworkSimulator._max_queue_length)
        avg_q_len.append(dynetworkSimulator._avg_queue_length)
        avg_perc_at_capacity.append(dynetworkSimulator._avg_perc_at_capacity)
        rejectionNums.append(dynetworkSimulator._rejection_numbers/dynetworkSimulator._dynetwork._deliveries)
        avg_perc_empty_nodes.append(dynetworkSimulator._avg_perc_empty)


        dynetworkSimulator.clear_queues()

    print("Simulation "+str(i+1)+" done.")
    print("")

script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'statistics/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
plt.savefig(results_dir + "dynet" + str(i) + ".png")

if(calculate_delivery_time):
    print("Avg Delivery")
    print(network_load)
    print(np.around(np.array(avg_deliv),3))
    plt.clf()
    plt.title("Average Delivery Time vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_deliv)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Avg Delivery Time')
    plt.savefig(results_dir + "avg_deliv.png")
    plt.clf()

'''
Maximum length of each node's queue
'''
if(calculate_congestion_max_q_len):
    print("Max Queue Length")
    print(network_load)
    print(maxNumPkts)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold vs Network Load")
    plt.scatter(np.repeat(network_load, trials), maxNumPkts)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(results_dir + "maxNumPkts.png")
    plt.clf()

'''
Average length of node's queue through out the process of delivery when sending packets 
'''
if(calculate_congestion_avg_q_len):
    print("Average Non-Empty Queue Length")
    print(network_load)
    print(np.around(np.array(avg_q_len),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_q_len)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(results_dir + "avg_q_len.png")
    plt.clf()


'''
Average percent of node working at capacity (queue >= sending capability) at each time stamp 
'''
if(calculate_congestion_perc_at_capacity):
    print("Percent of Nodes at Capacity")
    print(network_load)
    print(np.around(np.array(avg_perc_at_capacity),3))
    plt.clf()
    plt.title("Percent of Nodes at Capacity vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_perc_at_capacity)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Percent of Nodes at Capacity (in percentage)')
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    plt.clf()

'''
Average Average Rejection Numbers at each time stamp 
'''
if(calculate_congestion_rejection):
    print("Average Rejection Numbers")
    print(network_load)
    print(np.around(np.array(rejectionNums),3))
    plt.clf()
    plt.title("Average Rejection Numbers vs Network Load")
    plt.scatter(np.repeat(network_load, trials), rejectionNums)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Number of packet rejections')
    plt.savefig(results_dir + "rejectionNums.png")
    plt.clf()

'''
Average Average Percent Empty Nodes at each time stamp 
'''
if(calculate_perc_empty):
    print("Percent of Empty Nodes")
    print(network_load)
    print(np.around(np.array(avg_perc_empty_nodes),3))
    plt.clf()
    plt.title("Percent of Empty Nodes Per Episode")
    plt.scatter(np.repeat(network_load, trials), avg_perc_empty_nodes)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Percent of Empty Nodes  (in percentage)')
    plt.savefig(results_dir + "avg_perc_empty.png")
    plt.clf()