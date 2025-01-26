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
        # TODO this should shift entities relative to the focused entity's position
        for tile in self.level_tiles_reference:
            tile.shift(-1, 0)

        for entity in self.level_entities_references:
            entity.shift(-1, 0)