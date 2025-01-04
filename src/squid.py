import pygame
from actor import Actor
from constants import ENEMYSTATES

SPRITE_FRAME_SIZE = 16

class Squid(Actor):
    def __init__(self):
        super().__init__()

        self.health = 1

        self.current_state = ENEMYSTATES.WALKING
    
    # TODO Create and update where the squid simply walks left and right and turns around at walls
    # Should they care about ledges?

    # They can be taken out by being jumped on
    # They hurt the player if they run into their sides or they fall on the player (if they don't care about ledges)
    # Worth 100(?) points

    def load(self):
        self.sprite = pygame.image.load("../assets/sprites/enemy-squid-sheet.png")
        self.pos_rect = pygame.Rect(112, 80, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE) # TODO Make collision shape better fit to sprite
        
        for i in range(2):
            self.anim_frames.append(pygame.Rect(SPRITE_FRAME_SIZE * i, 0, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE)) # Walking
        
        self.anim_frames.append(pygame.Rect(0, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE, SPRITE_FRAME_SIZE))