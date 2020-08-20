from collections import namedtuple
import numpy as np
import random
import networkx as nx
import DQN
import torch
import math
import json
import torch.nn.functional as F
import os

'''Open file Setting.json which contains learning parameters. '''
#main_dir = os.path.dirname(os.path.realpath(__file__))
#main_dir = main_dir + '/'
with open('Setting.json') as f:
    setting = json.load(f)


Experience = namedtuple(
    'Experience',
    ('state', 'action', 'next_state', 'reward')
)


'''
    The agent file defines a learning agent and its hyperparameters
    File contains functions:
        generate_q_table: initialize Q-table
        act: returns which next node to send packet to
        learn: update Q-table after receiving corresponding rewards

'''


class QAgent(object):
    """

        Initialize an instance of the agent class
        learning rate: The amount of information that we wish to update our equation with, should be within (0,1]
        epsilon: probability that packets move randomly, instead of referencing routing policy
        discount: Degree to which we wish to maximize future rewards, value between (0,1)
        decay_rate: decays epsilon
        update_epsilon: utilized in our_env.router, only allows epsilon to decay once per time-step
        self.q: stores q-values
        *_memory: different methods of sampling from our memory bank

    """

    def __init__(self, dynetwork):
        self.config = {
            "nodes": dynetwork.num_nodes,
            "epsilon": setting['AGENT']['epsilon'],
            "decay_rate": setting['AGENT']['decay_epsilon_rate'],
            "batch_size": setting['DQN']['memory_batch_size'],
            "gamma": setting['AGENT']['gamma_for_next_q_val'],

            "update_less": setting['DQN']['optimize_per_episode'],
            "sample_memory": setting['AGENT']['use_random_sample_memory'],
            "recent_memory": setting['AGENT']['use_most_recent_memory'],
            "priority_memory": setting['AGENT']['use_priority_memory'],

            "update_epsilon": False,
            "update_models": torch.zeros([1, dynetwork.num_nodes], dtype=torch.bool),
            "entered": 0,
        }
        self.adjacency = dynetwork.adjacency_matrix
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")

    """

    act is a function that gives a packet the next best action (if possible)
        learning rate: The amount of information that we wish to update our equation with, should be within (0,1]
        epsilon: probability that packets move randomly, instead of referencing routing policy
        discount: Degree to which we wish to maximize future rewards, value between (0,1)
        decay_rate: decays epsilon
        update_epsilon: utilized in our_env.router, only allows epsilon to decay once per time-step
        self.q: stores q-values
        *_memory: different methods of sampling from our memory bank

    """

    def act(self, neural_network, state, neighbor):
        ''' We will either random walk or reference Q-table with probability epsilon '''
        if random.uniform(0, 1) < self.config['epsilon']:
            ''' We will either random walk or reference Q-table with probability epsilon '''
            if not bool(neighbor):
                # checks if the packet's current node has any available neighbors
                return None
            else:
                next_step = random.choice(neighbor)  # Explore action space
        else:
            if not bool(neighbor):
                return None
            else:
                ''' obtains the next best neighbor to move the packet from its current node by referencing our neural network '''
                with torch.no_grad():
                    qvals = neural_network.policy_net(
                        state.float())
                    next_step_idx = qvals[:, neighbor].argmax().item()
                    next_step = neighbor[next_step_idx]
                    if self.config['update_epsilon']:
                        self.config['epsilon'] = self.config["decay_rate"] * \
                            self.config['epsilon']
                        self.config['update_epsilon'] = False
        return next_step

    '''
        Updates replay memory with current experience
        and takes sample of previous experience
    '''

    def learn(self, nn, current_event, action, reward, next_state):
        ''' skip if no valid action or no reward is provided '''
        if (action == None) or (reward == None):
            pass
        else:
            if current_event != None:
                nn.replay_memory.push(
                    current_event, action, next_state, reward)

            ''' check if our memory bank has sufficient memories to sample from '''
            if (self.config["update_models"][:, nn.ID]) & (nn.replay_memory.can_provide_sample(self.config['batch_size'])):

                '''check which type of memories to pull'''
                if self.config['sample_memory']:
                    experiences = nn.replay_memory.sample(
                        self.config['batch_size'])

                elif self.config['recent_memory']:
                    experiences = nn.replay_memory.take_recent(
                        self.config['batch_size'])

                elif self.config['priority_memory']:
                    experiences, experiences_idx = nn.replay_memory.take_priority(
                        self.config['batch_size'])

                states, actions, next_states, rewards = self.extract_tensors(
                    experiences)
                '''extract values from experiences'''
                current_q_values = self.get_current_QVal(
                    nn.policy_net, states, actions)

                next_q_values = self.get_next_QVal(
                    nn.target_net, next_states, actions, nn.ID)

                target_q_values = (
                    next_q_values * self.config['gamma']) + rewards

                '''update priority memory's probability'''
                if self.config['priority_memory']:
                    nn.replay_memory.update_priorities(
                        experiences_idx, current_q_values, torch.transpose(target_q_values, 0, 1))

                '''backpropagation to update neural network'''
                loss = F.mse_loss(current_q_values,
                                  torch.transpose(target_q_values, 0, 1))
                nn.optimizer.zero_grad()
                loss.backward()
                nn.optimizer.step()

    ''' helper function to extract values from our stored experiences'''

    def extract_tensors(self, experiences):
        states = torch.cat(tuple(exps[0] for exps in experiences))
        actions = torch.cat(
            tuple(torch.tensor([exps[1]]) for exps in experiences))
        next_states = torch.cat(tuple(exps[2] for exps in experiences))
        rewards = torch.cat(
            tuple(torch.tensor([exps[3]]) for exps in experiences))
        return (states, actions, next_states, rewards)

    ''' helper function to obtain the Q-val of current state'''

    def get_current_QVal(self, policy_net, states, actions):
        return policy_net(states.float()).gather(dim=1, index=actions.unsqueeze(-1))

    ''' helper function to obtain the Q-val of the next state'''

    def get_next_QVal(self, target_net, next_states, actions, destination):
        ''' need to apply neighbors mask to target_net() prior to taking the maximum '''
        non_terminal_idx = (actions != destination)

        temp1 = target_net(next_states.float())

        ''' initialize zero value vectors '''
        batch_size = next_states.shape[0]
        values = torch.zeros(batch_size).view(1, -1).to(self.device)

        ''' update non-terminal state with Q value '''
        for idx in range(values.size()[1]):
            if non_terminal_idx[idx]:
                adjs = self.adjacency[actions[idx]][0]
                adjs = (adjs == 1)
                temp2 = temp1[idx, :].view(1, -1)
                values[0, idx] = torch.max(temp2[adjs]).detach()

        return values
