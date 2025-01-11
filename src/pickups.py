import pygame

SPRITE_SIZE = 16
ANIM_FRAME_COUNT = 4
ANIM_COLLECTED_FRAME_START = 3 # Technically the 4th frame, but the math starts by adding 1, so it still equals to 4

# You know, it's a good question -> Does the player test to see if it collides with the coin
# or does the coin test to see if it collided with the player?
# TODO Add a method to give pos_rect so you can test if the player collides with it
# TODO Add a method to give point_val

class Pickup():
    def __init__(self) -> None:
        self.pos_rect = None # Rect -- It's collision shape and location
        self.player_rect_ref = None

        self.sprite = None # Surface
        self.anim_frames = []
        self.anim_index = 0
        self.anim_speed = 0.1 # Seconds or 1 Millisecond
        self.anim_counter = 0 # Used to count frames

        self.awake = True # same as actor awake
        self.collected = False
        self.point_val = 100

    def load(self):
        self.pos_rect = pygame.Rect(64, 56, SPRITE_SIZE, SPRITE_SIZE) # TODO load this in from some file actually, for now "center" screen
        self.sprite = pygame.image.load("../assets/sprites/pickup-coin-sheet.png").convert_alpha()
        for i in range(4):
            self.anim_frames.append(pygame.Rect(i*SPRITE_SIZE, 0, SPRITE_SIZE, SPRITE_SIZE))

    def update(self, dt):
        if(not self.awake): 
           return
        
        if self.pos_rect.colliderect(self.player_rect_ref):
            self.awake = False

        self.anim_counter += dt
        if self.anim_counter >= self.anim_speed:
            if not self.collected:
                self.anim_index = (self.anim_index + 1) % ANIM_FRAME_COUNT
            else:
                # MATH BE KUH-RAZZZZEEEEEEEEEE Y'ALLLLLLL
                # All that fuss and I forgot this animation isn't supposed to loop..... lol
                if self.anim_index != 7:
                    self.anim_index += 1
                    #self.anim_index = ((self.anim_index + 1) % ANIM_FRAME_COUNT) + ANIM_COLLECTED_FRAME_START
            self.anim_counter = 0

    def draw(self, canvas):
        if(not self.awake):
            return
        canvas.blit(self.sprite, self.pos_rect, self.anim_frames[self.anim_index])
    
    def set_player_ref(self, player):
        self.player_rect_ref = player