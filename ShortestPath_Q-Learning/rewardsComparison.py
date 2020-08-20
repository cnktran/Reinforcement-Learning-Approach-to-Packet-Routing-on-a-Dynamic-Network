from our_env import *
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
'''
This program generates a network, teaches a Q-learning agent
to route packets, and tests both the learned Q-routing policy
and Shortest Path for routing on the network over various
network loads.
'''

'''One episode starts with initialization of all the packets and ends with delivery of all of
env.npackets + env.max_initializations packets OR after time_steps.'''
numEpisode = 60 
'''Max length of one episode'''
time_steps = 2000
'''Mark true to generate plots of performance while learning'''
learning_plot = True
'''Mark true to generate plots of performance for different test network loads'''
comparison_plots = True
'''Number of times to repeat each value in network_load list'''
trials = 5
'''Specify list of network loads to test'''
network_load = np.arange(500, 5500, 500)
'''Establish the environment'''
env = dynetworkEnv()
for i in network_load:
    if i <= 0:
        print("Error: Network load must be positive.")
        sys.exit
    if i >= env.nnodes*env.max_queue:
        print("Error: Network load cannot exceed nodes times max queue size.")
        sys.exit
env.reset(max(network_load), False)

'''Which reward functions (specified in our_env.py) should be tested'''
reward1 = True
reward2 = True
reward3 = True
reward4 = True
reward5 = True
reward6 = False
reward7 = False
color_list = ['blue', 'orange', 'green', 'magenta', 'red', 'cyan', 'yellow']
reward_list = [reward1, reward2, reward3, reward4, reward5, reward6, reward7]

rewarddict = {}
def initialize_learning_lists(name):
    rewarddict[name]['avg_deliv_learning'] = []
    rewarddict[name]['maxNumPkts_learning'] = []
    rewarddict[name]['avg_q_len_learning'] = []
    rewarddict[name]['avg_perc_at_capacity_learning'] = []
    rewarddict[name]['rejectionNums_learning'] = []
    rewarddict[name]['avg_perc_empty_nodes_learning'] = []

def initialize_performance_lists(name):
    rewarddict[name]['avg_deliv'] = []
    rewarddict[name]['maxNumPkts'] = []
    rewarddict[name]['avg_q_len'] = []
    rewarddict[name]['avg_perc_at_capacity'] = []
    rewarddict[name]['rejectionNums'] = []
    rewarddict[name]['avg_perc_empty_nodes'] = []

'''----------------------LEARNING PROCESS--------------------------'''
def learn(reward):
    agent = rewarddict[reward]['agent']
    print("Training Function "+reward)
    for i_episode in range(numEpisode):
        print("---------- Episode:", i_episode+1," ----------")
        step = []
        deliveries = []
        for t in range(time_steps):
            env.updateWhole(agent, rewardfun=reward)

            step.append(t)
            deliveries.append(copy.deepcopy(env.dynetwork._deliveries))

            if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
                print("done!")
                break
            
        rewarddict[reward]['avg_deliv_learning'].append(env.calc_avg_delivery())
        rewarddict[reward]['maxNumPkts_learning'].append(env.dynetwork._max_queue_length)
        rewarddict[reward]['avg_q_len_learning'].append(np.average(env.dynetwork._avg_q_len_arr))
        rewarddict[reward]['avg_perc_at_capacity_learning'].append(((
           np.sum(env.dynetwork._num_capacity_node)/np.sum(env.dynetwork._num_working_node))/t) * 100)
        rewarddict[reward]['avg_perc_empty_nodes_learning'].append((((np.sum(env.dynetwork._num_empty_node))/env.nnodes)/t) *100)
        rewarddict[reward]['rejectionNums_learning'].append(env.dynetwork._rejections/(env.dynetwork._initializations + env.npackets))
        
        env.reset(max(network_load), False)

