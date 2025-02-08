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
    
    def cliff_side_check(self):
        #print(self.world_pos.center)
        left_groundpoint = self.map_ref.get_tile_at(self.world_pos.left, self.world_pos.bottom)
        center_groundpoint = self.map_ref.get_tile_at(self.world_pos.centerx, self.world_pos.bottom)
        right_groundpoint = self.map_ref.get_tile_at(self.world_pos.right, self.world_pos.bottom)
        
        # Is there no collision tile on the left or right side of their feet
        return ((left_groundpoint == -1 and center_groundpoint != -1 and right_groundpoint != -1) or
                (right_groundpoint == -1 and left_groundpoint != -1 and center_groundpoint != -1))