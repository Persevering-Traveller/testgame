from enum import Enum
import pygame
import constants
from actor import Actor

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

class Player(Actor):
    def __init__(self) -> None:
        super().__init__()

        self.health = 3

        self.jump_force = -4.0

        self.current_state = PLAYERSTATES.IDLE

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
                self.move_left_right(pressed_keys)
                self.jump(just_p_keys)
            case PLAYERSTATES.MOVING:
                self.move_left_right(pressed_keys)
                self.jump(just_p_keys)
                last_dir = self.deaccelerate_left_right(pressed_keys, dt)
            case PLAYERSTATES.JUMPING:
                self.move_left_right(pressed_keys)
                last_dir = self.deaccelerate_jumping(pressed_keys, dt)

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
        
        self.x_collision_check(self.x_velocity)
        self.y_collision_check(self.y_velocity)

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
                    canvas.blit(self.sprite, (self.pos_rect.x - SPRITE_OFFSET, self.pos_rect.y - SPRITE_OFFSET), self.anim_frames[self.anim_index])
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
            

    def move_left_right(self, pressed_keys):
        if pressed_keys[pygame.K_a]:
            if self.is_grounded and self.current_state != PLAYERSTATES.JUMPING:
                self.current_state = PLAYERSTATES.MOVING
            self.direction = -1
        if pressed_keys[pygame.K_d]:
            if self.is_grounded and self.current_state != PLAYERSTATES.JUMPING:
                self.current_state = PLAYERSTATES.MOVING
            self.direction = 1

    def jump(self, just_pressed_keys):
        if just_pressed_keys[pygame.K_j]:
                self.current_state = PLAYERSTATES.JUMPING
                self.is_grounded = False
                self.y_velocity = self.jump_force
    
    def deaccelerate_left_right(self, pressed_keys, dt):
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
            # Needed or the player will stop and face right when running on ground
            return last_dir
    
    def deaccelerate_jumping(self, pressed_keys, dt):
        # Needs to be out of the not pressing left or right keys check or else we won't change state if still moving
        if self.is_grounded:
            if abs(self.x_velocity) < 0.25: # TODO Play with this value some more
                self.current_state = PLAYERSTATES.IDLE
            else:
                self.current_state = PLAYERSTATES.MOVING

        if not pressed_keys[pygame.K_a] and not pressed_keys[pygame.K_d]:
            self.direction = 0
            last_dir = self.direction
            if self.x_velocity != 0:
                if self.x_velocity < 0:
                    self.x_velocity += self.deacceleration * dt
                else:
                    self.x_velocity -= self.deacceleration * dt
            return last_dir
                
        