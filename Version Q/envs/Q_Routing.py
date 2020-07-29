from our_env import *
import matplotlib.pyplot as plt
'''
This program manages the overall Q-learning process
'''
numEpisode = 60  # aka number of rounds of routing
time_steps = 2000  # number of steps give the network to sent packet
learning_plot = True # mark True if want to generate graphs for stat measures while learning
plot_opt = False # mark True if want to generate pictures of our network at each time step for all episodes in our simulation

# establish enviroment
env = dynetworkEnv()
agent = QAgent(env.dynetwork)
'''stats measures'''
avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []
avg_perc_empty_nodes =[]
# learn numEpisode times
for i_episode in range(numEpisode):
    print("---------- Episode:", i_episode+1," ----------")
    step = []
    deliveries = []

    """ iterate each time step try to finish routing within time_steps """
    for t in range(time_steps):
        # key function that obtain action and update Q-table
        env.updateWhole(agent)
        
        # Draw the current slice
        if plot_opt:
            env.render(t)
            
        # stores the final Q-table after all episodes have complete 
        if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
            print("done!")
            if i_episode == (numEpisode - 1):
                f = open("q-learning/dict.txt", "w")
                f.write(str(agent.q))
                f.close()
            break

    # stats measure after routing all packets
    avg_deliv.append(env.calc_avg_delivery())
    maxNumPkts.append(env.dynetwork._max_queue_length)
    avg_q_len.append(np.average(env.dynetwork._avg_q_len_arr))

    avg_perc_at_capacity.append(
        (np.sum(env.dynetwork._num_capacity_node) / np.sum(env.dynetwork._num_working_node)) * 100)
    avg_perc_empty_nodes.append(
        (np.sum(env.dynetwork._num_empty_node) / env.dynetwork.num_nodes) *100)
    rejectionNums.append(env.dynetwork._rejections/env.dynetwork._deliveries)
    env.reset()

script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, '.')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

if learning_plot:
    print("Average Delivery Time")
    print(np.around(np.array(avg_deliv),3))
    plt.clf()
    plt.title("Average Delivery Time Per Packet")
    plt.scatter(range(1, numEpisode + 1), avg_deliv)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time')
    plt.savefig(results_dir + "avg_deliv.png")
    plt.clf()

    print("Max Queue Length")
    print(maxNumPkts)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold Vs Episode")
    plt.scatter(list(range(1, numEpisode + 1)), maxNumPkts)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(results_dir + "maxNumPkts.png")
    plt.clf()

    print("Average Non-Empty Queue Length")
    print(np.around(np.array(avg_q_len),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_q_len)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(results_dir + "avg_q_len.png")
    plt.clf()

    print("Percent of Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity),3))
    plt.clf()
    plt.title("Percent of Nodes at Capacity Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_at_capacity)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Nodes at Capacity (in percentage)')
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    plt.clf()

    print("Percent of Empty Nodes")
    print(np.around(np.array(avg_perc_empty_nodes),3))
    plt.clf()
    plt.title("Percent of Empty Nodes Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_empty_nodes)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Empty Nodes  (in percentage)')
    plt.savefig(results_dir + "avg_perc_empty.png")
    plt.clf()

    print("Average Rejection Numbers")
    print(np.around(np.array(rejectionNums),3))
    plt.clf()
    plt.title("Average Rejection Numbers Per Packet")
    plt.scatter(list(range(1, numEpisode + 1)), rejectionNums)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of packet rejections')
    plt.savefig(results_dir + "rejectionNums.png")
    plt.clf()