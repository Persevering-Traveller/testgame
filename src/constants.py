from enum import Enum
import pygame
from src.manager_timer import TimerManager
from src.manager_sound import SoundManager

CANVAS_WIDTH = 160
CANVAS_HEIGHT = 144
TILE_SIZE = 16
LEVEL_TILE_WIDTH = 60

 # The tile ID of each collidable tile in Tiled
COLLISION_TILES = [39, 40, 41, # Single Row Grass tiles
                   50, 51, # Brown Brick, Large and Small tiles
                   52, 53, 54, 65, 67, 78, 79, 80, # 3x3 Grass tiles
                   68, # Single Grass tile
                   81, 94] # Single Column Grass tiles

# The tile IDs used for each entity's position and the end of level position
# Yes, it's just the Winter Tree tiles, I got lazy lol
PLAYER_POSITION = 4
ENEMY_POSITION = 5
PICKUP_POSITION = 6
END_POSITION = 31

# TODO Setup the one-way collision tile
#COLLISION_ONE_WAY_TILE = 42

TIMER_MANAGER = TimerManager() # Only one timer manager and should be accessible to all enemies and player (or anything else)
SOUND_MANAGER = SoundManager() # Only one sound manager

class GAMESTATE(Enum):
    TITLE = 0
    GAMEPLAY = 1
    PAUSED = 2
    GAMEOVER = 3
    RESET = 4
    WON = 5

class ENEMYSTATES(Enum):
    IDLE = 0
    WALKING = 1
    ATTACKING = 2
    HURT = 3
    DEAD = 4

class CUSTOMEVENTS():
    PICKUP_COLLECTED = pygame.event.custom_type()
    ENEMY_STOMPED = pygame.event.custom_type()
    PLAYER_HURT = pygame.event.custom_type()
    PLAYER_DIED = pygame.event.custom_type()
    PLAYER_REACH_GOAL = pygame.event.custom_type()
    TIMER_ENDED = pygame.event.custom_type()

class COLLISIONSIDE(Enum):
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3

class SOUNDFX(Enum):
    CONFIRM = 0
    GAMEOVER = 1
    END = 2
    HIT = 3
    JUMP = 4
    DIED = 5
    CURSOR = 6
    COIN = 7

class MUSIC(Enum):
    MAIN_MENU = 0
    LEVEL = 1