from enum import Enum
import pygame
import constants

class PLAYERSTATES(Enum):
    IDLE = 0
    MOVING = 1
    JUMPING = 2
    HURT = 3
    DIED = 4
    WIN = 5
    PAUSED = 6

COLLISION_WIDTH = 14
COLLISION_HEIGHT = 16
SPRITE_FRAME_SIZE = 32
SPRITE_OFFSET = 9 # The collision rect is 9x9 inwards on a frame
MAX_X_VELOCITY = 2.0
MAX_Y_VELOCITY = 2.0 # TODO play with and change these values (the velocity)
SUB_STEP_VELOCITY = 4

class Player():
    def __init__(self) -> None:
        self.sprite = None # Surface
        self.anim_frames = []
        self.anim_index = 0
        self.anim_speed = 0.1
        self.anim_counter = 0.0
        self.pos_rect = None # Rect ; position and collision rect
        self.map_ref = None # A reference to the map (game level) for collision checking

        self.health = 3
        self.direction = 0
        self.acceleration = 30.0
        self.deacceleration = 15.0
        self.gravity = 9.81
        self.jump_force = -4.0
        self.x_velocity = 0.0
        self.y_velocity = 0.0

        self.current_state = PLAYERSTATES.IDLE
        self.is_grounded = True
        self.facing = 1 # 1 for right, -1 for left

    def load(self):
        self.sprite = pygame.image.load("../assets/sprites/player-sheet.png").convert_alpha()
        self.pos_rect = pygame.Rect(80, 80, COLLISION_WIDTH, COLLISION_HEIGHT)

        self.anim_frames.append(pygame.Rect(0, 0, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Idle
        for i in range(3):
            self.anim_frames.append(pygame.Rect(SPRITE_FRAME_SIZE * i, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Moving
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE * 2, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Jumping
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE * 3, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Hurt and Dying
        print(self.anim_frames)

    def update(self, dt):
        self.anim_counter += dt # Needed here for animation

        last_dir = self.direction
        
        pressed_keys = pygame.key.get_pressed()
        just_p_keys = pygame.key.get_just_pressed()

        match self.current_state:
            case PLAYERSTATES.IDLE:
                if pressed_keys[pygame.K_a]:
                    if self.is_grounded:
                        self.current_state = PLAYERSTATES.MOVING
                    self.direction = -1
                if pressed_keys[pygame.K_d]:
                    if self.is_grounded:
                        self.current_state = PLAYERSTATES.MOVING
                    self.direction = 1
                if just_p_keys[pygame.K_j]:
                    self.current_state = PLAYERSTATES.JUMPING
                    self.is_grounded = False
                    self.y_velocity = self.jump_force
            case PLAYERSTATES.MOVING:
                if pressed_keys[pygame.K_a]:
                    self.direction = -1
                if pressed_keys[pygame.K_d]:
                    self.direction = 1
                if just_p_keys[pygame.K_j]:
                    self.current_state = PLAYERSTATES.JUMPING
                    self.is_grounded = False
                    self.y_velocity = self.jump_force

                if not pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:
                    # Don't change state back to idle until the player has reached 0 X velocity on the ground (or close to)
                    if self.is_grounded:
                        if abs(self.x_velocity) < 0.25: # TODO Play with this value some more
                            self.current_state = PLAYERSTATES.IDLE
                        else:
                            self.current_state = PLAYERSTATES.MOVING
                    self.direction = 0
                    last_dir = self.direction
                    if self.x_velocity != 0:
                        if self.x_velocity < 0:
                            self.x_velocity += self.deacceleration * dt
                        else:
                            self.x_velocity -= self.deacceleration * dt
            case PLAYERSTATES.JUMPING:
                if pressed_keys[pygame.K_a]:
                    self.direction = -1
                if pressed_keys[pygame.K_d]:
                    self.direction = 1
                
                if not pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:
                    self.direction = 0
                    last_dir = self.direction
                    if self.x_velocity != 0:
                        if self.x_velocity < 0:
                            self.x_velocity += self.deacceleration * dt
                        else:
                            self.x_velocity -= self.deacceleration * dt
                
                # Needs to be out of the not pressing left or right keys check or else we won't change state if still moving
                if self.is_grounded:
                    if abs(self.x_velocity) < 0.25: # TODO Play with this value some more
                        self.current_state = PLAYERSTATES.IDLE
                    else:
                        self.current_state = PLAYERSTATES.MOVING

        self.y_velocity += self.gravity * dt
        self.x_velocity += self.direction * self.acceleration * dt

        # For flipping the sprite if we're facing in another direction
        if last_dir != self.direction:
            if self.direction < 0: self.facing = -1
            else: self.facing = 1

        if self.x_velocity > 0:
            if self.x_velocity >= MAX_X_VELOCITY:
                self.x_velocity = MAX_X_VELOCITY
        else:
            if self.x_velocity <= -MAX_X_VELOCITY:
                self.x_velocity = -MAX_X_VELOCITY

        # The velocity of each direction (x&y) needs to be broken down into 1s. 
        # So if x velocity is like 2.3 or something, move the player 1 pixel at a time (2 steps in total) 
        # and check for collsions only in the x axis each step.
        # If y velocity is like 4.8, we step through it 1 pixel at a time (4 steps in total) and check for collisions only in the y axis
        # each step
        sub_x_vel_acc = int(self.x_velocity)
        sub_y_vel_acc = int(self.y_velocity)
        # X movement first
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
            #print(f"Position is: X: {self.pos_rect.centerx}, Y:{self.pos_rect.centery} -- Tile ids are: {surrounding_tiles}")
            for tile_id in surrounding_tiles:
                if tile_id in constants.COLLISION_TILES:
                    collision = True
            
            # X collision and reaction is working PERFECTLY!
            if collision:
                if sub_x_vel_acc > 0:
                    self.pos_rect.move_ip(-1, 0) # If heading right, push back left
                else:
                    self.pos_rect.move_ip(1, 0) # if heading left, push back right
        
        # Then Y movement
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


        # Screen Boundaries ; Temporary
        if self.pos_rect.x < 0: self.pos_rect.x = 0
        elif self.pos_rect.x + self.pos_rect.width > 160: self.pos_rect.x = 160 - self.pos_rect.width

        if self.pos_rect.y < -32: self.pos_rect.y = -32
        elif self.pos_rect.y + self.pos_rect.height > 144: self.pos_rect.y = 144 - self.pos_rect.height

    def draw(self, canvas: pygame.Surface):
        match self.current_state:
            case PLAYERSTATES.IDLE:
                self.anim_index = 0
                # For facing left, we need to get the subsurface image, flip only that image, then blit that image to the canvas
                if self.facing < 0:
                    frame_to_flip = self.sprite.subsurface(self.anim_frames[self.anim_index])
                    canvas.blit(pygame.transform.flip(frame_to_flip, True, False), (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET))
                else:
                    canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[self.anim_index].scale_by(1, 1))
            case PLAYERSTATES.MOVING:
                if self.anim_index < 1 or self.anim_index > 3: self.anim_index = 1 # The Starting frame for Moving animation
                if self.facing < 0:
                    frame_to_flip = self.sprite.subsurface(self.anim_frames[self.anim_index])
                    canvas.blit(pygame.transform.flip(frame_to_flip, True, False), (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET))
                else:
                    canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[self.anim_index])
                if self.anim_counter >= self.anim_speed:
                    self.anim_index += 1
                    self.anim_counter = 0.0
            case PLAYERSTATES.JUMPING:
                self.anim_index = 4
                if self.facing < 0:
                    frame_to_flip = self.sprite.subsurface(self.anim_frames[self.anim_index])
                    canvas.blit(pygame.transform.flip(frame_to_flip, True, False), (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET))
                else:
                    canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[self.anim_index])
            case PLAYERSTATES.HURT | PLAYERSTATES.DIED:
                self.anim_index = 5
                if self.facing < 0:
                    frame_to_flip = self.sprite.subsurface(self.anim_frames[self.anim_index])
                    canvas.blit(pygame.transform.flip(frame_to_flip, True, False), (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET))
                else:
                    canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[self.anim_index])
    
    def set_map_ref(self, map):
        if map != None:
            self.map_ref = map