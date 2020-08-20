import torch.nn as nn
import torch.nn.functional as F

'''Class created to configure the structure for our neural networks'''
class DQN(nn.Module):

    '''
    Initialize a neural network for deep Q-learning. 
    num_states: the number of nodes in the network 
    and also the number of outputs for the network.
    num_extra_params: the number of other parameters besides for the 
    one-hot encoded vector for the current node we are taking in.
    Our neural network has 3 layers and 1 hidden layer. 
    '''
    def __init__(self, num_states, num_extra_params):
        super(DQN, self).__init__()
        hidden_size = 2 * num_states
        """ Inputs to hidden layer linear transformation """ 
        self.layer1 = nn.Linear(num_states + num_extra_params, hidden_size)
        """ HL1 to output linear transformation """ 
        self.layer2 = nn.Linear(hidden_size, num_states)
        """ our activation function  """ 
        self.tanh = nn.Tanh()

    ''' Output the result of the network given input x.
    Take in input x, transform to hidden layer, apply tanh to hidden layer,
    and transform them into outputs. '''
    def forward(self, x):
        """  HL1 with tanh activation """ 
        out = self.tanh(self.layer1(x))
        """  Output layer with linear activation """ 
        out = self.layer2(out)
        return out
        