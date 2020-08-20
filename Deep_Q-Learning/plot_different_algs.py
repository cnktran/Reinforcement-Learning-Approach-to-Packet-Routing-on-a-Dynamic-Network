import numpy as np
import matplotlib.pyplot as plt
import os

'''Run this file to create plots with shortest path, q-learning, deep Q-learning 
all on one graph for each of the graphs of our metrics. Note the network loads 
and number of trials must be the same for both tests.'''

#change this based on the parameters used for your test 
network_load = np.arange(500, 7500, 500) 
trials = 5

files_headers = ['sp_', 'ql_', 'dqn_']
colors = ['orange', 'blue', 'lime']
labels = ['Shortest Path', 'Q-learning', 'Deep Q-Learning']

rest_of_file_name = ['avg_deliv', 'avg_perc_at_capacity', 'avg_perc_empty_nodes', 'rejectionNums']
titles = ["Average Delivery Time vs Network Load", "Percent of Working Nodes at Capacity vs Network Load", "Percent of Empty Nodes vs Network Load", "Average Packet Idle Time vs Network Load", "Average Packet Queue Length per Node vs Network Load"
          "Percent of Working Nodes at Capacity Per Episode"]
ylabels = ['Avg Delivery Time (in steps)', 'Percent of Working Nodes at Capacity', 'Percent of Empty Nodes', 'Packet Idle Time (in steps)', 'Average Number of Packets being hold by a Node']

'''Make folder plots_mult to store plots in if it doesn't already exist'''
script_dir = os.path.dirname(__file__)
results_dir = os.path.join(script_dir, 'plots_mult/')
if not os.path.isdir(results_dir):
    os.makedirs(results_dir)

'''Extract data and create plots'''
for rest_idx in range(len(rest_of_file_name)):
    plt.clf()
    plt.title(titles[rest_idx])
    plt.xlabel('Number of packets')
    plt.ylabel(ylabels[rest_idx])
    rest = rest_of_file_name[rest_idx]
    for header_idk in range(len(files_headers)):
        header = files_headers[header_idk]
        my_file = header + rest
        ys = np.load(script_dir+ '/' + my_file + '.npy')
        plt.scatter(np.repeat(network_load, trials), ys, c = colors[header_idk], label = labels[header_idk])

    plt.legend()
    plt.savefig(results_dir + rest + ".png")
