import Packet


class Packets:
    def __init__(self, packetList, num_Packets):
        self.packetList = None
        self.num_Packets = 0

    def fillPackets(self, listOfPackets):
        self.packetList = listOfPackets
        self.num_Packets = len(listOfPackets)
# below function '''

    def randomGenerate(self, num_packets):
        tempList = []
        for i in range(num_packets):

            # node initialization
            startNode = self.nodes(randint(0, len(self)))
            endNode = self.nodes(randint(0, len(self)))

            while (startNode == endNode):
                endNode = self.nodes(randint(0, len(self)))

            # give weight zero in the begining
            curPack = Packet(startNode, endNode, startNode, 0)

            tempList.append(curPack)
        # creat Packets Object
        packetsObj = Packets(tempList)

        # Assign Packets Object to the network
        self.packets = packetsObj
