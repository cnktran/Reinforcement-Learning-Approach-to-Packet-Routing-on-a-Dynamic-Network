# Dynamic Routing

## Project Description:
To test various packet routing algorithms on a dynamic network, we create a simulation of a network with random edge change (on/off and weights) and create a router that determines paths for each packet. The router then conduct Q-learning and uses Q-table to route packets.

## Requirements:
- NetworkX
- FFmpeg
- Matplotlib

## Files:
-

## File Descriptions:
- Animator.py
	used to generate screenshots for each time stamp
- dynetwork.py
	used to set up network features. Called by main class
- Packet.py
	file to define packet class
- our_agent.py
    used to create agent instance and adjust agent learning policy
- our_env.py
    used to create Q-learning environment and set up network
- Q_Routing.py
    used to simulate Q-learning based on our_env.py and produce statsitics for learning process
- Q_Routing_NLs.py
    used to simulate Q-learning based on our_env.py and produce statsitics for post-learning process on different network load


- one_time_env.py
	used to create Q-learning environment for one-round of learning (used for debuging purposes)
- one_time_learning.py
	used to run Q-learning based on environment from one_time_env (used for debuging purposes)
---

## Usage:
- To perform Q-learning and observe learning results. Open Q_Routing.py and specify 'numEpisode' being number of times you wish the program to learn
Then specify 'time_steps' being the maximum time stamps for router to finish route all packets

To change the network setup, open our_env.py to specify setup.

To adjust learning rates, open our_agent.py to specify setup.

- To perform Q-learning and observe learning results and observe performance on different network loads. Open Q_Routing_NLs.py (Network Loads). Specify 'numEpisode' being number of times you wish the program to learn. Then specify 'time_steps' being the maximum time stamps for router to finish route all packets. Then specify network load to perform simulation.

-More instructions will be updating soon...
### Parameter Discussion
- node_count : Number of nodes on the network.
- edge_count : Number of edges on the network. For barabasi-albert (see network_type), specify **edges per node**. For erdos-renyi, specify **total number of edges desired**.
- max_transmit : Number of packets a node can send per time step.
- max_queue : Number of packets a node can hold at any given time step.
- time_steps : Length of simulation. In Statistics.py, this information is stored in list for in network_load.
- edge_removal_min : The minimum number of edges that is removed from the network per time step.
- edge_removal_max : The maximum number of edges that is removed from the network per time step.
- network_type : Currently we can generate two types of random networks. One uses the Barabasi-Albert construction, which creates a center node and adds nodes branch outwards. This produces a well-connected graph with a "center" of high degree. This is representative of Internet networks, and is prone to high congestion at its center. The other network uses the Erdos-Renyi construction, which is random with a relatively consistent degree across all nodes. This is less representative of Internet networks and can generate "isolates" which are unconnected to the rest of the network.
- router_type : Routing algorithm used to determine packet path. Current options are Shortest Path via Dijkstra's Algorithm, Shortest Path via Floyd-Warshall Algorithm, and Reinforcement Learning via Q-Learning.
- plot_opt : Produce graphs and an animation of the simulation. Works well for individual simulations of time_steps less than or equal to 100. Otherwise leave False or run at your own risk.
#### Parameters in Statistics.py
- calculate_delivery_time : Print data and produce plot for average number of time steps for delivery across the given network loads.
- calculate_congestion_max_q_len : Print data and produce plot for the max queue size of the most congested node in the simulation across the given network loads.
- calculate_congestion_avg_q_len : Print data and produce plot for the average queue size of the nodes during the simulation across the given network loads.
- calculate_congestion_perc_at_capacity : Print data and produce plots for the percentage of nodes that operate at full holding capacity across the given network loads.
- network_load : See time_steps.