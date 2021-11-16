import pygame
from pathlib import Path
from random import randrange
import re

wallNames = [
    "01A10A0A",
    "01A1011A",  # EX "01A10A1A",
    "01A1001A",
    "11A10A0A",
    "11A1001A",
    "01011A0A",
    "01111A0A",
    "11111A0A",
    "01011010",
    "01011011",
    "01011110",
    "01011111",  # only 1
    "01111010",
    "01111011",
    "01111110",
    "01111111",  # only 1
    "11011010",
    "11011011",
    "11011110",
    "11011111",  # only 1
    "11111010",
    "11111011",
    "11111110",
    "11111111",  # only 1
    "A0A00A0A",
    "A0A00A1A",
    "A0A01A0A",
    "A0A01A10",
    "A0A01A11",
    "A0A10A0A",
    "A0A11A0A",
    "A0A11A1A",
    "A0A1001A",
    "A0A1011A",
    "A0A11010",
    "A0A11011",
    "A0A11110",
    "A1A00A0A",
    "A1A00A1A",
    "A1101A11",  # EX "A1A01A1A",
    "11A1011A",  # EX "A1A10A1A",
    "A1001A0A",
    "A1001A11",  # EX "A1001A1A",
    "A1001A10",
    "A1011A0A",
    "A1101A0A",
    "A1101A10"
]

regexNames = [
    "01011010",
    "01011011",
    "01011110",
    "01011111",
    "01111010",
    "01111011",
    "01111110",
    "01111111",
    "11011010",
    "11011011",
    "11011110",
    "11011111",
    "11111010",
    "11111011",
    "11111110",
    "11111111",
    "01011[01]0[01]",
    "01111[01]0[01]",
    "11111[01]0[01]",
    "01[01]1001[01]",
    "01[01]1011[01]",  # EX "01[01]10[01]1[01]",
    "11[01]1001[01]",
    "11[01]1011[01]",  # EX "[01]1[01]10[01]1[01]"
    "[01]0[01]11010",
    "[01]0[01]11011",
    "[01]0[01]11110",
    "[01]1001[01]10",
    "[01]1001[01]11",  # EX "[01]1001[01]1[01]",
    "[01]1101[01]10",
    "[01]1101[01]11",  # EX "[01]1[01]01[01]1[01]",
    "01[01]10[01]0[01]",
    "11[01]10[01]0[01]",
    "[01]0[01]01[01]10",
    "[01]0[01]01[01]11",
    "[01]0[01]1001[01]",
    "[01]0[01]1011[01]",
    "[01]1001[01]0[01]",
    "[01]1011[01]0[01]",
    "[01]1101[01]0[01]",
    "[01]0[01]00[01]0[01]",
    "[01]0[01]00[01]1[01]",
    "[01]0[01]01[01]0[01]",
    "[01]0[01]10[01]0[01]",
    "[01]0[01]11[01]0[01]",
    "[01]0[01]11[01]1[01]",
    "[01]1[01]00[01]0[01]",
    "[01]1[01]00[01]1[01]"
]

tilesize = 128
frameRate = 60  # FPS
animationFrameRate = 12  # FPSs of the animations.
defaultSprite = pygame.transform.scale(pygame.image.load(str(Path(
    __file__).parent.absolute()) + "\\Resources\\Default.png"), (tilesize, tilesize))

pygame.init()
# Open the file to read the configuration:
configfile = open("config.txt", "r")
# If the config file exists and we can read it:
if configfile.mode == 'r':
    # We read the first line (Corresponding to resolution. Ex:resolution: 1920x1080)
    textline = configfile.read()
    # We format the text line for more flexibility:
    textline = textline.replace(" ", "")
    textline = textline.lower()
    if textline.startswith("resolution:"):
        slicepoint = textline.find("x")
        xRes = int(textline[11:slicepoint])
        yRes = int(textline[slicepoint+1:len(textline)])
# Setting the screen options:
screen = pygame.display.set_mode((xRes, yRes))
pygame.display.set_caption("Killer Digger")


def generateRandomIndex(value):
    return randrange(value)


