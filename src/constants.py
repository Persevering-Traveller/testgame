from enum import Enum
import pygame

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