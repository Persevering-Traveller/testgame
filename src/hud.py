import pygame
import constants

ICON_SIZE = 8

ICON_HEART_FULL = 3
ICON_HEART_EMPTY = 4

MAX_HEALTH = 3

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
        self.last_time = 0
        self.time_numerals = [9, 9, 9]

        self.player_icons = [] # The rects for player lives, health, and coins
        self.player_lives_icon_position = None # Vector2
        self.player_lives_number_position = None
        self.player_health_start_position = None # Vector2
        self.player_coins_icon_position = None # Vector2
        self.player_coins_mult_icon_position = None
        self.player_coins_number_start_position = None

        self.score_font = [] # The rects for the score font
        self.score_start_position = None # Vector2

        self.hearts = []
        self.score = []
        self.coins = []

    
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

        for i in range(3):
            self.hearts.append(self.player_icons[ICON_HEART_FULL])

        for i in range(6):
            self.score.append(self.score_font[9]) # Fill the score with zeroes
        
        for i in range(2):
            self.coins.append(self.score_font[9])
        

    def draw(self, canvas: pygame.Surface):
        # TODO MAJOR -> Make a function that can convert an int value to the proper icon of the number
        canvas.blit(self.bg)
        canvas.blit(self.sheet, self.player_lives_icon_position.xy, self.player_icons[0]) # Player Icon
        # TODO Draw the correct number for how many lives, for now just 3
        canvas.blit(self.sheet, self.player_lives_number_position.xy, self.score_font[2]) # Player Lives Amount

        # TODO Draw the correct health amount (filled in if full, empty if less), for now draw all filled hearts
        for i in range(3):
            canvas.blit(self.sheet, (self.player_health_start_position.x + (i*ICON_SIZE), self.player_health_start_position.y), self.hearts[i]) # Player Health Icons
        
        canvas.blit(self.coins_surf, (self.player_coins_icon_position.x + 4, self.player_coins_icon_position.y - 8)) # 'COIN' text
        canvas.blit(self.sheet, self.player_coins_icon_position.xy, self.player_icons[1]) # Coin Icon
        canvas.blit(self.sheet, self.player_coins_mult_icon_position.xy, self.player_icons[2]) # Coin Mult Icon
        # Draw the amount of coins the player has collected
        for i in range(2):
            canvas.blit(self.sheet, (self.player_coins_number_start_position.x + (i * ICON_SIZE), self.player_coins_number_start_position.y), self.coins[i])

        canvas.blit(self.score_surf, (self.score_start_position.x+12, self.score_start_position.y - 8))
        # Draw the player's score
        for i in range(6):
            canvas.blit(self.sheet, (self.score_start_position.x + (i*ICON_SIZE), self.player_health_start_position.y), self.score[i]) # Score Amount
        
        # Draw timer
        canvas.blit(self.sheet, self.time_icon_position.xy, self.time_font_and_icon[11]) # Timer Icon
        # Draw how much time the player has left; This is easy, as the index is the same as the shown numerical value!
        for i in range(3):
            canvas.blit(self.sheet, (self.time_start_position.x + (i*ICON_SIZE), self.time_start_position.y), self.time_font_and_icon[self.time_numerals[i]]) # Timer Amount
    
    def set_font_ref(self, font: pygame.Font):
        self.font = font
    
    def convert_numeral_to_surf_rect(self, number):
        number_index = -1
        if number == 0:
            number_index = 9 # In the image, the layout of numbers starts from 1 and ends at 0
        else:
            number_index = number - 1
        
        if number_index == -1:
            print("Number given can not be processed")
            return
        else:
            return self.score_font[number_index]
    
    def update_number_array(self, amount, number_rect_array):
        i = -1 # append from the last element
        while(amount != 0):
            number = amount % 10
            number_rect_array[i] = self.convert_numeral_to_surf_rect(number)
            i -= 1
            amount = amount // 10
    
    def update_time(self, current_time):
        time = int(current_time)
        if self.last_time == time:
            return

        self.time_numerals[0] = time // 100 # Hundreds place
        time = time - (self.time_numerals[0] * 100)
        self.time_numerals[1] = time // 10 # Tens place
        time = time - (self.time_numerals[1] * 10)
        self.time_numerals[2] = time # Ones place

        self.last_time = time
    
    def update_score(self, score):
        self.update_number_array(score, self.score)

    def update_coins(self, coins):
        self.update_number_array(coins, self.coins)
    
    def update_health(self, health):
        i = 0
        while(i < health):
            self.hearts[i] = self.player_icons[ICON_HEART_FULL]
            i += 1
        while(i < MAX_HEALTH):
            self.hearts[i] = self.player_icons[ICON_HEART_EMPTY]
            i += 1