import pygame

class Camera():
    def __init__(self):
        self.focused_entity = None # What the camera will 'follow'
        self.level_entities_references = [] # All entities in the level, so it can shift them
        self.level_tiles_reference = None
    
    def set_focus(self, entity):
        self.focused_entity = entity
    
    def add_level_entity(self, entity):
        self.level_entities_references.append(entity)
    
    def set_level_tiles(self, tiles):
        self.level_tiles_reference = tiles
    
    def update(self, dt):
        # This perfectly follows the player
        # TODO Consider making a sort of buffer zone that's slightly left and slightly right of center
        shift_amt = -self.focused_entity.get_x_velocity()

        for tile in self.level_tiles_reference:
            tile.shift(shift_amt, 0)

        for entity in self.level_entities_references:
            entity.shift(shift_amt, 0)