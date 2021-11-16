import pygame
import math
from pathlib import Path
import os
# Personal imports:
import builder
import spriteManager

tilesize = spriteManager.tilesize


def renderScreen():
    global tilesize
    global cameraX, cameraY
    global entityDict, entityList, rectList

    spriteManager.screen.fill((0, 0, 0))
    entityList = []
    rectList = []
    for ypos in range(0, spriteManager.yRes//tilesize + 2):
        for xpos in range(0, spriteManager.xRes//tilesize + 2):
            try:
                entityList.extend(
                    entityDict[(cameraX//tilesize + xpos, cameraY//tilesize + ypos)])
                rectList.append(pygame.Rect(
                    entityDict[(cameraX//tilesize + xpos, cameraY //
                                tilesize + ypos)][0].posx,
                    entityDict[(cameraX//tilesize + xpos, cameraY //
                                tilesize + ypos)][0].posy,
                    entityDict[(cameraX//tilesize + xpos, cameraY //
                                tilesize + ypos)][0].width,
                    entityDict[(cameraX//tilesize + xpos, cameraY //
                                tilesize + ypos)][0].height
                ))
            except KeyError:
                pass


def checkForSolidsInTile(coords):
    global entityDict
    try:
        tile = entityDict[coords]
    except KeyError:
        return True
    for entity in tile:
        if entity.solid:
            return True
    return False


def findBlockNeighbors(X, Y):
    global theMap
    try:
        bit1 = str(theMap.mapMatrix[(X-1, Y-1)])
    except KeyError:
        bit1 = "1"
    try:
        bit2 = str(theMap.mapMatrix[(X, Y-1)])
    except KeyError:
        bit2 = "1"
    try:
        bit3 = str(theMap.mapMatrix[(X+1, Y-1)])
    except KeyError:
        bit3 = "1"
    try:
        bit4 = str(theMap.mapMatrix[(X-1, Y)])
    except KeyError:
        bit4 = "1"
    try:
        bit5 = str(theMap.mapMatrix[(X+1, Y)])
    except KeyError:
        bit5 = "1"
    try:
        bit6 = str(theMap.mapMatrix[(X-1, Y+1)])
    except KeyError:
        bit6 = "1"
    try:
        bit7 = str(theMap.mapMatrix[(X, Y+1)])
    except KeyError:
        bit7 = "1"
    try:
        bit8 = str(theMap.mapMatrix[(X+1, Y+1)])
    except KeyError:
        bit8 = "1"
    return bit1 + bit2 + bit3 + bit4 + bit5 + bit6 + bit7 + bit8


class Entity():
    # Stats:
    health = 100
    armor = 0
    # Graphics parameters:
    width = 64
    height = 64
    posx = 0
    posy = 0
    sprite = spriteManager.defaultSprite
    depth = 0
    solid = False
    tag = ""

    def __init__(self, _width, _height, _posx, _posy, _sprite, _depth, _solid, _tag):
        self.width = _width
        self.height = _height
        self.posx = _posx
        self.posy = _posy
        self.sprite = _sprite
        self.depth = _depth
        self.solid = _solid
        self.tag = _tag

    def draw(self):
        global cameraX, cameraY
        spriteManager.screen.blit(
            self.sprite, (self.posx - cameraX, self.posy - cameraY, self.width, self.height))


class Wall(Entity):

    def __init__(self, _width, _height, _posx, _posy, _sprite, _depth, _solid, _tag, _biome, _wallName):
        self.width = _width
        self.height = _height
        self.posx = _posx
        self.posy = _posy
        self.sprite = _sprite
        self.depth = _depth
        self.solid = _solid
        self.tag = _tag
        self.biome = _biome
        self.wallName = _wallName

    def hit(self, dmg):
        global entityDict, tilesize
        self.health -= dmg
        print(self.health)
        if self.health <= 0:
            try:
                entityDict[(math.floor(self.posx/tilesize),
                            math.floor(self.posy/tilesize))].remove(self)
                theMap.mapMatrix[(math.floor(self.posx/tilesize),
                                  math.floor(self.posy/tilesize))] = 0
                self.rebuildSurrondings()
            except KeyError:
                pass

    def rebuildSurrondings(self):
        width = math.floor(self.posx/tilesize)-1
        height = math.floor(self.posy/tilesize)-1
 # Our column counter to reset the row to zero every time we go down.
        colCount = 0
        # Because we use 8 bits instead of 9, I have to declare this variable to recognize the middle row where I only need 2 bits instead of 3.
        rowCount = 0
        jumped = False
        for char in self.wallName:
            if rowCount != 1:
                if colCount >= 3:
                    colCount = 0
                    rowCount += 1
            else:
                if colCount == 1:
                    colCount = 2
            if char == "1":
                neighbors = findBlockNeighbors(width+colCount, height+rowCount)
                for entity in entityDict[(width+colCount, height+rowCount)]:
                    if entity.tag == "wall":
                        newWallSprite = rockLand.findWallSprite(neighbors)
                        entity.sprite = newWallSprite[0]
                        entity.wallName = newWallSprite[1]
                entityList.extend(
                    entityDict[(width+colCount, height+rowCount)])
            colCount += 1
            if rowCount == 1 and colCount == 3:
                rowCount += 1
                colCount = 0
        return


class Player(Entity):
    velocity = 5
    solid = True
    moving = "Left"
    state_body = "Idle"
    state_hands = "Idle"
    state_head = "Idle"
    # Step counter so as not to mine each frame instantly if we keep the button pressed.
    miningStep = 0
    mineHitFrame = 24  # Frame in which we hit to mine and reset the counter.

    def __init__(self, _width, _height, _posx, _posy, _velocity, _sprite, _depth):
        self.width = _width
        self.height = _height
        self.posx = _posx
        self.posy = _posy
        self.velocity = _velocity
        self.sprite = _sprite
        self.depth = _depth

    def inCollision(self, keyMove):
        global tilesize
        xCoords = self.posx / tilesize
        yCoords = self.posy / tilesize
        xCoordsExt = (self.posx + self.width) / tilesize
        yCoordsExt = (self.posy + self.height) / tilesize
        # tile = (IsSolid, Initial Coord, Final Coord) Xs and Ys in Player space (not in integer tile coordinates). The coords can be Xs if going up / down or Ys if going left / right
        if keyMove == "w":
            tileList = [
                (checkForSolidsInTile((round(xCoords-1), math.floor(yCoords))),
                 round(self.posx-tilesize), round(self.posx)),
                (checkForSolidsInTile((round(xCoords), math.floor(yCoords))), round(
                    self.posx), round(self.posx+tilesize)),
                (checkForSolidsInTile((round(xCoords+1), math.floor(yCoords))),
                 round(self.posx+tilesize), round(self.posx+tilesize+tilesize))
            ]
            for tile in tileList:
                if tile[0]:
                    if self.posx < tile[2] and self.posx+self.width > tile[1]:
                        return True
            return False
        if keyMove == "a":
            tileList = [
                (checkForSolidsInTile((math.floor(xCoords), round(yCoords-1))),
                 round(self.posy-tilesize), round(self.posy)),
                (checkForSolidsInTile((math.floor(xCoords), round(yCoords))), round(
                    self.posy), round(self.posy+tilesize)),
                (checkForSolidsInTile((math.floor(xCoords), round(yCoords+1))),
                 round(self.posy+tilesize), round(self.posy+tilesize+tilesize))
            ]
            for tile in tileList:
                if tile[0]:
                    if self.posy < tile[2] and self.posy+self.height > tile[1]:
                        return True
            return False
        if keyMove == "s":
            tileList = [
                (checkForSolidsInTile((round(xCoords-1), math.floor(yCoords+1))),
                 round(self.posx-tilesize), round(self.posx)),
                (checkForSolidsInTile((round(xCoords), math.floor(
                    yCoords+1))), round(self.posx), round(self.posx+tilesize)),
                (checkForSolidsInTile((round(xCoords+1), math.floor(yCoords+1))),
                 round(self.posx+tilesize), round(self.posx+tilesize+tilesize))
            ]
            for tile in tileList:
                if tile[0]:
                    if self.posx < tile[2] and self.posx+self.width > tile[1]:
                        return True
            return False
        if keyMove == "d":
            tileList = [
                (checkForSolidsInTile((math.floor(xCoords+1), round(yCoords-1))),
                 math.floor(self.posy-tilesize), math.floor(self.posy)),
                (checkForSolidsInTile((math.floor(xCoords+1), round(yCoords))),
                 math.floor(self.posy), math.floor(self.posy+tilesize)),
                (checkForSolidsInTile((math.floor(xCoords+1), round(yCoords+1))),
                 math.floor(self.posy+tilesize), math.floor(self.posy+tilesize+tilesize))
            ]
            for tile in tileList:
                if tile[0]:
                    if self.posy < tile[2] and self.posy+self.height > tile[1]:
                        return True
            return False

    def move(self, k_w, k_a, k_s, k_d, k_space):
        global entityList, entityDict, rectList, tilesize
        global cameraX, cameraY, cameraSpeed

        rectList.append(pygame.Rect(self.posx-self.width, self.posy -
                        self.height, self.posx+self.width, self.posy+self.height))
        xCoords = self.posx / tilesize
        yCoords = self.posy / tilesize
        if k_w:
            if not self.inCollision("w"):
                self.posy -= self.velocity
                self.state_body = "Walking"
                self.state_head = "Walking"
                self.state_hands = "Walking"
        if k_a:
            self.moving = "Left"
            if not self.inCollision("a"):
                self.posx -= self.velocity
                self.state_body = "Walking"
                self.state_head = "Walking"
                self.state_hands = "Walking"
        if k_s:
            if not self.inCollision("s"):
                self.posy += self.velocity
                self.state_body = "Walking"
                self.state_head = "Walking"
                self.state_hands = "Walking"
        if k_d:
            self.moving = "Right"
            if not self.inCollision("d"):
                self.posx += self.velocity
                self.state_body = "Walking"
                self.state_head = "Walking"
                self.state_hands = "Walking"
        if not k_w and not k_a and not k_s and not k_d:
            self.state_body = "Idle"
            self.state_head = "Idle"
            self.state_hands = "Idle"
        # Actions:
        if k_space:
            if self.miningStep == 0:
                if self.moving == "Left":
                    try:
                        for item in entityDict[(math.floor(xCoords), round(yCoords))]:
                            if item.solid:
                                item.hit(25)
                    except KeyError:
                        pass
                else:
                    try:
                        for item in entityDict[(round(xCoords+1), round(yCoords))]:
                            if item.solid:
                                item.hit(25)
                    except KeyError:
                        pass
                self.miningStep += 1
            elif self.miningStep >= self.mineHitFrame:
                self.miningStep = 0
            else:
                self.miningStep += 1
        # We update all the cells that are close to the player to erase him when he moves (movement and animation):
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords), math.floor(yCoords))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords-1), math.floor(yCoords-1))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords), math.floor(yCoords-1))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords+1), math.floor(yCoords-1))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords-1), math.floor(yCoords))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords+1), math.floor(yCoords))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords-1), math.floor(yCoords+1))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords), math.floor(yCoords+1))])
        except KeyError:
            pass
        try:
            entityList.extend(
                entityDict[(math.floor(xCoords+1), math.floor(yCoords+1))])
        except KeyError:
            pass
        # If the player approaches an edge, we move the camera:
        marginX = spriteManager.xRes//7
        marginY = spriteManager.yRes//5
        if self.posx - cameraX > spriteManager.xRes/2 + marginX:
            cameraX += cameraSpeed
            renderScreen()
        if self.posx - cameraX < spriteManager.xRes/2 - marginX:
            cameraX -= cameraSpeed
            renderScreen()
        if self.posy - cameraY > spriteManager.yRes/2 + marginY:
            cameraY += cameraSpeed
            renderScreen()
        if self.posy - cameraY < spriteManager.yRes/2 - marginY:
            cameraY -= cameraSpeed
            renderScreen()
        # We render the player:
        rectList.append(pygame.Rect(self.posx-self.width, self.posy -
                        self.height, self.posx+self.width, self.posy+self.height))
        entityList.append(self)

    def draw(self):
        global cameraX, cameraY
        spriteManager.screen.blit(self.sprite.giveSprite(self.state_body, self.state_head, self.state_hands,
                                  self.moving), (self.posx - cameraX, self.posy - cameraY, self.width, self.height))


