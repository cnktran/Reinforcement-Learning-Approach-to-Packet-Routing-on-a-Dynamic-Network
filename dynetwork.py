import networkx as nx
import dynetx as dn
import matplotlib.pyplot as plt
import time
import random
import numpy as np 
import Packet 


#Note that this is a measure of edges per added node, not total number of edges
fixed_positions = nx.spring_layout(G)
class DynamicNetwork:
	def __init__(self, network, packets, rejections = 0):
        self._network = network
        self._packets = packets
        self._rejections = rejections

# Method declaration
	def randomGeneratePackets(self, num_packets):
    	tempList = []
    	for i in range(num_packets):
        	# random node initialization
        	startNode = self.nodes(randint(0, len(self._network)))
        	endNode = self.nodes(randint(0, len(self._network)))
            
            # if the node is full then assign to another
            while(startNode['current_queue'].length() == startNode['max_capacity']){
              startNode = self.nodes(randint(0, len(self._network)))
            }
			
            # distinct starting and ending node
        	while (startNode == endNode):
            	endNode = self.nodes(randint(0, len(self._network)))
            
        	# give weight 0 in the begining		
        	curPack = Packet(startNode, endNode, startNode, 0)

        	tempList.append(curPack)

    	# create Packets Object
    	packetsObj = Packets(tempList)

    	# Assign Packets Object to the network
    	self._network._packets = packetsObj

        
#-----------Below can be in the main funciton----------------------
node_count = 100
edge_count = 50
max_capacity = 5
time_steps = 10
edge_removal_min = 0
edge_removal_max = 10
num_packets = 100

#Initialize a Network using Networkx
G = nx.barabasi_albert_graph(node_count, edge_count)
nx.set_node_attributes(G, max_capacity, 'max_capacity')
nx.set_node_attributes(G, np.repeat(-1,max_capacity), 'current_queue')

#store in DynamicNetwork class
G = DynamicNetwork(G, None)
G.randomGeneratePackets(num_packets)

#store packet index from Packets list
for i in range(num_packets):
	temp = np.repeat(-1, G._network.nodes[G._packets[i].startPos]['max capacity'])
	pos = (G._network.nodes[G._packets[i].startPos]['current_queue'] == temp)
	G._network.nodes[G._packets[i].startPos]['current_queue'][pos][0] = i 

del temp
del pos

# Dynamic Edge Change
#use G.edges() to obtain a list of all edges
#use G.neighbors(n) to obtain neighbors of node n 

r = Router()
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
    
    for pkt in G._packets:
      r.dijkstra_router(G._network, pkt)

      
      
      