from enum import Enum

CANVAS_WIDTH = 160
CANVAS_HEIGHT = 144
TILE_SIZE = 16

COLLISION_TILES = [39, 40, 41, 50, 52, 53] # The tile ID of each collidable tile in Tiled

class GAMESTATE(Enum):
    TITLE = 0
    GAMEPLAY = 1
    PAUSED = 2
    GAMEOVER = 3

class ENEMYSTATES(Enum):
    IDLE = 0
    WALKING = 1
    ATTACKING = 2
    HURT = 3
    DEAD = 4