'''--------------------------TESTING PROCESS--------------------------'''
def test(reward):
    print("Testing Function "+reward)
    agent = rewarddict[reward]['agent']
    for i in range(len(network_load)):
        curLoad = network_load[i]
        
        print("---------- Testing Load of ", curLoad," ----------")
        for currTrial in range(trials):
            env.reset(curLoad, False)
            step = []
            deliveries = []

            for t in range(time_steps):      
                env.updateWhole(agent, learn=False, rewardfun=reward)

                if (env.dynetwork._deliveries >= (env.npackets + env.dynetwork._max_initializations)):
                    print("done!")
                    break
            
            rewarddict[reward]['avg_deliv'].append(env.calc_avg_delivery())
            rewarddict[reward]['maxNumPkts'].append(env.dynetwork._max_queue_length)
            rewarddict[reward]['avg_q_len'].append(np.average(env.dynetwork._avg_q_len_arr))
            rewarddict[reward]['avg_perc_at_capacity'].append(((
               np.sum(env.dynetwork._num_capacity_node)/np.sum(env.dynetwork._num_working_node))/t) * 100)
            rewarddict[reward]['avg_perc_empty_nodes'].append((((np.sum(env.dynetwork._num_empty_node))/env.nnodes)/t) *100)
            rewarddict[reward]['rejectionNums'].append(env.dynetwork._rejections/(env.dynetwork._initializations + env.npackets))

for i in range(len(reward_list)):
    if reward_list[i]:
        key = 'reward'+str(i+1)
        rewarddict[key] = {}
        if learning_plot:
            initialize_learning_lists(key)
        if comparison_plots:
            initialize_performance_lists(key)
        env.reset(max(network_load), False)
        rewarddict[key]['agent'] = QAgent(env.dynetwork)
        learn(key)
        rewarddict[key]['agent'].config['epsilon'] = 0.0001
        rewarddict[key]['agent'].config['decay_rate'] = 1
        test(key)

script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'rewardplots/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)
learn_results_dir = os.path.join(script_dir, 'rewardplots/learnRes/')
if not os.path.isdir(learn_results_dir):
    os.makedirs(learn_results_dir)

x = np.repeat(network_load, trials)
def compare_deliv(reward, color):
    print(reward+": "+str(np.around(np.array(rewarddict[reward]['avg_deliv']), 3)))
    plt.scatter(x, rewarddict[reward]['avg_deliv'], c=color_list[color], label=reward)
def compare_max(reward, color):
    print(reward+": "+str(rewarddict[reward]['maxNumPkts']))
    plt.scatter(x, rewarddict[reward]['maxNumPkts'], c=color_list[color], label=reward)
def compare_avg(reward, color):
    print(reward+": "+str(np.around(np.array(rewarddict[reward]['avg_q_len']), 3)))
    plt.scatter(x, rewarddict[reward]['avg_q_len'], c=color_list[color], label=reward)
def compare_capacity(reward, color):
    print(reward+": "+str(np.around(np.array(rewarddict[reward]['avg_perc_at_capacity']), 3)))
    plt.scatter(x, rewarddict[reward]['avg_perc_at_capacity'], c=color_list[color], label=reward)
def compare_idle(reward, color):
    print(reward+": "+str(rewarddict[reward]['rejectionNums']))
    plt.scatter(x, rewarddict[reward]['rejectionNums'], c=color_list[color], label=reward)
def compare_empty(reward, color):
    print(reward+": "+str(np.around(np.array(rewarddict[reward]['avg_perc_empty_nodes']), 3)))
    plt.scatter(x, rewarddict[reward]['avg_perc_empty_nodes'], c=color_list[color], label=reward)

