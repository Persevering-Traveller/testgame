import pygame

class Camera():
    def __init__(self):
        self.camera_target = None # What the camera will 'follow'
        self.level_entities_references = [] # All entities in the level, so it can shift them
        self.level_tiles_reference = None
        self.level_background_reference = None
        self.shift_amount = 0.0
        self.prev_target_pos_x = 0
    
    def set_camera_target(self, target):
        self.camera_target = target
        self.prev_target_pos_x = target.pos_rect.x
    
    def add_level_entity(self, entity):
        #print(f"World Pos at initial add: {entity.world_pos}")
        self.level_entities_references.append(entity)
    
    def set_level_tiles(self, tiles):
        self.level_tiles_reference = tiles
    
    def set_background_ref(self, bg):
        self.level_background_reference = bg
    
    def update(self, dt):
        # This perfectly follows the player
        # TODO Consider making a sort of buffer zone that's slightly left and slightly right of center
        self.shift_amount = -(self.camera_target.pos_rect.x - self.prev_target_pos_x)
        #print(f"Shift Amt: {self.shift_amount}")

        for tile in self.level_tiles_reference:
            tile.shift(self.shift_amount, 0)
        
        # Shift background slightly slower than level for pretend depth
        self.level_background_reference.shift(self.shift_amount/2, 0)

        for entity in self.level_entities_references:
            entity.shift(self.shift_amount, 0)
            entity.set_world_pos(-self.shift_amount, 0)
        
        self.prev_target_pos_x = self.camera_target.pos_rect.x