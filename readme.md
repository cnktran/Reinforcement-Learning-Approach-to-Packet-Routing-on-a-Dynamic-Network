# Dynamic Routing

## Project Description:
In order to test the performance of various routing algorithms on a dynamic network, we create a packet routing simulation on a network that updates discretely over a series of time steps.

Throughout one episode of the simulation, edges are randomly chosen to disappear and be restored at each time step. In addition, edge weights fluctuate in a sinusoidal manner throughout the episode. At the beginning of each episode, a number of packets (the network load) is generated on the network, each with a random start and destination node. Every time a packet is delivered, a new one is initialized some number of time steps later. Once a set number of packets have been generated and delivered on the network, the episode ends. Average packet delivery time and various measures of network congestion are then calculated.

The simulation calls upon a router to determine paths for each packet according to one routing algorithm. For this project in particular, we explore shortest path via Dijkstra's algorithm, shortest path via Floyd-Warshall's algorithm, Q-learning via various reward functions, and Deep Q Learning. 


## Requirements:
- NetworkX
- FFmpeg (for animating)
- Matplotlib
- OpenAI Gym
- PyTorch

---
## Shortest Path & Q-Learning
Contains routing using Q-Learning, implemented in a Gym environment. Contains the option to also run Shortest Path (either Dijkstra or Floyd-Warshall) on the same network for comparison purposes.

### Files
- dynetwork.py
- our_agent.py
- our_env.py
- Packet.py
- QLSimulationWithSP.py
- rewardsComparison.py
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
- QLSimulationWithSP.py
    -Teaches an agent based on the max in a list of network loads for a fixed number of episodes. Then routes solely based on the Q-table and outputs measures of delivery time and congestion. Contains options for comparing to Shortest Path.
- rewardsComparison.py
    - Serves the same function as QLSimulationWithSP.py, but used to compare Q-learning for various reward functions instead of one Q-learning algorithm and Shortest Path. 
- UpdateEdges.py
    - Contains functions for dynamic edge change.

### Usage
- Open our_env.py and change network properties at the top. The default is a 50-node network of average degree 3, queue size 150, max transmit 10, with 5000 packets to start and 5000 additional packets to delivery before the episode terminates.
- Open QLSimulationWithSP.py and specify 'numEpisode' for how many episodes the agent should learn. Specify an array of network loads that you would like to test, and whether the program should also run shortest path.
- To adjust learning rates, open our_agent.py to specify setup at the top of the file. The default is
- Run QLSimulationWithSP.py in python3.

---
## Deep Q-Learning
Contains routing using Deep Q-Learning, using PyTorch package.

### Files
- DeepQSimulation.py
- dynetwork.py
- our_agent.py
- our_env.py
- Packet.py
- UpdateEdges.py
- DQN.py
- neural_network.py
- replay_memory.py
- Setting.json

### Additional File Descriptions
- DQN.py
    - Specifies hidden layer and activation functions
- neural_network.py
    - Create instance of neural networks which contains DQN instances, specify memory size, policy and target networks, and optimizer.
- replay_memory.py
    - contain methods for creating reply_memory instance, pushing and pulling experiences.
- Setting.json
    - contain all the settings for network, parameters for deep Q-learning, agent and setup for simulation.
- DeepQSimulation.py
    -Teaches an agent based on the max in a list of network loads for a fixed number of episodes. Then routes using deep Q-learning algorithms. Outputs measures of delivery time and congestion. Contains options for comparing to Shortest Path.

### Usage
- Open Setting.json and specify desired settings
- Open DeepQSimulation.py and run the program in python 3

## Parameter Discussion

### General Parameters (in Shortest Path/in Q-Learning)
#### In our_env.py
- nnodes : Number of nodes on the network.
- nedges : Number of edges on the network. For barabasi-albert (see network_type), specify **edges per node**. For erdos-renyi, specify **total number of edges desired**.
- max_queue : Number of packets a node can hold at any given time step.
- max_transmit : Number of packets a node can send per time step.
- npackets : The number of packets to generate on the network at the start of the episode.
- max_initializations : Number of packets to generate and deliver on the network before the episode is complete.
- max_edge_weight : When initializing edge weights, a weight is randomly selected from [0, max_edge_weight].
- min_edge_removal : The minimum number of edges that is removed from the network per time step.
- max_edge_removal : The maximum number of edges that is removed from the network per time step.
- edge_change_type : Off, sinusoidal, or random walk.
- network_type : Currently we can generate two types of random networks. One uses the Barabasi-Albert construction, which creates a center node and adds nodes branch outwards. This produces a well-connected graph with a "center" of high degree. This is representative of Internet networks, and is prone to high congestion at its center. The other network uses the Erdos-Renyi construction, which is random with a relatively consistent degree across all nodes. This is less representative of Internet networks and can generate "isolates" which are unconnected to the rest of the network.
- router_type : Algorithm used to determine packet path when routing using shortest path. Current options are Shortest Path via Dijkstra's Algorithm or Shortest Path via Floyd-Warshall Algorithm.

#### In DeepQSimulation.py
- numEpisode : Number of episodes spent learning. For a decay rate of 0.999, around 60 episodes is sufficient.
- time_steps : Maximum length of simulation.
- rewardfunction : string that specifies which reward function to use (defined in our_env.py)
- learning_plot : Boolean. If True, saves plots for delivery/congestion performance during learning process.
- comparison_plots : Boolean. If True, saves plots for tests done for each network load.
- trials : Number of times to test per item in network_load.
- show_example_comparison : Boolean. Saves animation of a sample packet path at each network load when testing. Discouraged for large networks.
- sp : Boolean. Toggle Shortest Path routing on or off when testing.
- network_load : Vary starting number of packets on the network. Given as a list of network loads for testing.

### DQN Parameters
- DQN
	- take_queue_size_as_input : Boolean, if true, neural network will take queue_size of the node as additional input for neural network
	- memory_bank_size : number of experiences being kept in memory reply
	- memory_batch_size : number of experiences being pulled from memory reply
	- optimizer_learning_rate: step size used to minimize loss function
	- optimizer_per_episode : Boolean, if true, will call optimizer every time step, if false, will call optimizer after route one packet
- AGENT
	- epsilon : probability of doing explore (random walk) ie. not exploit (use Q-value)
	- decay_epsilon_rate : factor to discount epsilon 
	- gamma_for_next_q_val : discount factor for Q-values
	- use_random_sample_memory: one of three ways of pulling experiences from memory reply (random sample)
	- use_most_recent_sample_memory: one of three ways of pulling experiences from memory reply (most recent sample)
	- use_priority_memory: one of three ways of pulling experiences from memory reply (prioritized sample)\
-SIMULATION 
	- training_episodes : number of episodes for training the neural network,
	- max_allowed_time_step_per_episode : max time steps allowed for each per episode,
	- num_time_step_to_update_target_network : how often do we update target network,
	- test_network_load_min : minimum network load to test,
	- test_network_load_max : maximum network load to test,
	- test_network_load_step_size : step size between minimum network load to maximum network load,
	- test_trials_per_load : number of trials for one network load,
	- learning_plot : Boolean, if true print performance measure plots for learning plots,
	- test_diff_network_load_plot : Boolean, if true print performance measure plots for tests,
	- plot_routing_network : Boolean, if true, save screen shots of network during the routing

