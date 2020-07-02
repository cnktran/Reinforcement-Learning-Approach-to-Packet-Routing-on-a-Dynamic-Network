import networkx as nx
import numpy as np


class Packet:
    def __init__(self, startPos, endPos, curPos, weight):
        self._startPos = None
        self._endPos = None
        self._curPos = None
        self._weight = 0

    def get_startPos(self):
        print("getter method called")
        return self._startPos

    def get_endPos(self):
        print("getter method called")
        return self._endPos

    def get_curPos(self):
        print("getter method called")
        return self._curPos

    def get_weight(self):
        print("getter method called")
        return self._weight

    def set_startPos(self, startNode):
        print("setter method called")
        self._startPos = startNode

    def set_endPos(self, endNode):
        print("setter method called")
        self._endPos = endNode

    def set_curPos(self, curNode):
        print("setter method called")
        self._curPos = curNode

    def set_weight(self, weight):
        print("setter method called")
        self._weight = weight