class Biome():
    biomeName = ""
    wallVarieties = []
    wallVarietiesDict = {}
    wallSprites = {}
    floorVarieties = 1
    floorSprites = []

    def __init__(self, _biomeName, _wallVarieties, _floorVarieties):
        global wallNames
        self.biomeName = _biomeName
        self.wallVarieties = _wallVarieties
        self.floorVarieties = _floorVarieties

        index = 0
        for name in wallNames:
            self.wallVarietiesDict[name] = self.wallVarieties[index]
            index += 1
        self.loadSprites()

    def loadSprites(self):
        global wallNames, tilesize
        # Index that we use to go through the array wallVarieties in parallel.
        mainIndex = 0
        for name in wallNames:
            path = str(Path(__file__).parent.absolute()) + \
                "\\Resources\\Biomes\\"+self.biomeName+"\\"+name
            spritesToAdd = []
            if self.wallVarieties[mainIndex] > 1:
                for item in range(1, self.wallVarieties[mainIndex]+1):
                    endName = "-0" + str(item) + ".png"
                    spritesToAdd.append(pygame.transform.scale(pygame.image.load(
                        path + endName), (tilesize, tilesize)).convert_alpha())
            else:
                spritesToAdd.append(pygame.transform.scale(pygame.image.load(
                    path+".png"), (tilesize, tilesize)).convert_alpha())
            self.wallSprites[name] = spritesToAdd
            mainIndex += 1

        for num in range(1, self.floorVarieties+1):
            path = str(Path(__file__).parent.absolute()) + \
                "\\Resources\\Biomes\\"+self.biomeName+"\\F"+str(num)+".png"
            self.floorSprites.append(pygame.transform.scale(
                pygame.image.load(path), (tilesize, tilesize)).convert_alpha())

    def findWallSprite(self, bitList):
        global regexNames, defaultSprite
        retMe = defaultSprite
        for regex in regexNames:
            if re.search(regex, bitList):
                spriteName = regex.replace("[01]", "A")
                ranInd = generateRandomIndex(
                    self.wallVarietiesDict[spriteName])
                retMe = (self.wallSprites[spriteName][ranInd], spriteName)
                break
        return retMe

    def findFloorSprite(self):
        global defaultSprite
        try:
            return self.floorSprites[generateRandomIndex(self.floorVarieties)]
        except:
            return defaultSprite


class AnimatedSprite():
    global defaultSprite, frameRate, animationFrameRate
    name = ""
    mainSprite = defaultSprite
    frameCount = 0
    frameMaxValue = frameRate // animationFrameRate
    spriteStep = 0
    positionStep = 0
    spriteDict = {}
    posDict = {}

    def __init__(self, _name, _spriteDict, _posDict, _currentSpriteState, _currentPosState,  _mainSprite=defaultSprite):
        self.name = _name
        self.mainSprite = _mainSprite
        self.spriteDict = _spriteDict
        self.posDict = _posDict
        self.currentSpriteState = _currentSpriteState
        self.currentPosState = _currentPosState

    def step(self, spriteState, posState):
        if self.frameCount >= self.frameMaxValue:
            if self.spriteDict != {}:
                self.spriteStep += 1
                if self.spriteStep >= len(self.spriteDict[spriteState]):
                    self.spriteStep = 0
            if self.posDict != {}:
                self.positionStep += 1
                if self.positionStep >= len(self.posDict[posState]):
                    self.positionStep = 0
            self.frameCount = 0
        else:
            self.frameCount += 1

    def sprite(self, spriteState, posState):
        # If we change state we make sure to start the animation from the beginning:
        if self.currentSpriteState != spriteState:
            self.spriteStep = 0
            self.currentSpriteState = spriteState
        if self.currentPosState != posState:
            self.positionStep = 0
            self.currentPosState = posState
        if self.posDict == {} or posState == None:
            returnPosition = (0, 0)
        else:
            returnPosition = self.posDict[posState][self.positionStep]
        if self.spriteDict == {} or spriteState == None:
            returnSprite = self.mainSprite
        else:
            returnSprite = self.spriteDict[spriteState][self.spriteStep]
        self.step(spriteState, posState)
        return (returnSprite, returnPosition)


