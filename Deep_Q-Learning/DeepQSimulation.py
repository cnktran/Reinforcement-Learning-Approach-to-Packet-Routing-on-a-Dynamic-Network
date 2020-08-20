import sys
from datetime import datetime
import torch.nn.functional as F
import time
from our_env import *
import matplotlib.pyplot as plt
import matplotlib
import json
import numpy
import os
matplotlib.use('Agg')

'''Open file Setting.json which contains learning parameters. '''
#main_dir = os.path.dirname(os.path.realpath(__file__))
#main_dir = main_dir + 'start/'
with open('Setting.json') as f:
    setting = json.load(f)

'''
This is the main file used to train and test Deep Q-learning on 
in a network packet routing enviornment
'''
now = datetime.now()

start_time = now.strftime("%H:%M:%S")
print("Current Time =", start_time)

''' aka number of rounds of routing '''
numEpisode = setting["Simulation"]["training_episodes"]
''' number of steps give the network to sent packet '''
time_steps = setting["Simulation"]["max_allowed_time_step_per_episode"]
''' mark True if want to generate graphs for stat measures while learning '''
learning_plot = setting["Simulation"]["learning_plot"]
''' mark True if want to generate graphs for stat measures for testing among various network loads '''
comparison_plots = setting["Simulation"]["test_diff_network_load_plot"]
plot_opt = setting["Simulation"]["plot_routing_network"]
''' target_update is the number of steps we wish to wait until we decide to update our network '''
TARGET_UPDATE = setting["Simulation"]["num_time_step_to_update_target_network"]

starting_size = setting["Simulation"]["test_network_load_min"]
ending_size = setting["Simulation"]["test_network_load_max"] + \
    setting["Simulation"]["test_network_load_step_size"]
step_size = setting["Simulation"]["test_network_load_step_size"]
network_load = np.arange(starting_size,
                         ending_size, step_size)  # np.arange(500, 5500, 500)
for i in network_load:
    if i <= 0:
        print("Error: Network load must be positive.")
        sys.exit()
trials = setting["Simulation"]["test_trials_per_load"]
# establish enviroment
env = dynetworkEnv()
env.reset(max(network_load))
'''

update_less : setting this to TRUE will restrict the optimizer for each NN to only be called once per time step t within each episode
              setting this to FALSE will allow the optimizer to called an unlimited number of times (will be called as many times as
              there are packets routed associated with a certain neural network 

'''
agent = QAgent(env.dynetwork)
if agent.config['update_less'] == False:
    agent.config["update_models"][:, :] = True

''' check valid input configuration '''
if agent.config["sample_memory"]+agent.config["recent_memory"]+agent.config["priority_memory"] != 1:
    print("Error: Check memory type!")
    sys.exit()


'''stats measures'''
avg_deliv_learning = []
maxNumPkts_learning = []
avg_q_len_learning = []
avg_perc_at_capacity_learning = []
rejectionNums_learning = []
avg_perc_empty_nodes_learning = []


past_reward = env.helper_calc_reward()
dqn0to1_reward_diff = []


