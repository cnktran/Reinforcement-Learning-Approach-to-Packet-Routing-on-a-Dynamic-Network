import random
from collections import namedtuple
import math
import json
import os
from operator import itemgetter
import torch
import math
import json
import torch.nn.functional as F
import numpy as np

'''Open file Setting.json which contains learning parameters. '''
#main_dir = os.path.dirname(os.path.realpath(__file__))
#main_dir = main_dir + '/'
with open('Setting.json') as f:
    setting = json.load(f)


'''Tuple class created to contain elements for experiences'''

Experience = namedtuple(
    'Experience',
    ('state', 'action', 'next_state', 'reward')
)


'''
    The ReplayMemory file defines a memory bank which contains experiences.
    File contains functions:
        push: push experiences into the memory bank
        sample: returns which next node to send packet to
        take_recent: return most recent experiences
        take_priority: return experiences based on their priority probability
        __len__: return the length of experiences in the memory bank
        can_provide_sample: return a Boolean if able to provide experiences
        update_priorities: update priority probability for experiences
'''


class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0
        self.prob_weight = np.empty(0)
        self.temp_priorities_max = 1
        self.start_provide = 0
        self.epsil = 1 ** -2

    '''Turn *args into an Experience and put into self.memory.
    If self.memory is full then replace the element that has been 
    in self.memory the longest. '''

    def push(self, *args):
        if len(self.memory) < self.capacity:
            self.memory.append(Experience(*args))

            # update priority probs
            if self.__len__() >= self.capacity / 4:
                self.prob_weight = np.append(
                    self.prob_weight, max(self.prob_weight))
            else:
                self.prob_weight = np.append(
                    self.prob_weight, self.temp_priorities_max)
        else:
            self.position = (self.position + 1) % self.capacity
            self.memory[self.position] = Experience(*args)
            self.prob_weight[self.position] = max(self.prob_weight)

    '''Take a random sample of size batch_size from self.memory'''

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    '''Given size batch_size, take the batch_size most recent Experiences. '''

    def take_recent(self, batch_size):
        return self.memory[-batch_size:]

    '''Take a sample of size batch_size with samples which are more 
    different from our model are more likely to be selected. '''

    def take_priority(self, batch_size):

        ind = random.choices(range(len(self.prob_weight)),
                             k=batch_size, weights=self.prob_weight)

        return list(itemgetter(*ind)(self.memory)), ind

    '''return the length of our memory bank '''

    def __len__(self):
        return len(self.memory)

    '''return a boolean if able to provide experiences for learning'''

    def can_provide_sample(self, batch_size):
        # print("size: ", len(self.memory), " and ", batch_size)
        self.temp_priorities_max = max(self.prob_weight)
        return self.__len__() >= self.capacity / 4

    '''helper function to update probability for priority memories'''

    def update_priorities(self, indices, cur_q, target_q):
        delta = abs(target_q-cur_q)
        self.prob_weight[indices] = delta.detach().numpy().reshape(-1)
