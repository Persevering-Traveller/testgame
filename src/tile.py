import pygame
from src.entity import Entity
import src.constants as constants

class Tile(Entity):
    def __init__(self):
        super().__init__()
        self.tile_id = -1 # -1 means non-existant tile
        # Though tile is an entity, there's no reason to update its world position, 
        # because the tiles ARE the world
    
    def set_tile_id(self, id):
        self.tile_id = id
    
    def get_tile_id(self):
        return self.tile_id
    
    def set_draw_area(self, area):
        # All tiles will have only one draw area
        draw_area = pygame.Rect(area[0] * constants.TILE_SIZE, area[1] * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
        self.anim_frames.append(draw_area)
    
    def get_draw_area(self):
        return self.anim_frames[self.anim_index]
    
    def set_pos(self, pos):
        position = pygame.Rect(pos[0] * constants.TILE_SIZE, pos[1] * constants.TILE_SIZE, constants.TILE_SIZE, constants.TILE_SIZE)
        self.pos_rect = position.copy()
        self.initial_world_pos = position.copy()
    
    def reset(self):
        self.pos_rect = self.initial_world_pos.copy()