class Packet(object):
    def __init__(self, startPos, endPos, curPos, index, weight):
        self._startPos = startPos
        self._endPos = endPos
        self._curPos = curPos
        self._index = index
        self._weight = weight

    def get_startPos(self):
        # print("getter method called")
        return self._startPos

    def get_endPos(self):
        # print("getter method called")
        return self._endPos

    def get_curPos(self):
        # print("getter method called")
        return self._curPos

    def get_index(self):
        # print("getter method called")
        return self._index

    def get_weight(self):
        # print("getter method called")
        return self._weight

    def set_startPos(self, startNode):
        # print("setter method called")
        self._startPos = startNode

    def set_endPos(self, endNode):
        # print("setter method called")
        self._endPos = endNode

    def set_curPos(self, curNode):
        # print("setter method called")
        self._curPos = curNode

     def set_index(self, index):
        # print("getter method called")
        self._index = index

    def set_weight(self, weight):
        # print("setter method called")
        self._weight = weight
