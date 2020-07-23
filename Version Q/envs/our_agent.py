import collections
import numpy as np
import random
import networkx as nx


class QAgent(object):
    """
    Agent implementing tabular Q-learning for the NetworkSimulatorEnv.
    """

    def __init__(self, dynetwork):
        self.config = {
            "init_mean": 0.0,  # Initialize Q values with this mean
            "init_std": 0.0,  # Initialize Q values with this standard deviation
            "learning_rate": 0.8,
            "epsilon": 0.6,  # Epsilon in epsilon greedy policies
            "discount": 0.9,
            "n_iter": 10000000, # Number of iterations
            "update_epsilon": False,
            "decay_rate": 0.99999}
          # whether or not we are allowed to upadte epsilon
        self.q = self.generate_q_table(dynetwork._network)

    def generate_q_table(self, network):
        q_table = {}
        dists = nx.floyd_warshall(network, weight='edge_delay')
        num_nodes = len(network)
        for currpos in range(num_nodes):
            nlist = list(network.neighbors(currpos))
            for dest in range(num_nodes):
                q_table[(currpos, dest)] = {}
                for action in nlist:
                    if currpos != dest:
                        try:
                            # all possible neighbors
                            q_table[(currpos, dest)][action] = - dists[action][dest]
                        except KeyError:
                            print("No path aaaaaaaaaaaaaaaaaaaa")
                            q_table[(currpos, dest)][action] = -1000
                    else:
                        q_table[(currpos, dest)][action] = 10
        return q_table

    # returns best action for a given state
    def act(self, state, neighbor):
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
                if self.config['update_epsilon']:
                    self.config['epsilon'] = self.config["decay_rate"] * self.config['epsilon']
                    self.config['learning_rate'] = self.config["decay_rate"] * self.config['learning_rate']
                    if self.config['epsilon'] < 0.05:
                        self.config['epsilon'] = 0.05
                    if self.config['epsilon'] < 0.1:
                        self.config['epsilon'] = 0.1
                    self.config['update_epsilon'] = False

        return next_step

    # updates q-table given current state, reward, and action
    # represent the funciton
    def learn(self, current_event, reward, action):
        if (action == None) or (reward == None):
            pass
        else:
            n = current_event[0]
            dest = current_event[1]

            max_q = max(self.q[(action, dest)].values())  # change to max if necessary

            # Q learning
            self.q[(n, dest)][action] = self.q[(n, dest)][action] + (self.config["learning_rate"])*(reward + self.config["discount"] * max_q - self.q[(n, dest)][action])
    
    #def to_matrix(self):
        
