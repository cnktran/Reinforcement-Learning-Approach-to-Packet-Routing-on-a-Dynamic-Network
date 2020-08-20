from our_env import *
import matplotlib
import matplotlib.pyplot as plt
'''
This program generates a network, teaches a Q-learning agent
to route packets, and tests both the learned Q-routing policy
and Shortest Path for routing on the network over various
network loads.
'''

'''One episode starts with initialization of all the packets and ends with delivery of all of
env.npackets + env.max_initializations packets OR after time_steps.'''
numEpisode = 30 
'''Max length of one episode'''
time_steps = 2000
'''Specify reward function (listed in our_env.py)'''
rewardfunction = 'reward5'
'''Mark true to generate plots of performance while learning'''
learning_plot = True
'''Mark true to generate plots of performance for different test network loads'''
comparison_plots = True
'''Number of times to repeat each value in network_load list'''
trials = 5
'''Mark true to create .mp4 example of routing of 1 packet for each network load.
   Increases runtime and discouraged for large networks '''
show_example_comparison = False
'''Mark true to perform shortest path simultaneously during testing for comparison to Q-learning'''
sp = True
'''Initialize environment'''
env = dynetworkEnv()
'''Specify list of network loads to test'''
network_load = np.arange(500, 5500, 500)
for i in network_load:
    if i <= 0:
        print("Error: Network load must be positive.")
        sys.exit
    if i >= env.nnodes*env.max_queue:
        print("Error: Network load cannot exceed nodes times max queue size.")
env.reset(max(network_load), False)
agent = QAgent(env.dynetwork)

'''Performance Measures for Q-Learning While Learning'''
avg_deliv_learning = []
maxNumPkts_learning = []
avg_q_len_learning = []
avg_perc_at_capacity_learning = []
rejectionNums_learning = []
avg_perc_empty_nodes_learning=[]


'''----------------------LEARNING PROCESS--------------------------'''
for i_episode in range(numEpisode):
    print("---------- Episode:", i_episode+1," ----------")
    step = []
    deliveries = []
    '''iterate each time step try to finish routing within time_steps'''
    for t in range(time_steps):
        '''key function that obtain action and update Q-table'''
        env.updateWhole(agent, rewardfun=rewardfunction)

        '''store atributes for performance measures'''
        step.append(t)
        deliveries.append(copy.deepcopy(env.dynetwork._deliveries))

        if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
            print("done!")
            break
        
    '''Save all performance measures'''
    avg_deliv_learning.append(env.calc_avg_delivery())
    maxNumPkts_learning.append(env.dynetwork._max_queue_length)
    avg_q_len_learning.append(np.average(env.dynetwork._avg_q_len_arr))
    avg_perc_at_capacity_learning.append(((
       np.sum(env.dynetwork._num_capacity_node)/np.sum(env.dynetwork._num_working_node))/t) * 100)
    avg_perc_empty_nodes_learning.append((((np.sum(env.dynetwork._num_empty_node))/env.nnodes)/t) *100)
    rejectionNums_learning.append(env.dynetwork._rejections/(env.dynetwork._initializations + env.npackets))
    print(env.calc_avg_delivery())
    
    env.reset(max(network_load), False)

script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'plots/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
learn_results_dir = os.path.join(script_dir, 'plots/learnRes/')
if not os.path.isdir(learn_results_dir):
    os.makedirs(learn_results_dir)

