import constants

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
        self.prev_target_pos_x = target.world_pos.x
    
    def add_level_entity(self, entity):
        #print(f"World Pos at initial add: {entity.world_pos}")
        self.level_entities_references.append(entity)
    
    def set_level_tiles(self, tiles):
        self.level_tiles_reference = tiles
    
    def set_background_ref(self, bg):
        self.level_background_reference = bg
    
    def update(self, dt):
        # Don't shift the camera if the player is at the edges of the level
        if (self.camera_target.world_pos.x - (constants.CANVAS_WIDTH//2) <= 0 or 
            self.camera_target.world_pos.x + (constants.CANVAS_WIDTH//2) >= 16 * constants.LEVEL_TILE_WIDTH): 
            return
        
        # This perfectly follows the player
        # TODO Consider making a sort of buffer zone that's slightly left and slightly right of center
        self.shift_amount = -(self.camera_target.world_pos.x - self.prev_target_pos_x)
        #print(f"Shift Amt: {self.shift_amount}")

        for tile in self.level_tiles_reference:
            tile.shift(self.shift_amount, 0)
        
        # Shift background slightly slower than level for pretend depth
        self.level_background_reference.shift(self.shift_amount/2, 0)

        for entity in self.level_entities_references:
            entity.shift(self.shift_amount, 0)
        
        self.prev_target_pos_x = self.camera_target.world_pos.x

        #print(f"ShiftAmt: {self.shift_amount} | PrvTrgtX: {self.prev_target_pos_x}")

    def reset(self):
        # Without resetting this back to the target's world_pos after target's reset,
        # the shift amount will be too large and the visuals won't sync with collisions
        self.prev_target_pos_x = self.camera_target.world_pos.x
        self.shift_amount = 0.0