if comparison_plots:
    plt.title("Average Delivery Time vs Network Load")
    plt.clf()
    print("Average Delivery Time")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_deliv(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.legend()
    plt.savefig(results_dir + "avg_deliv.png")
    plt.clf()

    plt.title("Maximum Num of Pkts Nodes Held vs Network Load")
    plt.clf()
    print("Max Queue Length")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_max(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Maximum Number of Packets Held')
    plt.legend()
    plt.savefig(results_dir + "maxNumPkts.png")
    plt.clf()

    plt.title("Average Num of Pkts Nodes Held vs Network Load")
    plt.clf()
    print("Max Num Packets")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_avg(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Average Number of Packets Held')
    plt.legend()
    plt.savefig(results_dir + "avg_q_len.png")
    plt.clf()

    plt.title("Percent of Working Nodes at Capacity vs Network Load")
    plt.clf()
    print("Percent of Nodes at Capacity")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_capacity(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Percentage of Working Nodes at Capacity')
    plt.legend()
    plt.savefig(results_dir + "avg_perc_at_capacity.png")
    plt.clf()

    plt.title("Average Packet Idle Time vs Network Load")
    plt.clf()
    print("Average Packet Idle Time")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_idle(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Time Steps Spent Idle')
    plt.legend()
    plt.savefig(results_dir + "rejectionNums.png")
    plt.clf()

    plt.title("Percent of Empty Nodes vs Network Load")
    plt.clf()
    print("Percent of Empty Nodes")
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_empty(key, i)
    plt.xlabel('Number of packets')
    plt.ylabel('Percentage of Nodes Empty')
    plt.legend()
    plt.savefig(results_dir + "avg_perc_empty.png")
    plt.clf()

y = list(range(1, numEpisode + 1))
def compare_deliv_l(reward, color):
    plt.scatter(y, rewarddict[reward]['avg_deliv_learning'], c=color_list[color], label=reward)
def compare_max_l(reward, color):
    plt.scatter(y, rewarddict[reward]['maxNumPkts_learning'], c=color_list[color], label=reward)
def compare_avg_l(reward, color):
    plt.scatter(y, rewarddict[reward]['avg_q_len_learning'], c=color_list[color], label=reward)
def compare_capacity_l(reward, color):
    plt.scatter(y, rewarddict[reward]['avg_perc_at_capacity_learning'], c=color_list[color], label=reward)
def compare_idle_l(reward, color):
    plt.scatter(y, rewarddict[reward]['rejectionNums_learning'], c=color_list[color], label=reward)
def compare_empty_l(reward, color):
    plt.scatter(y, rewarddict[reward]['avg_perc_empty_nodes_learning'], c=color_list[color], label=reward)

if learning_plot:
    plt.title("Average Delivery Time Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_deliv_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Avg Delivery Time (in steps)')
    plt.legend()
    plt.savefig(learn_results_dir + "avg_deliv_learning.png")
    plt.clf()

    plt.title("Maximum Num of Pkts Nodes Held Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_max_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Maximum Number of Packets Held')
    plt.legend()
    plt.savefig(learn_results_dir + "maxNumPkts_learning.png")
    plt.clf()

    plt.title("Average Num of Pkts Nodes Held Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_avg_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Average Number of Packets Held')
    plt.legend()
    plt.savefig(learn_results_dir + "avg_q_len_learning.png")
    plt.clf()

    plt.title("Percent of Working Nodes at Capacity Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_capacity_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Percentage of Working Nodes at Capacity')
    plt.legend()
    plt.savefig(learn_results_dir + "avg_perc_at_capacity_learning.png")
    plt.clf()

    plt.title("Average Packet Idle Time Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_idle_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Time Steps Spent Idle')
    plt.legend()
    plt.savefig(learn_results_dir + "rejectionNums_learning.png")
    plt.clf()

    plt.title("Percent of Empty Nodes Per Episode")
    plt.clf()
    for i in range(len(reward_list)):
        if reward_list[i]:
            key = 'reward'+str(i+1)
            compare_empty_l(key, i)
    plt.xlabel('Episode')
    plt.ylabel('Percentage of Nodes Empty')
    plt.legend()
    plt.savefig(learn_results_dir + "avg_perc_empty_learning.png")
    plt.clf()