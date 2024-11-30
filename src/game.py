import pygame
import pygame.freetype
import pygame.ftfont
from map import Map
from hud import HUD
from pickups import Pickup
from player import Player
import constants

LIFE_UP_COIN_AMT = 100
FONT_SIZE = 10

class Game():
    def __init__(self) -> None:
        pygame.init()
        
        self.window_size = 4
        # Screen has to come before canvas because Surface.convert() needs a window display first
        # That little 1 at the end is so essential. It's VSync.
        self.screen = pygame.display.set_mode((constants.CANVAS_WIDTH * self.window_size, constants.CANVAS_HEIGHT * self.window_size), 0, 0, 0, 1)
        self.canvas = pygame.Surface((constants.CANVAS_WIDTH, constants.CANVAS_HEIGHT)).convert()
        pygame.display.set_caption("Test Game")
        self.game_font = pygame.font.Font("../assets/fonts/game_font.ttf", FONT_SIZE) # NOTE I've tried other fonts, but they render poorly at 160x144 scale

        self.map = Map()
        self.hud = HUD()
        self.pickup = Pickup()
        self.player = Player()

        # Should this be on the player?
        self.score = 0
        self.lives = 3 # player lives
        self.coins = 0

        self.time = 999 # how much time per level to finish, just 999 for now

    def load(self) -> None:
        self.map.load()
        self.hud.set_font_ref(self.game_font) # Needs to come before load
        self.hud.load()
        self.pickup.load()
        self.player.load()
        self.player.set_map_ref(self.map)
    
    def update(self, dt) -> None:
         self.hud.update(dt)
         self.pickup.update(dt)
         self.player.update(dt)

    def draw(self) -> None:
        self.canvas.fill(pygame.color.Color(128, 128, 255)) # Good ol' Cornflower Blue!

        self.map.draw(self.canvas)
        self.pickup.draw(self.canvas)
        self.player.draw(self.canvas)

        self.hud.draw(self.canvas)
        # draw canvas to the screen scaled to the same size as the screen(window)
        self.screen.blit(pygame.transform.scale(self.canvas, self.screen.get_rect().size))

        pygame.display.flip()