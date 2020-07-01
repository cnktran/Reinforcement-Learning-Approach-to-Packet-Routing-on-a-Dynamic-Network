#!/usr/bin/env python
# coding: utf-8

# In[9]:


from graph_tool.all import *
from itertools import combinations
from random import sample
from numpy.random import randint
import numpy as np

np.random.seed(42)
import time

num_nodes = 10
num_edges = 3
min_weight = 1
max_weight = 10

g = Graph()
g.add_vertex(num_nodes)
eprop_int = g.new_ep("int")
#create list of edges
for s,t in zip(randint(0, num_nodes, num_edges), randint(0, num_nodes, num_edges)):
  while s == t:
      s = randint(0,num_nodes)
      t = randint(0,num_nodes)
    
  g.add_edge(g.vertex(s), g.vertex(t))

eprop_int.a = randint(min_weight, max_weight, g.num_edges())
g.ep.weights = eprop_int
#g.ep.pen_width = graph_tool.draw.prop_to_size(g.ep.weights, mi=0, ma=5, log=False, power=0.5)
#pos = arf_layout(g, weight = g.ep.weights, max_iter=1000)
graph_draw(g, vertex_text=g.vertex_index) #graph_draw(g, pos = pos, vertex_text=g.vertex_index)
#could also use sfdp_layout(?) to show numbers of connections and hotspots without. relying on edge widths 


# In[36]:


from graph_tool import topology
x= topology.shortest_distance(g, pred_map= True, weights = g.ep.weights)
print(x[g.vertex(3)].a)


# In[39]:


y,z = topology.shortest_path(g, g.vertex(3), g.vertex(4), weights=g.ep.weights)


# In[40]:


print([str(e) for e in z])


# In[ ]:




