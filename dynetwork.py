import networkx as nx
import dynetx as dn
import matplotlib.pyplot as plt
import time
import random
import numpy as np

node_count = 50
edge_count = 5
max_capacity = 5
time_steps = 10
edge_removal_min = 0
edge_removal_max = 10

#Initialize a Network
G = nx.barabasi_albert_graph(node_count, edge_count)
fixed_positions = nx.spring_layout(G)
nx.set_node_attributes(G, 0, 'current_queue')
nx.set_node_attributes(G, max_capacity, 'max_queue')

# Dynamic Edge Change
#use G.edges() to obtain a list of all edges
#use G.neighbors(n) to obtain neighbors of node n 

stripped_list = []
for i in range(1, time_steps): 
	#delete some edges
	edges = G.edges()
	deletion_number = random.randint(edge_removal_min, min(edge_removal_max, len(edges) - 1))  
	strip = random.sample(edges, k = deletion_number)
	G.remove_edges_from(strip)
	stripped_list.extend(strip)
	#restore some deleted edges
	restore_number = random.randint(0, len(stripped_list) - 1)
	restore = random.choices(stripped_list, k = restore_number)
	G.add_edges_from(restore)
	nx.draw(G, pos=fixed_positions, with_labels=True, font_weight='bold')
	plt.savefig("network_images/dynet" + str(i) + ".png")
	plt.clf()