'''Produces plots for average delivery time and congestion while learning '''
if learning_plot:
    print("Average Delivery Time")
    print(avg_deliv_learning)
    plt.clf()
    plt.title("Average Delivery Time Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_deliv_learning)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.savefig(learn_results_dir + "avg_deliv_learning.png")
    np.save("avg_deliv_learning", avg_deliv_learning)
    plt.clf()

    print("Max Queue Length")
    print(maxNumPkts_learning)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), maxNumPkts_learning)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "maxNumPkts_learning.png")
    np.save("maxNumPkts_learning", maxNumPkts_learning)
    plt.clf()

    print("Average Non-Empty Queue Length")
    print(np.around(np.array(avg_q_len_learning),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_q_len_learning)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "avg_q_len_learning.png")
    np.save("avg_q_len_learning", avg_q_len_learning)
    plt.clf() 

    print("Percent of Working Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity_learning),3))
    plt.clf()
    plt.title("Percent of Working Nodes at Capacity Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_at_capacity_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Working Nodes at Capacity')
    plt.savefig(learn_results_dir + "avg_perc_at_capacity_learning.png")
    np.save("avg_perc_at_capacity_learning", avg_perc_at_capacity_learning)
    plt.clf()

    print("Percent of Empty Nodes")
    print(np.around(np.array(avg_perc_empty_nodes_learning),3))
    plt.clf()
    plt.title("Percent of Empty Nodes Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_empty_nodes_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Empty Nodes')
    plt.savefig(learn_results_dir + "avg_perc_empty_learning.png")
    np.save("avg_perc_empty_nodes_learning", avg_perc_empty_nodes_learning)
    plt.clf()

    print("Average Packet Idle Time Numbers")
    print(rejectionNums_learning)
    plt.clf()
    plt.title("Average Idle Time Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), rejectionNums_learning)
    plt.xlabel('Episode')
    plt.ylabel('Packet Idle Time (in steps)')
    plt.savefig(learn_results_dir + "avg_pkt_idle_learning.png")
    np.save("avg_pkt_idle_learning", rejectionNums_learning)
    plt.clf()

'''--------------------------TESTING PROCESS--------------------------'''
'''Performance Measures for Q-Learning'''
avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []
avg_perc_empty_nodes=[]

'''Performance Measures for Shortest Path'''
sp_avg_deliv = []
sp_maxNumPkts = []
sp_avg_q_len = []
sp_avg_perc_at_capacity = []
sp_rejectionNums = []
sp_avg_perc_empty_nodes=[]


for i in range(len(network_load)):
    curLoad = network_load[i]
    
    print("---------- Testing Load of ", curLoad," ----------")
    
    '''Route the first packet using Q-Learning and using SP, animate both one after the other, allow user to close'''
    if show_example_comparison:
        env.reset(curLoad, True)
        env.routing_example(agent, curLoad)

    for currTrial in range(trials):
        env.reset(curLoad, True)

        step = []
        deliveries = []
        sp_step = []
        sp_deliveries = []
    
        '''iterate each time step try to finish routing within time_steps'''
        for t in range(time_steps):
    
            total = env.npackets + env.dynetwork._max_initializations
            q_done = (env.dynetwork._deliveries >= total)
            if sp:
                s_done = (env.dynetwork.sp_deliveries >= total)
            else:
                s_done = True
            env.updateWhole(agent, learn=False, q=not q_done, sp=not s_done, rewardfun=rewardfunction, savesteps=False)

            if q_done and s_done:
                print("Finished trial ", currTrial)
                break
        
        '''STATS MEASURES'''
        avg_deliv.append(env.calc_avg_delivery())
        maxNumPkts.append(env.dynetwork._max_queue_length)
        avg_q_len.append(np.average(env.dynetwork._avg_q_len_arr))
        avg_perc_at_capacity.append(np.sum(env.dynetwork._num_capacity_node) / np.sum(env.dynetwork._num_working_node) * 100)
        avg_perc_empty_nodes.append((np.sum(env.dynetwork._num_empty_node) / env.nnodes/t) *100)
        rejectionNums.append(env.dynetwork._rejections/(env.dynetwork._initializations + env.npackets))

        if sp:
            sp_avg_deliv.append(env.calc_avg_delivery(True))
            sp_maxNumPkts.append(env.dynetwork.sp_max_queue_length)
            sp_avg_q_len.append(np.average(env.dynetwork.sp_avg_q_len_arr))
            sp_avg_perc_at_capacity.append(np.sum(env.dynetwork.sp_num_capacity_node) / np.sum(env.dynetwork.sp_num_working_node) * 100)
            sp_avg_perc_empty_nodes.append((np.sum(env.dynetwork.sp_num_empty_node) / env.nnodes/t) *100)
            sp_rejectionNums.append(env.dynetwork.sp_rejections/(env.dynetwork.sp_initializations + env.npackets))

if comparison_plots:
    x = np.repeat(network_load, trials)

    print("Average Delivery Time")
    print("Q-Learning: ", np.around(np.array(avg_deliv),3))
    if sp:
        print("Shortest Path: ", np.around(np.array(sp_avg_deliv),3))
    plt.clf()
    plt.title("Average Delivery Time vs Network Load")
    plt.scatter(x, avg_deliv, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_avg_deliv, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.legend()
    plt.savefig(results_dir + "avg_deliv.png")
    np.save("sp_avg_deliv", sp_avg_deliv)
    np.save("ql_avg_deliv", avg_deliv)
    plt.clf()

    print("Max Queue Length")
    print("Q-Learning: ", maxNumPkts)
    if sp:
        print("Shortest Path: ", sp_maxNumPkts)
    plt.clf()
    plt.title("Maximum Num of Pkts Nodes Held vs Network Load")
    plt.scatter(x, maxNumPkts, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_maxNumPkts, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Maximum Number of Packets Held')
    plt.legend()
    plt.savefig(results_dir + "maxNumPkts.png")
    np.save("sp_maxNumPkts", sp_maxNumPkts)
    np.save("ql_maxNumPkts", maxNumPkts)
    plt.clf()

    print("Average Non-Empty Queue Length")
    print("Q-Learning: ", np.around(np.array(avg_q_len),3))
    if sp:
        print("Shortest Path: ", np.around(np.array(sp_avg_q_len), 3))
    plt.clf()
    plt.title("Average Num of Pkts Nodes Held vs Network Load")
    plt.scatter(x, avg_q_len, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_avg_q_len, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Average Number of Packets Held')
    plt.legend()
    plt.savefig(results_dir + "avg_q_len.png")
    np.save("sp_avg_q_len", sp_avg_q_len)
    np.save("ql_avg_q_len", avg_q_len)
    plt.clf()

    print("Percent of Nodes at Capacity")
    print("Q-Learning: ", np.around(np.array(avg_perc_at_capacity),3))
    if sp:
        print("Shortest Path: ", np.around(np.array(sp_avg_perc_at_capacity), 3))
    plt.clf()
    plt.title("Percent of Working Nodes at Capacity vs Network Load")
    plt.scatter(x, avg_perc_at_capacity, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_avg_perc_at_capacity, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Percentage of Working Nodes at Capacity')
    plt.legend()
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    np.save("sp_avg_perc_at_capacity", sp_avg_perc_at_capacity)
    np.save("ql_avg_perc_at_capacity", avg_perc_at_capacity)
    plt.clf()

    print("Average Packet Idle Time")
    print("Q-Routing: ", rejectionNums)
    if sp:
        print("Shortest Path: ", sp_rejectionNums)
    plt.clf()
    plt.title("Average Packet Idle Time vs Network Load")
    plt.scatter(x, rejectionNums, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_rejectionNums, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Time Steps Spent Idle')
    plt.legend()
    plt.savefig(results_dir + "avg_pkt_idle.png")
    np.save("sp_rejectionNums", sp_rejectionNums)
    np.save("ql_rejectionNums", rejectionNums)
    plt.clf()

    print("Percent of Empty Nodes")
    print("Q-Routing: ", np.around(np.array(avg_perc_empty_nodes), 3))
    if sp:
        print("Shortest Path: ", np.around(np.array(sp_avg_perc_empty_nodes), 3))
    plt.clf()
    plt.title("Percent of Empty Nodes vs Network Load")
    plt.scatter(x, avg_perc_empty_nodes, c='blue', label='Q-Learning')
    if sp:
        plt.scatter(x, sp_avg_perc_empty_nodes, c='orange', label='Shortest Path')
    plt.xlabel('Number of packets')
    plt.ylabel('Percentage of Nodes Empty')
    plt.legend()
    plt.savefig(results_dir + "avg_perc_empty.png")
    np.save("sp_avg_perc_empty_nodes", sp_avg_perc_empty_nodes)
    np.save("ql_avg_perc_empty_nodes", avg_perc_empty_nodes)
    plt.clf()
    
if learning_plot:
    print("Average Delivery Time While Learning")
    print(avg_deliv_learning)
    plt.clf()
    plt.title("Average Delivery Time Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_deliv_learning)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.savefig(learn_results_dir + "avg_deliv_learning.png")
    plt.clf()

    print("Max Queue Length While Learning")
    print(maxNumPkts_learning)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), maxNumPkts_learning)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "maxNumPkts_learning.png")
    plt.clf()

    print("Average Non-Empty Queue Length While Learning")
    print(np.around(np.array(avg_q_len_learning),3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_q_len_learning)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "avg_q_len_learning.png")
    plt.clf() 

    print("Percent of Working Nodes at Capacity While Learning")
    print(np.around(np.array(avg_perc_at_capacity_learning),3))
    plt.clf()
    plt.title("Percent of Working Nodes at Capacity Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_at_capacity_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Working Nodes at Capacity')
    plt.savefig(learn_results_dir + "avg_perc_at_capacity_learning.png")
    plt.clf()

    print("Percent of Empty Nodes While Learning")
    print(np.around(np.array(avg_perc_empty_nodes_learning),3))
    plt.clf()
    plt.title("Percent of Empty Nodes Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_empty_nodes_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Empty Nodes')
    plt.savefig(learn_results_dir + "avg_perc_empty_learning.png")
    plt.clf()

    print("Average Packet Idle Time Numbers While Learning")
    print(rejectionNums)
    plt.clf()
    plt.title("Average Idle Time vs Network Load")
    plt.scatter(np.repeat(network_load, trials), rejectionNums)
    plt.xlabel('Number of packets')
    plt.ylabel('Packet Idle Time (in steps)')
    plt.savefig(learn_results_dir + "avg_pkt_idle_learning.png")
    plt.clf()
    