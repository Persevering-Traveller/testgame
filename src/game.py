import pygame
from map import Map
from hud import HUD
from pickups import Pickup
from player import Player
from squid import Squid
from camera import Camera
import constants

LEVEL_TIME = 9
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
RESET_TEXT_X = 64
RESET_TEXT_Y = 80
RESET_ICON_X = RESET_TEXT_X - 6
RESET_ICON_Y = RESET_TEXT_Y - 16

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
        self.pickups = []
        self.player = Player()
        self.enemies = []
        self.camera = Camera()

        self.title_logo_surf = None
        self.title_cursor_surf = None
        self.title_cursor_locations = []
        self.title_cursor_selection = 0
        self.title_play_text_surf = None
        self.title_quit_text_surf = None

        self.pause_surf = None
        self.pause_text = None

        self.reset_icons = []
        self.reset_icons_start_loc = None
        self.reset_text_surf = None
        self.reset_text_location = None

        # Should this be on the player?
        self.score = 0
        self.lives = 3 # player lives
        self.coins = 0

        self.time = LEVEL_TIME # how much time per level to finish, just 999 for now

        self.reset_timer = constants.TIMER_MANAGER.new_timer(2)

    def load(self) -> None:
        self.map.load()
        self.hud.set_font_ref(self.game_font) # Needs to come before load
        self.hud.load()
        for pickup in self.map.get_pickup_positions():
            new_pickup = Pickup()
            new_pickup.load(pickup.x, pickup.y)
            self.pickups.append(new_pickup)

        self.player.load(self.map.get_player_start_pos().x,self.map.get_player_start_pos().y)

        for enemy in self.map.get_enemy_positions():
            new_enemy = Squid()
            new_enemy.load(enemy.x, enemy.y)
            self.enemies.append(new_enemy)
        
        # Set references
        self.player.set_map_ref(self.map)
        for enemy in self.enemies:
            enemy.set_map_ref(self.map)
            enemy.set_player_ref(self.player)
        for pickup in self.pickups:
            pickup.set_player_ref(self.player)

        self.player.enemy_refs = self.enemies # TODO delete this after setting up Enemy Manager
        constants.SOUND_MANAGER.load()

        self.camera.set_level_tiles(self.map.get_level_data())
        self.camera.set_background_ref(self.map.get_level_bg())
        for pickup in self.pickups:
            self.camera.add_level_entity(pickup)
        self.camera.add_level_entity(self.player)
        for enemy in self.enemies:
            self.camera.add_level_entity(enemy)
        self.camera.set_camera_target(self.player)

        self.title_logo_surf = pygame.image.load("../assets/sprites/main-menu-bg.png").convert()
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

        self.reset_text_surf = self.game_font.render("Ready?", False, "white")
        self.reset_text_location = pygame.Rect(RESET_TEXT_X, RESET_TEXT_Y, 1, 1)
        self.reset_icons_start_loc = pygame.Rect(RESET_ICON_X, RESET_ICON_Y, 1, 1)
        # TODO This is very hack-y, try to find a better way to do this
        self.reset_icons = [self.hud.player_icons[0],
                            self.hud.player_icons[2]]
    
    def update(self, dt) -> None:
        constants.TIMER_MANAGER.update(dt)
        keys = pygame.key.get_just_pressed()
        match self.state:
            case constants.GAMESTATE.TITLE:
                constants.SOUND_MANAGER.play_music(constants.MUSIC.MAIN_MENU)

                if keys[pygame.K_w]:
                    # Move selection cursor up
                    self.title_cursor_selection = abs((self.title_cursor_selection - 1) % len(self.title_cursor_locations))
                    constants.SOUND_MANAGER.play_sfx(constants.SOUNDFX.CURSOR)
                if keys[pygame.K_s]:
                    # Move selection cursor down
                    self.title_cursor_selection = (self.title_cursor_selection + 1) % len(self.title_cursor_locations)
                    constants.SOUND_MANAGER.play_sfx(constants.SOUNDFX.CURSOR)
                if keys[pygame.K_RETURN] or keys[pygame.K_j]:
                    # Read selection and change state/quit accordingly
                    constants.SOUND_MANAGER.play_sfx(constants.SOUNDFX.CONFIRM)
                    if self.title_cursor_selection == 0:
                        constants.SOUND_MANAGER.stop_music()
                        self.state = constants.GAMESTATE.GAMEPLAY
                    else:
                        # Will be captured by main's checking for QUIT
                        pygame.event.post(pygame.Event(pygame.QUIT)) # I find it a little silly that I have to turn this known constant into a proper pygame Event
            case constants.GAMESTATE.GAMEPLAY:
                constants.SOUND_MANAGER.play_music(constants.MUSIC.LEVEL)

                if keys[pygame.K_ESCAPE]:
                    constants.SOUND_MANAGER.pause_music()
                    self.state = constants.GAMESTATE.PAUSED
                
                self.hud.update_time(self.time)
                for pickup in self.pickups:
                    pickup.update(dt)
                self.player.update(dt)
                for enemy in self.enemies:
                    enemy.update(dt)
                self.camera.update(dt)
                self.time -= dt
                # Player dies on time out
                if self.time <= 1:
                    self.time = 0
                    self.player.die()

                for event in pygame.event.get([constants.CUSTOMEVENTS.PICKUP_COLLECTED, 
                                               constants.CUSTOMEVENTS.ENEMY_STOMPED,
                                               constants.CUSTOMEVENTS.PLAYER_HURT,
                                               constants.CUSTOMEVENTS.PLAYER_DIED,
                                               constants.CUSTOMEVENTS.PLAYER_REACH_GOAL]):
                    if event.type == constants.CUSTOMEVENTS.PICKUP_COLLECTED:
                        point_value = self.pickups[0].point_val # The point value of every coin is the same
                        self.score += point_value
                        self.coins += 1
                        self.hud.update_score(self.score)
                        if self.coins == 100:
                            self.coins = 0
                            self.lives += 1
                            self.hud.update_lives(self.lives)
                        self.hud.update_coins(self.coins)
                        self.check_life_up()
                    if event.type == constants.CUSTOMEVENTS.ENEMY_STOMPED:
                        squashed_enemy_points = self.enemies[0].squashed_point_val # Point value is the same for all enemies
                        self.score += squashed_enemy_points
                        self.hud.update_score(self.score)
                        self.check_life_up()
                    if event.type == constants.CUSTOMEVENTS.PLAYER_HURT:
                        self.hud.update_health(self.player.health)
                    if event.type == constants.CUSTOMEVENTS.PLAYER_DIED:
                        self.lives -= 1
                        self.hud.update_lives(self.lives)
                        constants.TIMER_MANAGER.start_timer(self.reset_timer)
                        constants.SOUND_MANAGER.stop_music()
                        self.state = constants.GAMESTATE.RESET
            case constants.GAMESTATE.PAUSED:
                if keys[pygame.K_ESCAPE]:
                    constants.SOUND_MANAGER.play_music(constants.MUSIC.LEVEL)
                    self.state = constants.GAMESTATE.GAMEPLAY
                if keys[pygame.K_RETURN]:
                    pygame.event.post(pygame.Event(pygame.QUIT))
            # TODO GAMEOVER state shouldn't have any controls, just have a timer and then go back to TITLE state
            case constants.GAMESTATE.GAMEOVER:
                pass
            case constants.GAMESTATE.RESET:
                for event in pygame.event.get(constants.CUSTOMEVENTS.TIMER_ENDED):
                    if event.type == constants.CUSTOMEVENTS.TIMER_ENDED:
                        if event.dict["id"] == self.reset_timer:
                            self.reset()
                            self.hud.update_health(self.player.health)
                            self.state = constants.GAMESTATE.GAMEPLAY

    def draw(self) -> None:
        match self.state:
            case constants.GAMESTATE.TITLE:
                self.canvas.fill(pygame.color.Color(0, 0, 0)) # Background -- Black

                self.canvas.blit(self.title_logo_surf, (0, 0))
                self.canvas.blit(self.title_play_text_surf, (TEXT_X, TEXT_PLAY_Y))
                self.canvas.blit(self.title_quit_text_surf, (TEXT_X, TEXT_QUIT_Y))
                self.canvas.blit(self.title_cursor_surf, self.title_cursor_locations[self.title_cursor_selection])
                
            case constants.GAMESTATE.GAMEPLAY:
                self.canvas.fill(pygame.color.Color(128, 128, 255)) # Good ol' Cornflower Blue!

                self.map.draw(self.canvas)
                for pickup in self.pickups:
                    pickup.draw(self.canvas)
                self.player.draw(self.canvas)
                for enemy in self.enemies:
                    enemy.draw(self.canvas)

                self.hud.draw(self.canvas)
            
            case constants.GAMESTATE.PAUSED:
                self.canvas.blit(self.pause_surf, (PAUSE_X, PAUSE_Y))
                
            # TODO GAMEOVER state should draw Game Over screen stuff
            case constants.GAMESTATE.GAMEOVER:
                pass

            case constants.GAMESTATE.RESET:
                self.canvas.fill(pygame.Color(0, 0, 0))
                i = 0
                while i < len(self.reset_icons):
                    self.canvas.blit(self.hud.sheet, (self.reset_icons_start_loc.x + (i * 16), self.reset_icons_start_loc.y), self.reset_icons[i])
                    i += 1
                # Need i for easy drawing of hud's lives icon
                self.canvas.blit(self.hud.sheet, (self.reset_icons_start_loc.x + (i * 16), self.reset_icons_start_loc.y), self.hud.lives)
                self.canvas.blit(self.reset_text_surf, self.reset_text_location)

        # draw canvas to the screen scaled to the same size as the screen(window)
        self.screen.blit(pygame.transform.scale(self.canvas, self.screen.get_rect().size))
        
        pygame.display.flip()
    
    def reset(self):
        self.time = LEVEL_TIME
        self.player.reset()
        # TODO Have Enemy Manager and Coin Manager reset
        for enemy in self.enemies:
            enemy.reset()
        for pickup in self.pickups:
            pickup.reset()
        self.map.reset()
        self.camera.reset()
    
    def check_life_up(self):
        if self.score % LIFE_UP_COIN_AMT == 0:
            self.lives += 1
            self.hud.update_lives()
