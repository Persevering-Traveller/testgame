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
        self.jump_force = -250.0
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
        
        keys = pygame.key.get_pressed()

        match self.current_state:
            case PLAYERSTATES.IDLE:
                if keys[pygame.K_a]:
                    if self.is_grounded:
                        self.current_state = PLAYERSTATES.MOVING
                    self.direction = -1
                if keys[pygame.K_d]:
                    if self.is_grounded:
                        self.current_state = PLAYERSTATES.MOVING
                    self.direction = 1
                if keys[pygame.K_j]:
                    self.current_state = PLAYERSTATES.JUMPING
                    self.is_grounded = False
                    self.y_velocity += self.jump_force * dt
            case PLAYERSTATES.MOVING:
                if keys[pygame.K_a]:
                    self.direction = -1
                if keys[pygame.K_d]:
                    self.direction = 1
                if keys[pygame.K_j]:
                    self.current_state = PLAYERSTATES.JUMPING
                    self.is_grounded = False
                    self.y_velocity += self.jump_force * dt

                if not keys[pygame.K_a] and not keys[pygame.K_d]:
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
                if keys[pygame.K_a]:
                    self.direction = -1
                if keys[pygame.K_d]:
                    self.direction = 1
                
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
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

        # TODO Not sure if it's the gravity or if it's the non-stepped collision push back, but
        # jump height is very slightly variable. FIX
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

        self.pos_rect.move_ip(self.x_velocity, self.y_velocity)

        # Collision Checking
        # Checks the tiles left, right, top, and bottom of collision rect for collidable tiles
        # If one is found, collision flag will be true and used for collision reaction
        # collided_tiles is used to keep track of what indexes of surrounding tiles are the colliding tiles
        collision = False # TODO Do I need this variable or can I just use collided_tile?
        surrounding_tiles = [
            self.map_ref.get_tile_at(self.pos_rect.left, self.pos_rect.centery), # Left Tile; 0
            self.map_ref.get_tile_at(self.pos_rect.right, self.pos_rect.centery), # Right Tile; 1
            self.map_ref.get_tile_at(self.pos_rect.centerx, self.pos_rect.top), # Top Tile; 2
            self.map_ref.get_tile_at(self.pos_rect.centerx, self.pos_rect.bottom) # Bottom Tile; 3
        ]
        collided_tiles = []
        print(f"Position is: X: {self.pos_rect.centerx}, Y:{self.pos_rect.centery} -- Tile ids are: {surrounding_tiles}")
        for collision_index, tile_id in enumerate(surrounding_tiles):
            if tile_id in constants.COLLISION_TILES:
                collision = True
                collided_tiles.append(collision_index)

        # TODO The character seems to stop prematurely by a pixel or so, should implement checking by multiple tiny steps
        # Collision Reaction
        if collision:
            for col_tile in collided_tiles: # Iterate over the collection of indexes that are collided tiles
                if col_tile < 2: # Collision on Left or Right Tiles
                    if self.x_velocity > 0:
                        self.pos_rect.move_ip(-self.x_velocity, 0) # NOTE move_ip() does not function how I thought...
                    else:
                        self.pos_rect.move_ip(-self.x_velocity, 0) # NOTE because I thought I should positively move if heading to the left, but it's subtract?
                # TODO y collision checking has not been tested yet because jumping has not been implemented yet
                else: # Collision on Top or Bottom Tiles
                    if self.y_velocity > 0:
                        self.pos_rect.move_ip(0, -self.y_velocity) # NOTE I will keep these seperate untill I understand
                        self.is_grounded = True
                        self.y_velocity = 0
                    else:
                        self.pos_rect.move_ip(0, -self.y_velocity)
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