f = open("DQN_Times", "a")
''' we simulate one instance of finite packet routing numEpisode times '''
for i_episode in range(numEpisode):
    print("---------- Episode:", i_episode+1, " ----------")
    step = []
    deliveries = []
    start = time.time()
    f.writelines(["Episode " + str(i_episode) + ":\n"])
    ''' iterate each time step try to finish routing within time_steps '''
    for t in range(time_steps):
        if (t+1) % 20 == 0:
            print("Time step", t + 1)
        ''' debugging, tells us how many time steps the episodes are 
        # print("at time step:", t)
        # print("Deliveries:", env.dynetwork._deliveries)
        '''
        env.updateWhole(agent)
        if agent.config['update_less']:
            agent.config["update_models"][:, :] = True
            for destination_node in range(len(agent.config["update_models"][0, :])):
                ''' We pass None as our current node to avoid pushing into memory '''
                agent.learn(env.dqn[destination_node],
                            None, 0, 0, destination_node)
            agent.config["update_models"][:, :] = False
        ''' debugging message, tells us how many times the neural network optimizer
        # print("at time step " + str(t) + " we called optimizer " + str(agent.config["entered"]))
        # agent.config['entered'] = 0
        # Draw the current slice
        '''
        if plot_opt:
            env.render()

        ''' store attributes for stats measure'''
        step.append(t)
        deliveries.append(copy.deepcopy(env.dynetwork._deliveries))
        if (t+1) % TARGET_UPDATE == 0:
            env.update_target_weights()

        if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
            print("done! Finished in " + str(t + 1) + " time steps")
            break
    end = time.time()
    f.writelines(["Epsilon: " + str(agent.config['epsilon']) + "\n"])
    print("Epsilon", agent.config['epsilon'])
    f.writelines(["pkts delivered: " + str(env.dynetwork._deliveries) + "\n"])
    print("pkts delivered:", env.dynetwork._deliveries)
    f.writelines(["Time: " + str(end - start) + "\n"])
    print("Time:", end - start)

    ''' stats measure after routing all packets '''
    avg_deliv_learning.append(env.calc_avg_delivery())
    maxNumPkts_learning.append(env.dynetwork._max_queue_length)
    avg_q_len_learning.append(np.average(env.dynetwork._avg_q_len_arr))
    avg_perc_at_capacity_learning.append(((
        np.sum(env.dynetwork._num_capacity_node)/np.sum(env.dynetwork._num_working_node))/t) * 100)
    avg_perc_empty_nodes_learning.append(
        (((np.sum(env.dynetwork._num_empty_node))/env.dynetwork.num_nodes)/t) * 100)
    rejectionNums_learning.append(
        env.dynetwork._rejections/(env.dynetwork._initializations + env.npackets))

    reward = env.helper_calc_reward()
    diff = torch.norm(past_reward - reward) / torch.norm(past_reward)
    past_reward = reward
    dqn0to1_reward_diff.append(diff.tolist())

    env.reset(max(network_load))
    reward_slice = np.array(dqn0to1_reward_diff[-5:])
    if ((reward_slice < 0.05).sum() == 5):
        numEpisode = i_episode + 1
        break
f.close()

now = datetime.now()
train_end_time = now.strftime("%H:%M:%S")

agent.config['epsilon'] = 0.0001
agent.config['decay_rate'] = 1
'''stats measures'''
''' After learning, testing begins on different network loads '''
avg_deliv = []
maxNumPkts = []
avg_q_len = []
avg_perc_at_capacity = []
rejectionNums = []
avg_perc_empty_nodes = []
for i in range(len(network_load)):
    curLoad = network_load[i]
    print("---------- Testing:", curLoad, " ----------")

    for currTrial in range(trials):
        env.reset(curLoad)
        step = []
        deliveries = []

        ''' iterate each time step try to finish routing within time_steps '''
        for t in range(time_steps):
            env.updateWhole(agent, learn=False)

            if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
                print("Finished trial ", currTrial)
                break

        '''STATS MEASURES'''
        avg_deliv.append(env.calc_avg_delivery())
        maxNumPkts.append(env.dynetwork._max_queue_length)
        avg_q_len.append(np.average(env.dynetwork._avg_q_len_arr))
        avg_perc_at_capacity.append(
            np.sum(env.dynetwork._num_capacity_node) / np.sum(env.dynetwork._num_working_node) * 100)

        avg_perc_empty_nodes.append(
            (np.sum(env.dynetwork._num_empty_node) / env.dynetwork.num_nodes/t) * 100)

        rejectionNums.append(env.dynetwork._rejections /
                             (env.dynetwork._initializations + env.npackets))

'''Create plots and learnRes folder in plots if they don't already exist'''
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'plots/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
learn_results_dir = os.path.join(script_dir, 'plots/learnRes/')
if not os.path.isdir(learn_results_dir):
    os.makedirs(learn_results_dir)

