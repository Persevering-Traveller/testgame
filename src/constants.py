from enum import Enum

CANVAS_WIDTH = 160
CANVAS_HEIGHT = 144
TILE_SIZE = 16

class GAMESTATE(Enum):
    TITLE = 0
    GAMEPLAY = 1
    PAUSED = 2
    GAMEOVER = 3