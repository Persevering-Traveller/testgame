import pygame
import constants

ICON_SIZE = 8

class HUD():
    def __init__(self) -> None:
        self.bg = None # Will hold the hud's bg (a literal black bar)
        self.sheet = None # Will hold the spritesheet of the hud
        self.font = None # Game Font ref
        self.score_surf = None # Will hold the rendered 'Score' surface
        self.coins_surf = None # Will hold the rendered 'Coins' surface
        self.score_surf_start_pos = None
        self.coins_surf_start_pos = None

        self.time_font_and_icon = [] # Will hold the rects of time font on the sheet (to subdraw)
        self.time_icon_position = None
        self.time_start_position = None # Vector2

        self.player_icons = [] # The rects for player lives, health, and coins
        self.player_lives_icon_position = None # Vector2
        self.player_lives_number_position = None
        self.player_health_start_position = None # Vector2
        self.player_coins_icon_position = None # Vector2
        self.player_coins_mult_icon_position = None
        self.player_coins_number_start_position = None

        self.score_font = [] # The rects for the score font
        self.score_start_position = None # Vector2

    
    def load(self):
        # NOTE Okay, this is fine for this test game, but OH MY GOD I NEVER WANNA DO THIS BY HAND EVER AGAIN (load AND draw)
        # I gotta find a way to set this all up with Tiled

        # Make the background
        self.bg = pygame.Surface((constants.CANVAS_WIDTH, constants.TILE_SIZE)).convert()
        self.bg.fill("black")

        # Make the Score and Coin surfaces
        self.score_surf = self.font.render("SCORE", False, "white").convert()
        self.coins_surf = self.font.render("COINS", False, "white").convert()

        # Load HUD spritesheet
        self.sheet = pygame.image.load("../assets/sprites/hud-sheet.png").convert_alpha()
        # Load time subdraw positions
        for i in range(12): # 6x2 layout in sheet
            self.time_font_and_icon.append(pygame.Rect((i%6)*ICON_SIZE, (i//6)*ICON_SIZE, ICON_SIZE, ICON_SIZE))
        # Set time position (icon and font)
        self.time_icon_position = pygame.math.Vector2(8, constants.CANVAS_HEIGHT-ICON_SIZE)
        self.time_start_position = pygame.math.Vector2(self.time_icon_position.x + ICON_SIZE, self.time_icon_position.y)

        # Load lives subdraw positions
        for i in range(5):
            self.player_icons.append(pygame.Rect((ICON_SIZE*6)+((i%3)*ICON_SIZE), (i//3)*ICON_SIZE, ICON_SIZE, ICON_SIZE))
        # Set player lives position (icon and font)
        self.player_lives_icon_position = pygame.math.Vector2(8, 0)
        self.player_lives_number_position = pygame.math.Vector2(self.player_lives_icon_position.x + ICON_SIZE, self.player_lives_icon_position.y)
        # Set player health position
        self.player_health_start_position = pygame.math.Vector2(self.player_lives_icon_position.x, self.player_lives_icon_position.y + ICON_SIZE)
        # Set player coins position (icons, and font)
        self.player_coins_icon_position = pygame.math.Vector2(ICON_SIZE * 8, self.player_health_start_position.y)
        self.player_coins_mult_icon_position = pygame.math.Vector2(self.player_coins_icon_position.x + ICON_SIZE, self.player_coins_icon_position.y)
        self.player_coins_number_start_position = pygame.math.Vector2(self.player_coins_mult_icon_position.x + ICON_SIZE, self.player_coins_mult_icon_position.y)

        # Load score font subdraw positions
        for i in range(10):
            self.score_font.append(pygame.Rect((ICON_SIZE*10)+(i%5)*ICON_SIZE,(i//5)*ICON_SIZE, ICON_SIZE, ICON_SIZE))
        # Set score position
        self.score_start_position = pygame.math.Vector2(ICON_SIZE*14, self.player_coins_icon_position.y)
        

    
    def update(self, dt):
        pass

    def draw(self, canvas: pygame.Surface):
        # TODO MAJOR -> Make a function that can convert an int value to the proper icon of the number
        canvas.blit(self.bg)
        canvas.blit(self.sheet, self.player_lives_icon_position.xy, self.player_icons[0]) # Player Icon
        # TODO Draw the correct number for how many lives, for now just 3
        canvas.blit(self.sheet, self.player_lives_number_position.xy, self.score_font[2]) # Player Lives Amount

        # TODO Draw the correct health amount (filled in if full, empty if less), for now draw all filled hearts
        for i in range(3):
            canvas.blit(self.sheet, (self.player_health_start_position.x + (i*ICON_SIZE), self.player_health_start_position.y), self.player_icons[3]) # Player Health Icons
        
        canvas.blit(self.coins_surf, (self.player_coins_icon_position.x + 4, self.player_coins_icon_position.y - 8)) # 'COIN' text
        canvas.blit(self.sheet, self.player_coins_icon_position.xy, self.player_icons[1]) # Coin Icon
        canvas.blit(self.sheet, self.player_coins_mult_icon_position.xy, self.player_icons[2]) # Coin Mult Icon
        # TODO Draw the amount of coints the player has collected, for now double 0, and remember, 0 is the LAST number on the sheet
        canvas.blit(self.sheet, (self.player_coins_number_start_position.x, self.player_coins_number_start_position.y), self.score_font[9]) # Coin Amount (10s place)
        canvas.blit(self.sheet, (self.player_coins_number_start_position.x + ICON_SIZE, self.player_coins_number_start_position.y), self.score_font[9]) # Coin Amount (1s place)

        canvas.blit(self.score_surf, (self.score_start_position.x+12, self.score_start_position.y - 8))
        # TODO Draw the player's score correctly, for now all 0s
        for i in range(6):
            canvas.blit(self.sheet, (self.score_start_position.x + (i*ICON_SIZE), self.player_health_start_position.y), self.score_font[9]) # Score Amount
        

        canvas.blit(self.sheet, self.time_icon_position.xy, self.time_font_and_icon[11]) # Timer Icon
        # TODO Draw how much time the player has left correctly, for now all 9s; This should be easy, as the index is the same as the shown numerical value!
        for i in range(3):
            canvas.blit(self.sheet, (self.time_start_position.x + (i*ICON_SIZE), self.time_start_position.y), self.time_font_and_icon[9]) # Timer Amount
    
    def set_font_ref(self, font: pygame.Font):
        self.font = font
        