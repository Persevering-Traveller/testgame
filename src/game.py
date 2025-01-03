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
TEXT_X = 70
TEXT_PLAY_Y = 95
TEXT_QUIT_Y = 105
TITLE_CURSOR_X = TEXT_X - 10

class Game():
    def __init__(self) -> None:
        pygame.init()

        self.state = constants.GAMESTATE.TITLE
        
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

        self.title_logo_surf = None
        self.title_cursor_surf = None
        self.title_cursor_locations = []
        self.title_cursor_selection = 0
        self.title_play_text_surf = None
        self.title_quit_text_surf = None

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

        self.title_play_text_surf = self.game_font.render("Play", False, "white")
        self.title_quit_text_surf = self.game_font.render("Quit", False, "white")
        self.title_cursor_locations.append(pygame.Rect(TITLE_CURSOR_X, TEXT_PLAY_Y, 8, 8))
        self.title_cursor_locations.append(pygame.Rect(TITLE_CURSOR_X, TEXT_QUIT_Y, 8, 8))
        #self.title_cursor_surf = pygame.image.load().convert()
        self.title_cursor_surf = self.game_font.render(">", False, "white")
    
    def update(self, dt) -> None:
         match self.state:
            case constants.GAMESTATE.TITLE:
                keys = pygame.key.get_just_pressed()

                if keys[pygame.K_w]:
                    # Move selection cursor up
                    self.title_cursor_selection = abs((self.title_cursor_selection - 1) % len(self.title_cursor_locations))
                if keys[pygame.K_s]:
                    # Move selection cursor down
                    self.title_cursor_selection = (self.title_cursor_selection + 1) % len(self.title_cursor_locations)
                if keys[pygame.K_RETURN] or keys[pygame.K_j]:
                    # Read selection and change state/quit accordingly
                    if self.title_cursor_selection == 0:
                        self.state = constants.GAMESTATE.GAMEPLAY
                    else:
                        # Will be captured by main's checking for QUIT
                        pygame.event.post(pygame.Event(pygame.QUIT)) # I find it a little silly that I have to turn this known constant into a proper pygame Event
            case constants.GAMESTATE.GAMEPLAY:
                self.hud.update_time(self.time)
                self.pickup.update(dt)
                self.player.update(dt)
                self.time -= dt
                #TODO if self.time <= 0: change state to GAMEOVER
            # TODO PAUSE state should just handle unpausing and exiting the game
            # TODO GAMEOVER state shouldn't have any controls, just have a timer and then go back to TITLE state

    def draw(self) -> None:
        match self.state:
            case constants.GAMESTATE.TITLE:
                self.canvas.fill(pygame.color.Color(0, 0, 0)) # Background -- Black

                self.canvas.blit(self.title_play_text_surf, (TEXT_X, TEXT_PLAY_Y))
                self.canvas.blit(self.title_quit_text_surf, (TEXT_X, TEXT_QUIT_Y))
                self.canvas.blit(self.title_cursor_surf, self.title_cursor_locations[self.title_cursor_selection])
                
            case constants.GAMESTATE.GAMEPLAY:
                self.canvas.fill(pygame.color.Color(128, 128, 255)) # Good ol' Cornflower Blue!

                self.map.draw(self.canvas)
                self.pickup.draw(self.canvas)
                self.player.draw(self.canvas)

                self.hud.draw(self.canvas)
                
            # TODO PAUSE state should draw the pause screen (just dim it and write 'paused')
            # TODO GAMEOVER state should draw Game Over screen stuff

        # draw canvas to the screen scaled to the same size as the screen(window)
        self.screen.blit(pygame.transform.scale(self.canvas, self.screen.get_rect().size))
        
        pygame.display.flip()