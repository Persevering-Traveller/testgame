import pygame
from enemy import Enemy
import constants

MAX_X_VELOCITY = 1.5

class Squid(Enemy):
    def __init__(self):
        super().__init__()

        self.sprite_offset = (2, 3)
        self.health = 1
        self.direction = -1 # Start move left (in direction of player)
        self.acceleration = 10.0
        self.sprite_frame_size = 16
        
        self.anim_speed = 0.2 # TODO play with this value
        self.collision_dimensions = (12, 11)

        self.squashed_point_val = 100 # TODO Make this a member on the Enemy class

        self.current_state = constants.ENEMYSTATES.WALKING

        self.player_ref_rect = None
        # Default 100 points for being stomped

    def load(self):
        self.sprite = pygame.image.load("../assets/sprites/enemy-squid-sheet.png")
        self.pos_rect = pygame.Rect(112, 80, self.collision_dimensions[0], self.collision_dimensions[1])
        self.world_pos = self.pos_rect.copy() # Initially, pos_rect of screen space is the same as world pos
        self.initial_world_pos = self.world_pos.copy()
        for i in range(2):
            self.anim_frames.append(pygame.Rect(self.sprite_frame_size * i, 0, self.sprite_frame_size, self.sprite_frame_size)) # Walking
        
        self.anim_frames.append(pygame.Rect(0, self.sprite_frame_size, self.sprite_frame_size, self.sprite_frame_size))
    
    def update(self, dt):
        match self.current_state:
            case constants.ENEMYSTATES.WALKING:
                self.anim_counter += dt

                self.facing = self.direction

                self.y_velocity += self.gravity * dt
                self.x_velocity += self.direction * self.acceleration * dt

                if self.stomp_check(): # From Enemy class
                    # TODO play death sound effect
                    return # Early return so x and y velocity aren't overwritten

                # Checks to see if they touch a wall or if there's a cliff...
                bump_into_wall = self.x_collision_check(self.x_velocity)
                self.y_collision_check(self.y_velocity)
                cliff_side = self.cliff_side_check()

                # ...And turns around if so
                if bump_into_wall or cliff_side:
                    self.direction *= -1
                    self.x_velocity = 0
                    # Need to push them one pixel or else they'll turn around but still
                    # see they're near a cliff side, making them freak out
                    self.world_pos.x += 1 * self.direction
                
                # Cap movement speed
                if abs(self.x_velocity) >= MAX_X_VELOCITY:
                    self.x_velocity = MAX_X_VELOCITY * self.direction
            case constants.ENEMYSTATES.DEAD:
                # Don't check for collisions, just fall off the screen
                self.pos_rect.move_ip(self.x_velocity, self.y_velocity)
                self.y_velocity += self.gravity * dt

    def draw(self, canvas):
        match self.current_state:
            case constants.ENEMYSTATES.WALKING:
                if self.anim_counter >= self.anim_speed:
                    self.anim_index = (self.anim_index + 1) % 2
                    self.anim_counter = 0
            case constants.ENEMYSTATES.DEAD:
                self.anim_index = 2

        # Actual blitting happens with the Actor's draw
        super().draw(canvas)
        # DEBUG
        #pygame.draw.rect(canvas, "red", self.pos_rect, 1)
    
    def reset(self):
        super().reset()
        self.health = 1
        self.direction = -1
        self.current_state = constants.ENEMYSTATES.WALKING
        self.pos_rect.x = 112
        self.pos_rect.y = 80