import pygame
import constants

class Actor():
    def __init__(self) -> None:
        self.sprite = None # Main spritesheet surface
        self.anim_frames = []
        self.anim_speed = 0.1
        self.anim_counter = 0.0
        self.pos_rect = None # pygame.Rect; Position and Collision Rect
        self.map_ref = None # A reference to the map (game level) for collision checking

        self.health = 1 # All actors should probably take at least one hit
        self.direction = 0
        self.acceleration = 30.0
        self.deacceleration = 15
        self.gravity = 9.81
        self.jump_force = 0.0 # Not all actors can jump
        self.x_velocity = 0.0
        self.y_velocity = 0.0

        self.current_state = 0 # To be overwritten in inherited class
        self.is_grounded = True # Needed for collision checking
        self.facing = 1 # 1 for right, -1 for left
    
    def set_map_ref(self, map):
        if map != None:
            self.map_ref = map
    
    # The velocity of each direction (x&y) needs to be broken down into 1s. 
    # So if x velocity is like 2.3 or something, move the player 1 pixel at a time (2 steps in total) 
    # and check for collsions only in the x axis each step.
    # If y velocity is like 4.8, we step through it 1 pixel at a time (4 steps in total) and check for collisions only in the y axis
    # each step
    def x_collision_check(self, velocity):
        sub_x_vel_acc = int(velocity)
        
        for i in range(abs(sub_x_vel_acc)): # NOTE Fun thing about python, you can give this for a negative number and uh....WATCH OUT
            if sub_x_vel_acc > 0: # Move them in the direction they were heading, right or left
                self.pos_rect.move_ip(1, 0)
            else:
                self.pos_rect.move_ip(-1, 0)

            # Checks the tiles left and right of collision rect at 3 points(Top, Center, and Bottom) for collidable tiles
            # If one is found, collision flag will be true and used for collision reaction
            collision = False
            surrounding_tiles = [
                self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.top), # Check Top-Left Tile
                self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.centery), # Check Center-Left Tile
                self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.bottom - 1), # Check Bottom-Left Tile 1 additional pixel above self
                self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.top), # Check Top-Right Tile
                self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.centery), # Check Center-Right Tile
                self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.bottom - 1), # Check Bottom-Right Tile 1 additional pixel above self
            ]
            
            for tile_id in surrounding_tiles:
                if tile_id in constants.COLLISION_TILES:
                    collision = True
            
            # X collision and reaction is working PERFECTLY!
            if collision:
                if sub_x_vel_acc > 0:
                    self.pos_rect.move_ip(-1, 0) # If heading right, push back left
                else:
                    self.pos_rect.move_ip(1, 0) # if heading left, push back right

    def y_collision_check(self, velocity):
        sub_y_vel_acc = int(velocity)
        
        for i in range(abs(sub_y_vel_acc)):
            if sub_y_vel_acc > 0: # Move one pixel in the direction they were heading: down or up
                self.pos_rect.move_ip(0, 1)
            else:
                self.pos_rect.move_ip(0, -1)

            # Checks the tiles above and below the collision rect at 3 points(Left, Center, and Right) for collidable tiles.
            # If one is found, collision flag will become true and used for collision reaction 
            collision = False
            surrounding_tiles = [
                self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.top), # Check Top-Left Tile
                self.map_ref.get_tile_at(self.pos_rect.centerx, self.pos_rect.top), # Check Top-Center Tile
                self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.top), # Check Top-Right Tile
                self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.bottom - 1), # Check Bottom-Left Tile 1 additional pixel above self
                self.map_ref.get_tile_at(self.pos_rect.centerx, self.pos_rect.bottom - 1), # Check Bottom-Center Tile 1 additional pixel above self
                self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.bottom - 1) # Check Bottom-Right Tile 1 additional pixel above self
            ]

            for tile_id in surrounding_tiles:
                if tile_id in constants.COLLISION_TILES:
                    collision = True
            
            if collision:
                if sub_y_vel_acc > 0:
                    self.pos_rect.move_ip(0, -1) # If moving down, and collision, push back up
                    self.is_grounded = True
                    self.y_velocity = 0
                else:
                    self.pos_rect.move_ip(0, 1) # if moving up, and collision, push back down
                    self.y_velocity = 0   
    
    # Three main functions to be overloaded
    def load(self):
        pass

    def update(self, dt):
        pass

    def draw(self, canvas: pygame.Surface):
        pass