# We create a dictionary with a tuple of coordinates as key and the object as value:
entityDict = {}
# We create a list with the entities that must be drawn:
entityList = []
# We create a list with the rectangles to render selectively:
rectList = []

# We load sprites from biomes:
rockLand = spriteManager.Biome("RockLand", [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 3, 3, 3, 1, 3,
                               3, 3, 1, 3, 3, 3, 1, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], 4)

# We build the map:
theMap = builder.decodeMap("map")
width = 0
height = 0
startingCoords = (width, height)
# True when we find a position, to try to appear at the top left of the map and not at the bottom right
foundStartingCoords = False
while height < theMap.height:
    while width < theMap.width:
        bit = theMap.mapMatrix[(width, height)]
        neighbors = findBlockNeighbors(width, height)
        try:
            bit2 = theMap.mapMatrix[(width, height-1)]
        except KeyError:
            bit2 = 1
        # We save if there is an empty space for the player's initial coordinates:
        if width > 1 and height > 1 and bit == 0 and bit2 == 0 and not foundStartingCoords:
            startingCoords = (width, height)
            print(startingCoords)
            foundStartingCoords = True
        entitiesInTile = [Entity(tilesize, tilesize, width*tilesize,
                                 height*tilesize, rockLand.findFloorSprite(), 1, False, "floor")]
        if bit == 1:
            newWallSprite = rockLand.findWallSprite(neighbors)
            entitiesInTile.append(Wall(tilesize, tilesize, width*tilesize, height *
                                  tilesize, newWallSprite[0], 0, True, "wall", rockLand, newWallSprite[1]))
        entityDict[(width, height)] = entitiesInTile
        entityList.extend(entitiesInTile)
        width += 1
    width = 0
    height += 1
# We pass the startingCoords to the tile space:
startingCoords = (startingCoords[0]*tilesize, startingCoords[1]*tilesize)

# General moving speed:
# is given in tiles (depends on the scale)
generalSpeed = round(tilesize/32)

# Camera:
cameraX = 0
cameraY = 0
cameraSpeed = generalSpeed

playerSprite = spriteManager.PlayerSprites()
# We find some coordinates to put the player, where there are no walls:

player = Player(playerSprite.width, playerSprite.height,
                startingCoords[0], startingCoords[1], generalSpeed, playerSprite, -1)
entityList.append(player)

# Main Loop:
clock = pygame.time.Clock()
done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
    # We move the player:
    keys = pygame.key.get_pressed()
    player.move(keys[pygame.K_w], keys[pygame.K_a],
                keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_SPACE])
    # We draw everything that is needed:
    entityList.sort(reverse=True, key=lambda ent: ent.depth)
    for entity in entityList:
        entity.draw()
    pygame.display.flip()
    # pygame.display.update(rectList)
    entityList = []
    rectList = []
    clock.tick(spriteManager.frameRate)

pygame.quit()
