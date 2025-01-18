import pygame
import constants
from actor import Actor

class Enemy(Actor):
    def __init__(self):
        super().__init__()

        self.stomped_point_val = 100 # default

        self.player_ref_rect = None
    
    def set_player_ref(self, player_rect):
        self.player_ref_rect = player_rect
    
    def stomp_check(self):
        overlapping_side = self.get_overlapping_side(self.player_ref_rect)
        if overlapping_side == constants.COLLISIONSIDE.TOP:
            self.y_velocity = self.pushback_force_y
            self.x_velocity = -self.direction * self.pushback_force_x
            self.health -= 1
            if self.health <= 0:
                pygame.event.post(pygame.Event(constants.CUSTOMEVENTS.ENEMY_STOMPED))
                self.awake = False
                self.current_state = constants.ENEMYSTATES.DEAD
            else:
                self.current_state = constants.ENEMYSTATES.HURT
            return True
        else:
            return False