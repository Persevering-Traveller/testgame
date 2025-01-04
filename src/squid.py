import pygame
from actor import Actor
from constants import ENEMYSTATES

SPRITE_FRAME_SIZE = 16

MAX_X_VELOCITY = 1.5

class Squid(Actor):
    def __init__(self):
        super().__init__()

        self.health = 1
        self.direction = -1 # Start move left (in direction of player)
        self.acceleration = 10.0
        
        self.anim_speed = 0.2 # TODO play with this value

        self.current_state = ENEMYSTATES.WALKING

    # They can be taken out by being jumped on
    # They hurt the player if they run into their sides or they fall on the player (if they don't care about ledges)
    # Worth 100(?) points

    def load(self):
        self.sprite = pygame.image.load("../assets/sprites/enemy-squid-sheet.png")
        self.pos_rect = pygame.Rect(112, 80, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE) # TODO Make collision shape better fit to sprite
        
        for i in range(2):
            self.anim_frames.append(pygame.Rect(SPRITE_FRAME_SIZE * i, 0, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Walking
        
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE))
    
    def update(self, dt):
        self.anim_counter += dt

        self.y_velocity += self.gravity * dt
        self.x_velocity += self.direction * self.acceleration * dt

        # Checks to see if they touch a wall...
        bump_into_wall = self.x_collision_check(self.x_velocity)
        self.y_collision_check(self.y_velocity)

        # ...And turns around if so
        # Undecided on whether they should turn back at a pitfall...
        if bump_into_wall:
            self.direction *= -1
            self.x_velocity = 0
        
        # Cap movement speed
        if abs(self.x_velocity) >= MAX_X_VELOCITY:
            self.x_velocity = MAX_X_VELOCITY * self.direction

    def draw(self, canvas):
        # TODO Do state-based drawing
        canvas.blit(self.sprite, (self.pos_rect.x, self.pos_rect.y), self.anim_frames[self.anim_index])

        if self.anim_counter >= self.anim_speed:
            self.anim_index = (self.anim_index + 1) % 2
            self.anim_counter = 0