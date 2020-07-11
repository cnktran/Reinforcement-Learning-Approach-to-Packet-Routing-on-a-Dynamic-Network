import Stat_Simulator
import matplotlib.pyplot as plt
import copy
import sys

'''graph features'''
node_count = 500
# Note that this is a measure of edges per added node, for Barbarsi. #Total number of edge for Erdos
edge_count = 3
# specifies maximum bandwith for each edge
max_transmit = 10
# specifies maximum queue size for each node
max_queue = 5

'''simulation features'''
time_steps = 200
edge_removal_min = 100
edge_removal_max = 200
network_type = ['barabasi-albert', 'erdos-renyi']
router_type = 'dijkstra'
plot_opt = False

'''statistics option'''
calculate_delivery_time = False
calculate_congestion_max_q_len = False
calculate_congestion_avg_q_len = False
calculate_congestion_perc_at_capacity = True

# Same networkX network
networkX = Stat_Simulator.Simulator.generateRandStaticGraph(
    node_count, edge_count, max_queue, max_transmit, network_type[0])

# Different packet number (ak)
network_load = [500, 700, 1000]

if max(network_load) >= node_count * max_queue:
    print("Too many packets, increase max_queue.")
    sys.exit()

avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
for i in range(len(network_load)):
    curLoad = network_load[i]

    # create simulator object that has same network with different loads
    dynetworkSimulator = Stat_Simulator.Simulator(copy.copy(networkX), curLoad)

    # run simulation (by main())
    Stat_Simulator.main(node_count, edge_count, curLoad, max_transmit, max_queue, time_steps,
                        edge_removal_min, edge_removal_max, network_type[0], router_type, plot_opt, dynetworkSimulator)

    # store all measures
    avg_deliv.append(dynetworkSimulator._avg_deliv)
    maxNumPkts.append(dynetworkSimulator._max_queue_length)
    avg_q_len.append(dynetworkSimulator._avg_queue_length)
    avg_perc_at_capacity.append(dynetworkSimulator._avg_perc_at_capacity)

    print("Simulation "+str(i+1)+" done.")


if(calculate_delivery_time):
    print("Avg Delivery")
    print(network_load)
    print(avg_deliv)
    plt.clf()
    plt.title("Average Delivery Time vs Network Load")
    plt.plot(network_load, avg_deliv)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Avg Delivery Time')
    plt.savefig("avg_deliv.png")
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
    plt.plot(network_load, maxNumPkts)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig("maxNumPkts.png")
    plt.clf()

'''
Average length of node's queue through out the process of delivery when sending packets 
'''
if(calculate_congestion_avg_q_len):
    print("Average Queue Length")
    print(network_load)
    print(avg_q_len)
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold vs Network Load")
    plt.plot(network_load, avg_q_len)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig("avg_q_len.png")
    plt.clf()


'''
Average percent of node working at capacity (queue >= sending capability) at each time stamp 
'''
if(calculate_congestion_perc_at_capacity):
    print("Percent of Nodes at Capacity")
    print(network_load)
    print(avg_perc_at_capacity)
    plt.clf()
    plt.title("Percent of Nodes at Capacity vs Network Load")
    plt.plot(network_load, avg_perc_at_capacity)
    plt.xlabel('Initial Number of Packets')
    plt.ylabel('Percent of Nodes at Capacity (in percentage)')
    plt.savefig("avg_perc_at_capacity.png")
    plt.clf()