'''Start creating plots for measures over various network loads '''
if comparison_plots:
    print("Average Delivery Time")
    print(np.around(np.array(avg_deliv), 3))
    plt.clf()
    plt.title("Average Delivery Time vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_deliv)
    plt.xlabel('Number of packets')
    plt.ylabel('Avg Delivery Time (in steps)')
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
    print(np.around(np.array(avg_q_len), 3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_q_len)
    plt.xlabel('Number of packets')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(results_dir + "avg_q_len.png")
    plt.clf()

    print("Percent of Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity), 3))
    plt.clf()
    plt.title("Percent of Working Nodes at Capacity vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_perc_at_capacity)
    plt.xlabel('Number of packets')
    plt.ylabel('Percent of Working Nodes at Capacity')
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    plt.clf()

    print("Average Packet Idle Time")
    print(rejectionNums)
    plt.clf()
    plt.title("Average Packet Idle Time vs Network Load")
    plt.scatter(np.repeat(network_load, trials), rejectionNums)
    plt.xlabel('Number of packets')
    plt.ylabel('Packet Idle Time (in steps)')
    plt.savefig(results_dir + "avg_pkt_idle.png")
    plt.clf()

    print("Percent of Empty Nodes")
    print(np.around(np.array(avg_perc_empty_nodes), 3))
    plt.clf()
    plt.title("Percent of Empty Nodes vs Network Load")
    plt.scatter(np.repeat(network_load, trials), avg_perc_empty_nodes)
    plt.xlabel('Number of packets')
    plt.ylabel('Percent of Empty Nodes')
    plt.savefig(results_dir + "avg_perc_empty.png")
    plt.clf()

'''Create plots for metrics over Q-learning while it learns'''
if learning_plot:
    print("Average Delivery Time")
    print(avg_deliv_learning)
    plt.clf()
    plt.title("Average Delivery Time Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_deliv_learning)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.savefig(learn_results_dir + "avg_deliv_learning.png")
    plt.clf()

    print("Max Queue Length")
    print(maxNumPkts_learning)
    plt.clf()
    plt.title("Maximum Num of Pkts a Node Holds Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), maxNumPkts_learning)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "maxNumPkts_learning.png")
    plt.clf()

    print("Average Non-Empty Queue Length")
    print(np.around(np.array(avg_q_len_learning), 3))
    plt.clf()
    plt.title("Average Num of Pkts a Node Hold Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_q_len_learning)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets being hold by a Node')
    plt.savefig(learn_results_dir + "avg_q_len_learning.png")
    plt.clf()

    print("Percent of Working Nodes at Capacity")
    print(np.around(np.array(avg_perc_at_capacity_learning), 3))
    plt.clf()
    plt.title("Percent of Working Nodes at Capacity Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_at_capacity_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Working Nodes at Capacity (in percentage)')
    plt.savefig(learn_results_dir + "avg_perc_at_capacity_learning.png")
    plt.clf()

    print("Percent of Empty Nodes")
    print(np.around(np.array(avg_perc_empty_nodes_learning), 3))
    plt.clf()
    plt.title("Percent of Empty Nodes Per Episode")
    plt.scatter(list(range(1, numEpisode + 1)), avg_perc_empty_nodes_learning)
    plt.xlabel('Episode')
    plt.ylabel('Percent of Empty Nodes (in percentage)')
    plt.savefig(learn_results_dir + "avg_perc_empty_learning.png")
    plt.clf()

    print("Average Packet Idle Time Numbers")
    print(rejectionNums_learning)
    plt.clf()
    plt.title("Average Idle Time vs Network Load")
    plt.scatter(list(range(1, numEpisode + 1)), rejectionNums_learning)
    plt.xlabel('Number of packets')
    plt.ylabel('Packet Idle Time (in steps)')
    plt.savefig(learn_results_dir + "avg_pkt_idle_learning.png")
    plt.clf()

    print("Norm of Difference of Current and Past Rewards per Time Step")
    print(dqn0to1_reward_diff)
    plt.clf()
    plt.title(
        "Norm of Difference of Between Reward from Node 0 to Node 1 Per Episode")
    plt.scatter(list(range(2, numEpisode + 1)), dqn0to1_reward_diff[1:])
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    plt.savefig(learn_results_dir + "reward.png")
    plt.clf()

print("start Time =", start_time)
print("Train End Time =", train_end_time)
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Whole End Time =", current_time)

main_dir = os.path.dirname(os.path.realpath(__file__))

np.save(os.path.join(main_dir, "dqn_avg_deliv"), avg_deliv)
np.save(os.path.join(main_dir, "dqn_maxNumPkts"), maxNumPkts)
np.save(os.path.join(main_dir, "dqn_avg_capac"), avg_perc_at_capacity)
np.save(os.path.join(main_dir, "dqn_avg_idle"), rejectionNums)
np.save(os.path.join(main_dir, "dqn_avg_empty"), avg_perc_empty_nodes)
