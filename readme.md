# Dynamic Routing

## Project Description:
To test various packet routing algorithms on a dynamic network, we create a simulation dynamic network simulation that calls upon a router to determines paths for each packet according to one routing algorithm. For this project in particular, we explore shortest path via Dijkstra's algorithm, shortest path via Floyd-Warshall's algorithm, Q-learning, and Deep Q Learning. 

In one episode of the simulation, edges are randomly chosen to disappear and be restored at every time step. Furthermore, edge weights fluctuate mimicking a sinusoid. At the beginning of the episode, a number of packets (the network load) is generated on the network with a random start and destination node. Throughout the episode, every time a packet is delivered, a new one is initalized a number of time steps later. When a set number of packets have been generated and delivered, the episode ends and packet delivery time as well as network congestion is measured.

## Requirements:
- NetworkX
- FFmpeg (for animating)
- Matplotlib

## Version Shortest Path
Contains routing using shortest path via both Dijkstra and Floyd-Warshall.

### Files:
- Animator.py
- dynetwork.py
- router.py
- Packet.py
- Simulator.py
- Stat_Simulator.py
- Statistics.py
- UpdateEdges.py

### File Descriptions:
- Animator.py
    - Takes images in directory network_images and creates animation.mp4. Edit here for animation details (fps, size, etc.)
- dynetwork.py
    - Defines network object which contains information on the packets, deliveries, and rejections.
- Packet.py
    - Defines packet object.
- router.py
    - Determines next step taken by each packet on the network. Calls Dijkstra/Floyd-Warshall.
- Simulator.py
    - Contains main function and performs simulation over given number of time steps. Outputs average delivery time.
- Stat_Simulator.py
    - Version of Simulator.py to be used with Statistics.py.
- Statistics.py
    - Runs simulation multiple times to view effects of changing network load on delivery time and congestion.
- UpdateEdges.py
    - Contains functions for dynamic edge change.

### Usage:
- To perform individual simulations, open Simulator.py and edit parameters at the bottom of the file before running.
- To perform a meta-simulation across multiple network loads, open Statistics.py and edit parameters at the top of the file before running. Make sure to set plot_opt = False. You can determine which network loads you want to test by changing the values in the list network_load = [1000, 3000, 5000, 7000, 9000]. You can plot results in terms of average delivery time, average queue size, and maximum queue size.

---

## Version Q-Learning
Contains routing using Q-Learning.

### Files
- dynetwork.py
- our_agent.py
- our_env.py
- Packet.py
- Q_Routing.py
- Q_Routing_NLs.py
- UpdateEdges.py

### File Descriptions:
- dynetwork.py
	- Defines network object which contains information on the packets, deliveries, and rejections.
- our_agent.py
    - Creates agent instance and stores/adjusts agent Q-table.
- our_env.py
    - Creates Q-learning environment and contains all functions for performing the simulation. Also contains all parameters relevant to network and the reward function.
- Packet.py
	- Defines packet object.
- Q_Routing.py
    - Simulates Q-learning based on our_env.py and produces statistics for learning process.
- Q_Routing_NLs.py
    - Simulates Q-learning based on our_env.py and produce statistics for routing based on a fixed Q-table after a set number of learning episodes. Used for comparison of performance to shortest path.
- UpdateEdges.py
    - Contains functions for dynamic edge change.
---

### Usage:
- To perform Q-learning and observe learning results. Open Q_Routing.py and specify 'numEpisode' being number of times you wish the program to learn
Then specify 'time_steps' being the maximum time steps for router to finish routing all packets.

- To change the network setup, open our_env.py to specify setup at the top of the file.

- To adjust learning rates, open our_agent.py to specify setup at the top of the file.

- To perform Q-learning and observe learning results and observe performance on different network loads. Open Q_Routing_NLs.py (Network Loads). Specify 'numEpisode' being number of times you wish the program to learn. Then specify 'time_steps' being the maximum time stamps for router to finish route all packets. Then specify network load list (e.g. np.arange(500, 5500, 500)) to perform simulation.

---
## Parameter Discussion

### General Parameters (in Shortest Path/in Q-Learning)
- node_count/nnodes : Number of nodes on the network.
- edge_count/nedges : Number of edges on the network. For barabasi-albert (see network_type), specify **edges per node**. For erdos-renyi, specify **total number of edges desired**.
- max_transmit : Number of packets a node can send per time step.
- max_queue : Number of packets a node can hold at any given time step.
- time_steps : Maximum length of simulation.
- max_edge_weight : When initializing edge weights, a weight is randomly selected from [0, max_edge_weight].
- edge_removal_min : The minimum number of edges that is removed from the network per time step.
- edge_removal_max : The maximum number of edges that is removed from the network per time step.
- edge_change_type : Off, sinusoidal, or random walk.
- network_type : Currently we can generate two types of random networks. One uses the Barabasi-Albert construction, which creates a center node and adds nodes branch outwards. This produces a well-connected graph with a "center" of high degree. This is representative of Internet networks, and is prone to high congestion at its center. The other network uses the Erdos-Renyi construction, which is random with a relatively consistent degree across all nodes. This is less representative of Internet networks and can generate "isolates" which are unconnected to the rest of the network.
- init_num_packets/npackets : For individual episodes (Simulator.py/Q_Routing.py), the number of packets to generate on the network.
- max_new_packets : Number of packets to generate and deliver on the network before the episode is complete.
- network_load : Vary starting number of packets on the network. Given as a list of network loads for testing.
- trials : Number of times to test per item in network_load.

### Shortest Path-Specific Parameters
- router_type : Routing algorithm used to determine packet path. Current options are Shortest Path via Dijkstra's Algorithm or Shortest Path via Floyd-Warshall Algorithm.
- plot_opt : Produce graphs and an animation of the simulation. Works well for individual simulations of time_steps less than or equal to 100. Otherwise leave False or run at your own risk.
- weight_type : Leave on 'delay' for packets to wait the weight of an edge before its next step. Otherwise, 'none' means packets will add the edge weight to their lifespan but not pause between traversal.
- calculate_delivery_time : Print data and produce plot for average number of time steps for delivery across the given network loads.
- calculate_congestion_max_q_len : Print data and produce plot for the max queue size of the most congested node in the simulation across the given network loads.
- calculate_congestion_avg_q_len : Print data and produce plot for the average queue size of the nodes during the simulation across the given network loads.
- calculate_congestion_perc_at_capacity : Print data and produce plots for the percentage of nodes that operate at full holding capacity across the given network loads.

### Q-Learning-Specific Parameters
- numEpisode : Number of episodes spent learning. For a decay rate of 0.999, around 60 episodes is sufficient.
- learning_plot : Boolean. If True, saves plots for tests done for each network load.
- comparison_plots : Boolean. If True, saves plots for delivery/congestion performance during learning process.