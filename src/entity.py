# Base class for all things existing in the game
class Entity():
    def __init__(self):
        self.sprite = None # Main spritesheet surface
        self.sprite_offset = () # An x,y pair for drawing
        self.sprite_frame_size = 1 # The width and height of a frame
        self.anim_frames = []
        self.anim_index = 0
        self.anim_speed = 0.1
        self.anim_counter = 0.0
        self.pos_rect = None # pygame.Rect; Position and Collision Rect
        self.world_pos = None # pygame.Rect; Position in the "world" relative to how the camera has shifted

        self.awake = True # Used for when entity is not dead or off-screen
        self.current_state = 0 # To be overwritten in inherited class

    def get_pos_rect(self):
        return self.pos_rect

    def get_world_pos(self):
        return self.world_pos
    
    def set_world_pos(self, x, y):
        self.world_pos.x += x
        self.world_pos.y += y
    
    # This is a method meant to be used by the Camera object in order to "move the camera"
    # Though what's really happening is the world is shifting in the opposite direction of
    # the camera's focused entity's movement direction (Player goes ->, Shift world <-, 
    # and vice-versa)
    def shift(self, x, y):
        self.pos_rect.move_ip(x, y)
    
    def reset(self):
        self.anim_index = 0
        self.anim_counter = 0.0
        self.awake = True

    # Three main methods to be overwritten
    def load(self):
        pass

    def update(self, dt):
        pass

    def draw(self, canvas):
        pass