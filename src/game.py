import pygame
from map import Map
from hud import HUD
from pickups import Pickup
from player import Player
from squid import Squid
import constants

LIFE_UP_COIN_AMT = 10000
FONT_SIZE = 10
TEXT_X = 70
TEXT_PLAY_Y = 95
TEXT_QUIT_Y = 105
TITLE_CURSOR_X = TEXT_X - 10
PAUSE_SURF_WIDTH = 81
PAUSE_SURF_HEIGHT = 20
PAUSE_X = 41
PAUSE_Y = 68
PAUSE_TEXT_PADDING = 5

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
        self.enemy = Squid()

        self.title_logo_surf = None
        self.title_cursor_surf = None
        self.title_cursor_locations = []
        self.title_cursor_selection = 0
        self.title_play_text_surf = None
        self.title_quit_text_surf = None

        self.pause_surf = None
        self.pause_text = None

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
        self.enemy.load()
        self.player.set_map_ref(self.map)
        self.enemy.set_map_ref(self.map)
        self.pickup.set_player_ref(self.player)
        self.enemy.set_player_ref(self.player)
        self.player.enemy_ref = self.enemy # TODO delete this after setting up Enemy Manager

        self.title_play_text_surf = self.game_font.render("Play", False, "white")
        self.title_quit_text_surf = self.game_font.render("Quit", False, "white")
        self.title_cursor_locations.append(pygame.Rect(TITLE_CURSOR_X, TEXT_PLAY_Y, 8, 8))
        self.title_cursor_locations.append(pygame.Rect(TITLE_CURSOR_X, TEXT_QUIT_Y, 8, 8))
        #self.title_cursor_surf = pygame.image.load().convert()
        self.title_cursor_surf = self.game_font.render(">", False, "white")

        self.pause_surf = pygame.Surface((PAUSE_SURF_WIDTH, PAUSE_SURF_HEIGHT)).convert()
        self.pause_surf.fill("black")
        self.pause_text = self.game_font.render("[ P A U S E D ]", False, "white")
        self.pause_surf.blit(self.pause_text, (PAUSE_TEXT_PADDING, PAUSE_TEXT_PADDING))
    
    def update(self, dt) -> None:
        keys = pygame.key.get_just_pressed()
        match self.state:
            case constants.GAMESTATE.TITLE:
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
                if keys[pygame.K_ESCAPE]:
                    self.state = constants.GAMESTATE.PAUSED
                self.hud.update_time(self.time)
                self.pickup.update(dt)
                self.player.update(dt)
                self.enemy.update(dt)
                constants.TIMER_MANAGER.update(dt)
                self.time -= dt
                #TODO if self.time <= 0: change state to GAMEOVER

                for event in pygame.event.get([constants.CUSTOMEVENTS.PICKUP_COLLECTED, 
                                               constants.CUSTOMEVENTS.ENEMY_STOMPED,
                                               constants.CUSTOMEVENTS.PLAYER_HURT,
                                               constants.CUSTOMEVENTS.PLAYER_DIED,
                                               constants.CUSTOMEVENTS.PLAYER_REACH_GOAL]):
                    if event.type == constants.CUSTOMEVENTS.PICKUP_COLLECTED:
                        self.score += self.pickup.point_val
                        self.coins += 1
                        self.hud.update_score(self.score)
                        if self.coins == 100:
                            self.coins = 0
                            self.lives += 1
                            self.hud.update_lives(self.lives)
                        self.hud.update_coins(self.coins)
                        self.check_life_up()
                    if event.type == constants.CUSTOMEVENTS.ENEMY_STOMPED:
                        self.score += self.enemy.squashed_point_val
                        self.hud.update_score(self.score)
                        self.check_life_up()
                    if event.type == constants.CUSTOMEVENTS.PLAYER_HURT or event.type == constants.CUSTOMEVENTS.PLAYER_DIED:
                        self.hud.update_health(self.player.health)
                    if event.type == constants.CUSTOMEVENTS.PLAYER_DIED:
                        self.lives -= 1
                        self.hud.update_lives(self.lives)
            case constants.GAMESTATE.PAUSED:
                if keys[pygame.K_ESCAPE]:
                    self.state = constants.GAMESTATE.GAMEPLAY
                if keys[pygame.K_RETURN]:
                    pygame.event.post(pygame.Event(pygame.QUIT))
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
                self.enemy.draw(self.canvas)

                self.hud.draw(self.canvas)
            
            case constants.GAMESTATE.PAUSED:
                self.canvas.blit(self.pause_surf, (PAUSE_X, PAUSE_Y))
                
            # TODO GAMEOVER state should draw Game Over screen stuff

        # draw canvas to the screen scaled to the same size as the screen(window)
        self.screen.blit(pygame.transform.scale(self.canvas, self.screen.get_rect().size))
        
        pygame.display.flip()
    
    def check_life_up(self):
        if self.score % LIFE_UP_COIN_AMT == 0:
            self.lives += 1
            self.hud.update_lives()
