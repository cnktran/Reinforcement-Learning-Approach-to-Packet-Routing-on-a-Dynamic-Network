# Dynamic Routing

## Project Description:
To test various packet routing algorithms on a dynamic network, we create a simulation of a network with random edge change (on/off and weights) and create a router that determines paths for each packet. We generate a given number of packets at the beginning of one episode and allow the simulation to run a number of time steps before measuring packet delivery time and level of network congestion.

## Requirements:
- NetworkX
- FFmpeg
- Matplotlib

## Files:
- Animator.py
- dynetwork.py
- router.py
- Simulator.py
- Stat_Simulator.py
- Statistics.py

## File Descriptions:
- Animator.py
    - Takes images in directory network_images and creates animation.mp4. Edit here for animation details (fps, size, etc.)
- dynetwork.py
    - Defines network object which contains information on the packets, deliveries, and rejections.
- Packet.py
    - Defines packet object.
- router.py
    - Determines next step taken by each packet on the network. Contains various routing algorithms, including Dijkstra, Floyd-Warshall, and Q-learning.
- Simulator.py
    - Contains main function and performs simulation over given number of time steps. Outputs average delivery time.
- Stat_Simulator.py
    - Version of Simulator.py to be used with Statistics.py.
- Statistics.py
    - Runs simulation multiple times to view effects of changing network load on delivery time and congestion.

---

## Usage:
- To perform individual simulations, open Simulator.py and edit parameters at the bottom of the file before running.
- To perform a meta-simulation across multiple network loads, open Statistics.py and edit parameters at the top of the file before running. Make sure to set plot_opt = False. You can determine which network loads you want to test by changing the values in the list network_load = [1000, 3000, 5000, 7000, 9000]. You can plot results in terms of average delivery time, average queue size, and maximum queue size.
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