from enum import Enum
import pygame

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
COLLISION_TILES = [39, 40, 41, 50, 52, 53] # The tile ID of each collidable tile in Tiled

class Player():
    def __init__(self) -> None:
        self.sprite = None # Surface
        self.anim_frames = []
        self.anim_index = 0
        self.pos_rect = None # Rect ; position and collision rect
        self.map_ref = None # A reference to the map (game level) for collision checking

        self.health = 3
        self.direction = 0
        self.acceleration = 30.0
        self.deacceleration = 15.0
        self.gravity = 9.81
        self.jump_force = 10.0
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
            self.anim_frames.append(pygame.Rect(SPRITE_FRAME_SIZE * i, SPRITE_FRAME_SIZE * 2, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Moving
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE * 3, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Jumping
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE * 4, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Hurt and Dying

    def update(self, dt):
        keys = pygame.key.get_pressed()

        match self.current_state:
            case PLAYERSTATES.IDLE:
                if keys[pygame.K_a]:
                    if self.is_grounded:
                        #self.current_state = PLAYERSTATES.MOVING
                        pass
            
                    self.direction = -1
                if keys[pygame.K_d]:
                    if self.is_grounded:
                        #self.current_state = PLAYERSTATES.MOVING
                        pass
                    self.direction = 1
                # TODO This should be moved to MOVING state when set up
                if not keys[pygame.K_a] and not keys[pygame.K_d]:
                    # TODO Don't change state back to idle until the player has reached 0 X velocity on the ground (or close to)
                    self.direction = 0
                    if self.x_velocity != 0:
                        if self.x_velocity < 0:
                            self.x_velocity += self.deacceleration * dt
                            pass
                        else:
                            self.x_velocity -= self.deacceleration * dt
        # TODO check for jumping and running and hitting escape to pause

        self.x_velocity += self.direction * self.acceleration * dt

        if self.x_velocity > 0:
            if self.x_velocity >= MAX_X_VELOCITY:
                self.x_velocity = MAX_X_VELOCITY
        else:
            if self.x_velocity <= -MAX_X_VELOCITY:
                self.x_velocity = -MAX_X_VELOCITY

        self.pos_rect.move_ip(self.x_velocity, self.y_velocity)

        # TODO Collision checking
        # Currently only checks from the top left of our collision rect if we're i n a collidable tile
        # Should probably start checking the tiles left, right, top, and bottom of collision rect
        tile_id = self.map_ref.get_tile_at(self.pos_rect.x, self.pos_rect.y)
        print(f"Position is: X: {self.pos_rect.x}, Y:{self.pos_rect.y} -- Tile id is: {tile_id}")
        if tile_id in COLLISION_TILES:
            if self.x_velocity > 0:
                self.pos_rect.move_ip(-self.x_velocity, 0)
            else:
                self.pos_rect.move_ip(self.x_velocity, 0)

        # Screen Boundaries ; Temporary
        if self.pos_rect.x < 0: self.pos_rect.x = 0
        elif self.pos_rect.x + self.pos_rect.width > 160: self.pos_rect.x = 160 - self.pos_rect.width

    def draw(self, canvas):
        match self.current_state:
            case PLAYERSTATES.IDLE:
                canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[0])
    
    def set_map_ref(self, map):
        if map != None:
            self.map_ref = map