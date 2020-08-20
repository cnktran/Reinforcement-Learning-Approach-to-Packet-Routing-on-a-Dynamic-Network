'''Class representing packet which stores the starting position, current position,
destination node, and time steps sent alive'''
class Packet(object):
    def __init__(self, startPos, endPos, curPos, index, weight, time = 0):
        self._startPos = startPos
        self._endPos = endPos
        self._curPos = curPos
        self._index = index
        self._weight = weight
        self._time = time
        self._steps = [startPos]
    def get_startPos(self):
        #print("getter method called")
        return self._startPos

    def get_endPos(self):
        #print("getter method called")
        return self._endPos

    def get_curPos(self):
        #print("getter method called")
        return self._curPos
        
    def get_index(self):
        #print("getter method called")
        return self._index

    def get_weight(self):
        #print("getter method called")
        return self._weight
        
    def get_time(self):
        #print("getter method called")
        return self._time 
        
    def set_startPos(self, startNode):
        #print("setter method called")
        self._startPos = startNode

    def set_endPos(self, endNode):
        #print("setter method called")
        self._endPos = endNode

    def set_curPos(self, curNode):
        #print("setter method called")
        self._curPos = curNode
    
    def set_index(self, index):
        #print("getter method called")
        self._index = index

    def set_weight(self, weight):
        #print("setter method called")
        self._weight = weight
        
    def set_time(self, time):
        #print("getter method called")
        self._time = time 
        
    def add_step(self, step):
        (self._steps).append(step)

'''Class which stores all the packets in the network'''
class Packets(object):
    def __init__(self, packetList):
        self.packetList = packetList
        self.num_Packets = len(packetList)