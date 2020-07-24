from our_env import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
'''
This program does complete Q-learning process
'''

numEpisode = 50  # aka number of rounds of routing
time_steps = 2000  # number of steps give the network to sent packet
learning_plot = True
comparison_plots = True
plot_opt = False

network_load = np.arange(500, 5500, 500)
trials = 5

# establish enviroment
env = dynetworkEnv()
env.resetForTest(max(network_load))
agent = QAgent(env.dynetwork)

'''stats measures'''
avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []

avg_deliv_learning = []
maxNumPkts_learning = []
avg_q_len_learning = []
avg_perc_at_capacity_learning = []
rejectionNums_learning = []


# learn numEpisode times
for i_episode in range(numEpisode):

    print("---------- Episode:", i_episode+1," ----------")
    step = []
    deliveries = []

    # iterate each time step try to finish routing within time_steps
    for t in range(time_steps):
        #print("at time step:", t)
        #print("Deliveries:", env.dynetwork._deliveries)

        # key function that obtain action and update Q-table
        env.updateWhole(agent)

        # Draw the current slice
        # node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
        if plot_opt:
            env.render()

        # store arributes for stats measure
        step.append(t)
        deliveries.append(copy.deepcopy(env.dynetwork._deliveries))
        #f = open("q-learning/dict.txt", "w")
        #f.write(str(agent.q))
        #f.close()

        #if i_episode == (numEpisode - 1):
        #    f = open("q-learning/dict.txt", "w")
        #    f.write(str(agent.q))
        #   f.close()


        if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
            print("done!")
            break

    
    # stats measure after routing all packets
    avg_deliv_learning.append(env.calc_avg_delivery())
    maxNumPkts_learning.append(env.dynetwork._max_queue_length)
    avg_q_len_learning.append(np.average(env.dynetwork._avg_q_len_arr))
    avg_perc_at_capacity_learning.append(
        np.sum(env.dynetwork._num_capacity_node) / np.sum(env.dynetwork._num_working_node) * 100)
    rejectionNums_learning.append(env.dynetwork._rejections)

    env.resetForTest(max(network_load))
    
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'plots/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)



#After learning, testing begin
avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []

for i in range(len(network_load)):
    curLoad = network_load[i]
    
    print("---------- Testing:", curLoad," ----------")
    
    for currTrial in range(trials):
        env.resetForTest(curLoad)
        step = []
        deliveries = []
    
        # iterate each time step try to finish routing within time_steps
        for t in range(time_steps):
            #print("at time step:", t)
            #print("Deliveries:", env.dynetwork._deliveries)
    
            # key function that obtain action and update Q-table
            env.updateWhole(agent, learn=False)
    
            # Draw the current slice
            # node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
    
            # store arributes for stats measure

            #f = open("q-learning/dict.txt", "w")
            #f.write(str(agent.q))
            #f.close()
    
            if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
                print("Finished trial ", currTrial)
                break
        
            '''STATS MEASURES'''
        avg_deliv.append(env.calc_avg_delivery())
        maxNumPkts.append(env.dynetwork._max_queue_length)
        avg_q_len.append(np.average(env.dynetwork._avg_q_len_arr))
        avg_perc_at_capacity.append(
            np.sum(env.dynetwork._num_capacity_node) / np.sum(env.dynetwork._num_working_node) * 100)
        rejectionNums.append(env.dynetwork._rejections)


if comparison_plots:
    print("Average Delivery Time")
    print(np.around(np.array(avg_deliv),3))
    plt.clf()
    plt.title("Average Delivery Time vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_deliv)
    plt.xlabel('Number of packets')
    plt.ylabel('Avg Delivery Time')
    plt.savefig(results_dir + "avg_deliv.png")
    plt.clf()

    print("Max Queue Length")
    print(maxNumPkts)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold vs Network Load")
    plt.scatter(np.repeat(network_load, trials), maxNumPkts)
    plt.xlabel('Number of packets')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(results_dir + "maxNumPkts.png")
    plt.clf()

    print("Average Non-Empty Queue Length")
    print(np.around(np.array(avg_q_len),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_q_len)
    plt.xlabel('Number of packets')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(results_dir + "avg_q_len.png")
    plt.clf()

    print("Percent of Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity),3))
    plt.clf()
    plt.title("Percent of Nodes at Capacity vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_perc_at_capacity)
    plt.xlabel('Number of packets')
    plt.ylabel('Percent of Nodes at Capacity (in percentage)')
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    plt.clf()

    print("Total Rejection Numbers")
    print(rejectionNums)
    plt.clf()
    plt.title("Total Rejection Numbers vs Network Load")
    plt.scatter(np.repeat(network_load, trials), rejectionNums)
    plt.xlabel('Number of packets')
    plt.ylabel('Number of packet rejections')
    plt.savefig(results_dir + "rejectionNums.png")
    plt.clf()

if learning_plot:
    print("Average Delivery Time")
    print(avg_deliv_learning)
    plt.clf()
    plt.title("Average Delivery Time Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_deliv_learning)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time')
    plt.savefig(results_dir + "avg_deliv_learning.png")
    plt.clf()

    print("Max Queue Length")
    print(maxNumPkts_learning)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), maxNumPkts_learning)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(results_dir + "maxNumPkts_learning.png")
    plt.clf()

    print("Average Non-Empty Queue Length")
    print(np.around(np.array(avg_q_len_learning),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_q_len_learning)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(results_dir + "avg_q_len_learning.png")
    plt.clf() 

    print("Percent of Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity_learning),3))
    plt.clf()
    plt.title("Percent of Nodes at Capacity Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_at_capacity_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Nodes at Capacity (in percentage)')
    plt.savefig(results_dir + "avg_perc_at_capacity_learning.png")
    plt.clf()

    print("Total Rejection Numbers")
    print(rejectionNums_learning)
    plt.clf()
    plt.title("Total Rejection Numbers Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), rejectionNums_learning)
    plt.xlabel('Episode')
    plt.ylabel('Number of packet rejections')
    plt.savefig(results_dir + "rejectionNums_learning.png")
    plt.clf()
    