# The system is based on a 2D array of tiles, where a tile has
# chemical A from 0 to 1
# chemical B from 0 to 1
# positions in x, y
# positions in c, r



# INVARIANTS:
# A tile has 8 neighbors at any given time


# MODULES
import pygame
import random
import math

# DATA DEFS
DIMS = (160,160)
RES = 4
SCREEN = (DIMS[0]*RES,DIMS[1]*RES)
display = pygame.display.set_mode(SCREEN)

# 0.055
# 0.062
dA = 1
dB = 0.5
feed = 0.0545
k = 0.062
t = 1.5
# TIMER = 10

# DD. TILE
# tile = Tile()
# interp. a tile in the system
class Tile():
    def __init__(self,x,y):
        # Attribures relative to position
        self.x = x * RES #position in x relative to pixels on the screen
        self.y = y * RES #position in y relative to pixels on the screen
        self.c = x       #position in column relative to grid
        self.r = y       #position in row relative to grid
        # chemicals
        self.A = 1
        self.B = 0
        self.Ap = 0
        self.Bp = 0
        self.rect = pygame.Rect(self.x, self.y, RES, RES)
        self.color = (0,0,0)
        # A tile has 8 neighbors at any given time
        self.neighbors = None

    def getColor(self):
        # FD. remap()
        # Signature: float, float, float, float, float -> float
        # purp. rescale a given value
        def remap(value, from1, to1, from2, to2):
            return (value - from1) / (to1 - from1) * (to2 - from2) + from2

        r = math.floor(remap(self.A,0,1,0,255))
        g = math.floor(remap(self.B,0,1,0,255))
        self.color = (r,g,0)

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,(self.x, self.y, RES, RES))
        self.getColor()


# DD. TILEGRID
# tileGrid = [[TILE, ...], ... TILE]
# interp. a 2D array of tiles in the animation
tileGrid = []
for y in range(DIMS[1]):
    tileRow = []
    for x in range(DIMS[0]):
        tile = Tile(x,y)
        tileRow.append(tile)
    tileGrid.append(tileRow)


def fn_for_tileGrid(fn,*args):
    for r, tileRow in enumerate(tileGrid):
        for c, tile in enumerate(tileRow):
            fn(tile,*args)

# FD. getNeighbors()
# Signature: tile -> None
# purp. get the neighbors of this tile relative to the tileGrid
def getNeighbors(tile):
    r = tile.r
    c = tile.c
    # identify the neighbors to this tile and put the on a list
    tile.neighbors = [
        tileGrid[r-1][c-1],tileGrid[r-1][c],tileGrid[r-1][(c+1)%len(tileGrid[0])],
        tileGrid[r][c-1],tileGrid[r][c],tileGrid[r][(c+1)%len(tileGrid[0])],
        tileGrid[(r+1)%len(tileGrid)][c-1],tileGrid[(r+1)%len(tileGrid)][c],tileGrid[(r+1)%len(tileGrid)][(c+1)%len(tileGrid[0])]
    ]

fn_for_tileGrid(getNeighbors)


######################### CODE #########################

# 1. Seed a small area with B=1
size = 60
for y in range(size):
    for x in range(size):
        tileGrid[(DIMS[1]//2-(size//2))+y][(DIMS[0]//2-(size//2))+x].B = 1.0

def draw():
    # 1. bg
    display.fill("#1e1e1e")
    # 2. draw tiles
    fn_for_tileGrid(Tile.draw,display)
    # 3. update
    pygame.display.flip()
    pygame.time.Clock().tick()

def userInput():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        

def updateTiles():
    # take the current states in the tiles and update their chemicals A and B

    # FD. laplace()
    # Signature: TILE -> float, float
    # purp. get the values for the laplace transformations for the chemical A and B
    # The laplacian is performed with a 3x3 convolution where:
    # center (tile) is      -1
    # adjascent neighbors   0.2
    # corners               0.05
    def laplace(tile):
        sumA = 0
        sumB = 0
        # 1. get the values of the neighbors at the following indexes:
        # 0 top-left        (0.05)
        # 1 top-center      (0.2)
        # 2 top-right       (0.05)
        # 3 center-left     (0.2)
        # 4 current Tile    (-1.0)
        # 5 center-right    (0.2)
        # 6 bottom-left     (0.05)
        # 7 bottom-center   (0.2)
        # 8 bottom-right    (0.05)
        coeffs = [0.05,0.2,0.05,0.2,-1.0,0.2,0.05,0.2,0.05]
        for ix,n in enumerate(coeffs):
            sumA += tile.neighbors[ix].A * n
            sumB += tile.neighbors[ix].B * n
        return(sumA, sumB)
        

    # FD. increaseChem()
    # Signature: TILE -> None
    # purp. increase the amount of chemicals A and B
    def increaseChem(tile):
        laplaceA, laplaceB = laplace(tile)
        tile.Ap = tile.A + (dA * laplaceA) - (tile.A * tile.B * tile.B) + (feed * (1-tile.A))
        tile.Ap = tile.Ap * t
        tile.Bp = tile.B + (dB * laplaceB) + (tile.A * tile.B * tile.B) - ((k + feed) * tile.B)
        tile.Bp = tile.Bp * t
        # constrain the values between 0 and 1
        tile.Ap = 0 if tile.Ap <=0 else tile.Ap
        tile.Ap = 1 if tile.Ap >=1 else tile.Ap

        tile.Bp = 0 if tile.Bp <=0 else tile.Bp
        tile.Bp = 1 if tile.Bp >=1 else tile.Bp

    # FD. swap()
    # Signature: TILE -> None
    # purp. make the new values in A and B the old values in A and B
    def swap(tile):
        tile.A = tile.Ap
        tile.B = tile.Bp

    fn_for_tileGrid(increaseChem)
    fn_for_tileGrid(swap)


def update():
    userInput()
    updateTiles()
    


while True:
    draw()
    update()