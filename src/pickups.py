from enum import Enum
import pygame
from entity import Entity
import constants

SPRITE_SIZE = 16
ANIM_FRAME_COUNT = 4
ANIM_COLLECTED_FRAME_START = 3 # Technically the 4th frame, but the math starts by adding 1, so it still equals to 4

class PICKUPSTATE(Enum):
    IDLE = 0
    COLLECTED = 1

class Pickup(Entity):
    def __init__(self) -> None:
        super().__init__()
        self.player_ref = None

        self.current_state = PICKUPSTATE.IDLE
        self.point_val = 100

    def load(self):
        self.pos_rect = pygame.Rect(64, 56, SPRITE_SIZE, SPRITE_SIZE) # TODO load this in from some file actually, for now "center" screen
        self.world_pos = self.pos_rect.copy() # Initially, pos_rect of screen space is the same as world pos
        self.initial_world_pos = self.world_pos.copy()
        self.sprite = pygame.image.load("../assets/sprites/pickup-coin-sheet.png").convert_alpha()
        for i in range(8):
            self.anim_frames.append(pygame.Rect((i%ANIM_FRAME_COUNT)*SPRITE_SIZE, (i//ANIM_FRAME_COUNT)*SPRITE_SIZE, SPRITE_SIZE, SPRITE_SIZE))

    def update(self, dt):
        if(not self.awake): 
           return
        
        # Have to check current state or anim_index will set back to collected start frame while still colliding
        if self.player_ref.awake:
            if self.pos_rect.colliderect(self.player_ref.pos_rect) and self.current_state != PICKUPSTATE.COLLECTED:
                self.current_state = PICKUPSTATE.COLLECTED
                self.anim_index = ANIM_COLLECTED_FRAME_START
                self.anim_counter = self.anim_speed # Make it so that it will immediately change animation on collected
                pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.PICKUP_COLLECTED))

        self.anim_counter += dt
        if self.anim_counter >= self.anim_speed:
            if self.current_state == PICKUPSTATE.IDLE:
                self.anim_index = (self.anim_index + 1) % ANIM_FRAME_COUNT
            else:
                # MATH BE KUH-RAZZZZEEEEEEEEEE Y'ALLLLLLL
                # All that fuss and I forgot this animation isn't supposed to loop..... lol
                if self.anim_index != 7:
                    self.anim_index += 1
                    #self.anim_index = ((self.anim_index + 1) % ANIM_FRAME_COUNT) + ANIM_COLLECTED_FRAME_START
                else:
                    self.awake = False
            self.anim_counter = 0

    def draw(self, canvas):
        if(not self.awake):
            return
        canvas.blit(self.sprite, self.pos_rect, self.anim_frames[self.anim_index])
    
    def set_player_ref(self, player):
        self.player_ref = player
    
    def reset(self):
        super().reset()
        self.current_state = PICKUPSTATE.IDLE
        self.pos_rect.x = 64
        self.pos_rect.y = 56