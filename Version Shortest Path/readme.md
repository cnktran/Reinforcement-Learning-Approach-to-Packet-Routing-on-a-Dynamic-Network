# Shortest Path Routing

## Project Description:
To test various packet routing algorithms on a dynamic network
We create a simulation of a network with following features (all optional)
- network model setting (nodes, edges, packet nums...)
- random edge change (on/off and weights)
- edge weight act as delays in packet routing
- congestion measures

We create a router that determines paths for each packet. The router then conduct shortest path to route packets.

## Requirements:
- NetworkX
- FFmpeg
- Matplotlib

## Files:
- Animator.py
	used to generate screenshots for each time stamp
- dynetwork.py
	used to set up network features. Called by main class
- Packet.py
	file to define packet class
- router.py
    used to perform routing. Called by main class
- Simulator.py
    used to perform one simulation (used for debugging purposes)
- Stat_Simulator.py
    used with Statistics.py and create instance to keep tract of simulation results
- Statistics.py
    used to start the simulations and specify network set up and simulation details

## Usage:
- To perform simulation, open Statistics.py and enter ideal network setups.
		If you do not wish to see the screenshots for each time stamp you can set plot_opt =False

- More detailed instructions will be updating soon...

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