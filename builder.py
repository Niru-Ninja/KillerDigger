import os
import math


class Map():
    width = 0
    height = 0
    mapData = []
    mapMatrix = {}

    def __init__(self, _width, _height, _mapData):
        self.width = _width
        self.height = _height
        self.mapData = _mapData
        self.createMapMatrix()

    def createMapMatrix(self):
        width = 0
        height = 0
        for bit in self.mapData:
            self.mapMatrix[(width, height)] = bit
            width += 1
            if width >= self.width:
                width = 0
                height += 1


def charToBinary(char):
    # We decompose a character to 8 binary digits:
    return str(format(int(char), 'b').zfill(8))


def decodeMap(directory):
    # We read the file and decompose everything into bits:
    mapArray = []
    print("\n    Reading File... ")
    with open(directory, "rb") as mapFile:
        for line in mapFile:
            for char in line:
                for elem in list(charToBinary(char)):
                    mapArray.append(int(elem))
    # We calculate the width and height of the map so that it is square with the amount of bits we have:
    print("    Calculating map size... ")
    totalSize = len(mapArray)
    width = math.ceil((math.sqrt(totalSize)))
    height = math.ceil(totalSize / width)
    if width * height > totalSize:
        while len(mapArray) < width * height:
            mapArray.append('0')
    # Return the map:
    mapData = Map(width, height, mapArray)
    return mapData