class PlayerSprites():
    scaleIndex = tilesize // 16
    bodyHeight = 10
    bodyWidth = 7
    pixelMarginX = 6
    pixelMarginY = 3
    spriteMarginX = pixelMarginX * scaleIndex
    spriteMarginY = pixelMarginX * scaleIndex
    totBodHeight = int(bodyHeight * scaleIndex)
    totBodWidth = int(bodyWidth * scaleIndex)
    width = totBodWidth + spriteMarginX
    height = totBodHeight + spriteMarginY
    path = "\\Resources\\Player\\"

    spriteSurface = pygame.Surface(
        (int(totBodWidth+spriteMarginX), int(totBodHeight+spriteMarginY))).convert_alpha()

    body_spriteDict = {  # Status: [List of sprites with all frames]
        "Idle":    	  [pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute()) + path + "idle.png"), (totBodWidth, totBodHeight)).convert_alpha()],
        "Walking":    [
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-1.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-2.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-3.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-4.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-5.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-6.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-7.png"), (totBodWidth, totBodHeight)).convert_alpha(),
            pygame.transform.scale(pygame.image.load(str(Path(__file__).parent.absolute(
            )) + path + "walk-8.png"), (totBodWidth, totBodHeight)).convert_alpha()
        ],
        "Running":    [],
        "SneakingIdle":   [],
        "SneakingWalking":    []
    }
    headImage = pygame.transform.scale(pygame.image.load(str(Path(
        __file__).parent.absolute()) + path + "head.png"), (4*scaleIndex, 4*scaleIndex)).convert()
    head_posDict = {
        "Idle": [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, -1), (0, -1), (0, -1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 1), (0, 1), (0, 1), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)],
        "Walking": [(1, -1), (0, 1), (0, -1), (1, -2), (1, -1), (1, 1), (0, -1), (0, -2)]
    }
    handImage = pygame.transform.scale(pygame.image.load(str(Path(
        __file__).parent.absolute()) + path + "hand.png"), (2*scaleIndex, 2*scaleIndex)).convert()
    Lhand_posDict = {
        "Idle": [(0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 7), (0, 7), (0, 7), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 9), (0, 9), (0, 9), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8), (0, 8)],
        "Walking": [(0, 5), (-1, 5), (1, 8), (5, 7), (5, 8), (6, 9), (0, 8), (-1, 5)]
    }
    Rhand_posDict = {
        "Idle": [(5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 7), (5, 7), (5, 7), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 9), (5, 9), (5, 9), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8), (5, 8)],
        "Walking": [(5, 9), (5, 9), (0, 8), (-1, 5), (-1, 6), (-1, 6), (0, 8), (4, 7)]
    }

    bodySprite = AnimatedSprite("Body", body_spriteDict, {}, "Idle", None)
    headSprite = AnimatedSprite(
        "Head", {}, head_posDict, None, "Idle", headImage)
    LHandSprite = AnimatedSprite(
        "LHand", {}, Lhand_posDict, None, "Idle", handImage)
    RHandSprite = AnimatedSprite(
        "RHand", {}, Rhand_posDict, None, "Idle", handImage)

    def giveSprite(self, bodyState, headState, handsState, direction):
        bodyTuple = self.bodySprite.sprite(bodyState, None)
        headTuple = self.headSprite.sprite(None, headState)
        LHandTuple = self.LHandSprite.sprite(None, handsState)
        RHandTuple = self.RHandSprite.sprite(None, handsState)

        self.spriteSurface.fill(
            (255, 255, 255, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.spriteSurface.blit(bodyTuple[0], ((bodyTuple[1][0]+(self.pixelMarginX/2))*self.scaleIndex,
                                (bodyTuple[1][1]+self.pixelMarginY)*self.scaleIndex, self.totBodWidth, self.totBodHeight))
        self.spriteSurface.blit(headTuple[0], ((headTuple[1][0]+(self.pixelMarginX/2)-1)*self.scaleIndex,
                                (headTuple[1][1]+self.pixelMarginY-1)*self.scaleIndex, 4*self.scaleIndex, 4*self.scaleIndex))
        self.spriteSurface.blit(LHandTuple[0], ((LHandTuple[1][0]+(self.pixelMarginX/4))*self.scaleIndex,
                                (LHandTuple[1][1]+(self.pixelMarginY-4))*self.scaleIndex, 2*self.scaleIndex, 2*self.scaleIndex))
        self.spriteSurface.blit(RHandTuple[0], ((RHandTuple[1][0]+(self.pixelMarginX/4))*self.scaleIndex,
                                (RHandTuple[1][1]+(self.pixelMarginY-4))*self.scaleIndex, 2*self.scaleIndex, 2*self.scaleIndex))

        if direction == "Right":
            self.spriteSurface = pygame.transform.flip(
                self.spriteSurface, True, False)

        return self.spriteSurface
