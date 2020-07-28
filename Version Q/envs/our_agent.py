import collections
import numpy as np
import random
import networkx as nx

'''
    The agent file defines a learning agent and its hyperparameters
    File contains functions:
        genreate_q_table: initialize Q-table
        act: returns which next node to send packet to
        learn: update Q-table after receving corresponding rewards
'''
class QAgent(object):

    def __init__(self, dynetwork):
        self.config = {
            "learning_rate": 0.8,
            "epsilon": 0.6,  # epsil %
            "discount": 0.9,
            "update_epsilon": False,
            "decay_rate": 0.999}
          # whether or not we are allowed to upadte epsilon
        self.q = self.generate_q_table(dynetwork._network)

    ''' Use this function to set up the q-table'''
    def generate_q_table(self, network):
        q_table = {}
        #dists = nx.floyd_warshall(network, weight='edge_delay')
        num_nodes = len(network)
        for currpos in range(num_nodes):
            nlist = list(network.neighbors(currpos))
            for dest in range(num_nodes):
                q_table[(currpos, dest)] = {}
                for action in nlist:
                    if currpos != dest:
                        ''' Initialize 0 Q-table except destination '''
                        q_table[(currpos, dest)][action] = 0
                        
                        ''' Different approach to learning policy'''
                        ''' Initialize using Shortest Path'''
                        # try:
                        #     # all possible neighbors
                        #     q_table[(currpos, dest)][action] = - dists[action][dest]
                        # except KeyError:
                        #     print("No path")
                        #     q_table[(currpos, dest)][action] = -1000
                        ''' Initialize using Shortest Path'''
                    else:
                        q_table[(currpos, dest)][action] = 10
        return q_table

    '''Returns best action for a given state. '''
    def act(self, state, neighbor):
        ''' We will either random walk or reference Q-table with probability epsilon ''' 
        if random.uniform(0, 1) < self.config['epsilon']:
            # bool(list) or bool(dict) evaluate to false if either are empty
            if not bool(neighbor):
                return None
            else:
                next_step = random.choice(neighbor)  # Explore action space
        else:
            temp_neighbor_dict = {n: self.q[state][n] for n in self.q[state] if n in neighbor}
            if not bool(temp_neighbor_dict):
                return None
            else:
                next_step = max(temp_neighbor_dict, key=temp_neighbor_dict.get)
                """ config['update_epsilon'] is only True when all nodes have been visited
                then we decrease parameters epsilon and learning_rate by our decay rate """
                if self.config['update_epsilon']:
                    self.config['epsilon'] = self.config["decay_rate"] * self.config['epsilon']
                    self.config['learning_rate'] = self.config["decay_rate"] * self.config['learning_rate']
                    if self.config['epsilon'] < 0.05:
                        self.config['epsilon'] = 0.05
                    if self.config['learning_rate'] < 0.075:
                        self.config['learning_rate'] = 0.075
                    self.config['update_epsilon'] = False

        return next_step

    """updates q-table given current state, reward, and action where a state is a (Node, destination) pair and an action is a step to of the neighbors of the Node"""
    def learn(self, current_event, reward, action):
        if (action == None) or (reward == None):
            pass
        else:
            n = current_event[0]
            dest = current_event[1]

            max_q = max(self.q[(action, dest)].values())  # change to max if necessary

            # Q learning
            self.q[(n, dest)][action] = self.q[(n, dest)][action] + (self.config["learning_rate"])*(reward + self.config["discount"] * max_q - self.q[(n, dest)][action])
    
    
    '''Future plan Turn Q-table into matrix for more math calculation'''
    #def to_matrix(self):
        