import gym
import numpy as np
from gym import spaces, envs
from one_time_env import dynetworkEnv
from our_agent import QAgent

def main():
    # Initialize with zeros so that plot starts at the origin
    step = [0]
    deliveries = [0]
    time_steps = 10
    num_sims = 5
    env = dynetworkEnv()
    agent = QAgent(env.dynetwork)
    #pEdge = UpdateEdges()
    plot_opt = True
    
    for i in range(num_sims):
        for i in range(1, time_steps):
            if deliveries 
            if i % 100 == 0:
                f = open("q-learning/dict.txt","w")
                f.write(str(agent.q))
                f.close()
                print("Currently at time step ", i)
            env.change_network()
            env.purgatory()
            env.update_queues()
            env.update_time()
            #this will iterate through every packet, throughout all nodes and make them 'step ahead'
            router(env, agent) #do we ever use router?
                
            # Draw the current slice
            #node_queues = nx.get_node_attributes(self._dynetwork._network, 'sending_queue')
            if plot_opt:
                env.render(i)
    
            # Generate data for graph of cumulative deliveries
            step.append(i)
            deliveries.append(env.dynetwork._deliveries)
        env.reset()
        
        


def router(env, agent):

    temp_node_queue_lens = [0]
    temp_num_node_at_capacity = 0
    temp_num_nonEmpty_node = 0
    
    # iterate all nodes
    for nodeIdx in env.dynetwork._network.nodes:
        node = env.dynetwork._network.nodes[nodeIdx]
        # provides pointer for queue of current node
        env.curr_queue = node['sending_queue']
        sending_capacity = node['max_send_capacity']
        queue_size = len(env.curr_queue)

        # Congestion Measure #1: max queue len
        if(queue_size > env.dynetwork._max_queue_length):
            env._max_queue_length = queue_size

        # Congestion Measure #2: avg queue len pt1
        if(queue_size > 0):

            temp_node_queue_lens.append(queue_size)
            temp_num_nonEmpty_node += 1
            # Congestion Measure #3: avg percent at capacity
            if(queue_size > sending_capacity):
                # increment number of nodes that are at capacity
                temp_num_node_at_capacity += 1

        # stores packets which currently have no destination path
        remaining = []
        sendctr = 0
        for i in range(queue_size):
            # when node cannot send anymore packets break and move to next node
            if sendctr == sending_capacity:
                env.dynetwork.rejections +=(1*(len(node['sending_queue'])))
                break
            env.packet = env.curr_queue[0]
            #pkt = env.dynetwork._packets.packetList[env.packet]
            pkt_state = env.get_state(env.packet)
            neighbor = list(env.dynetwork._network.neighbors(pkt_state[0]))
            action = agent.act(pkt_state, neighbor)
            reward, remaining, curr_queue, action = env.step(action, pkt_state[0])
            if reward != None:
                sendctr += 1
            agent.learn(pkt_state, reward, action)

        node['sending_queue'] = remaining + node['sending_queue']

    # Congestion Measure #2: avg queue len pt2
    if len(temp_node_queue_lens) > 1:
        env.dynetwork._avg_q_len_arr.append(
            np.average(temp_node_queue_lens[1:]))

    # Congestion Measure #3: percent node at capacity
    env.dynetwork._num_capacity_node.append(temp_num_node_at_capacity)

    env.dynetwork._num_working_node.append(temp_num_nonEmpty_node)

if __name__ == '__main__':
    main()