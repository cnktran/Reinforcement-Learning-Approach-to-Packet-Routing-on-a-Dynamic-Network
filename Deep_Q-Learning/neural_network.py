from DQN import DQN
from replay_memory import ReplayMemory
import torch
import torch.nn as nn
import torch.optim as optim
import json
import os 

'''Open file Setting.json which contains learning parameters. '''
main_dir = os.path.dirname(os.path.realpath(__file__))
main_dir = main_dir + '/'
with open(main_dir + 'Setting.json') as f:
    setting = json.load(f)


    ''' 
    This class contains the policy and target neural network for a certain destination node deep Q-learning.
    node_number: this is the ID associated with each network, since each neural network is associated with some destination node 
    network_size: this is the number of nodes in our network, gives us part of the size of our hidden layer
    num_extra: the number of extra parameters we will be supplying in our network (network_size + num_extra = hidden layer size)
    capacity: the maximum memories that our neural network can sample from 

    '''
class NeuralNetwork(object):

    def __init__(self, node_number, network_size, num_extra, capacity=setting['DQN']['memory_bank_size']):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        learning_rate = setting['DQN']['optimizer_learning_rate']
        self.ID = node_number
        self.policy_net = DQN(network_size, num_extra).to(self.device)
        self.target_net = DQN(network_size, num_extra).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.replay_memory = ReplayMemory(capacity)
        self.optimizer = optim.SGD(
            params=self.policy_net.parameters(), lr=learning_rate)
