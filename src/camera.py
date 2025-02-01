import pygame

class Camera():
    def __init__(self):
        self.camera_target = None # What the camera will 'follow'
        self.level_entities_references = [] # All entities in the level, so it can shift them
        self.level_tiles_reference = None
        self.level_background_reference = None
    
    def set_camera_target(self, target):
        self.camera_target = target
    
    def add_level_entity(self, entity):
        self.level_entities_references.append(entity)
    
    def set_level_tiles(self, tiles):
        self.level_tiles_reference = tiles
    
    def set_background_ref(self, bg):
        self.level_background_reference = bg
    
    def update(self, dt):
        # This perfectly follows the player
        # TODO Consider making a sort of buffer zone that's slightly left and slightly right of center
        shift_amt = -self.camera_target.get_x_velocity()

        for tile in self.level_tiles_reference:
            tile.shift(shift_amt, 0)
        
        # Shift background slightly slower than level for pretend depth
        self.level_background_reference.shift(shift_amt/2, 0)

        for entity in self.level_entities_references:
            entity.shift(shift_amt, 0)