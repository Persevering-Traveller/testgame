import pygame
from tile import Tile
from entity import Entity
import constants

class Map():
    def __init__(self) -> None:
        self.tile_map = None # Will hold the tileset image
        self.level_bg = None # Entity that will hold the background image
        self.level = [] # Holds the tiles of a level
        self.player_pos = None
        self.end_of_level_pos = None
        self.enemy_pos = []
        self.pickup_pos = []

    def load(self) -> None:
        # Load the World .csv file with open()
        test_level = open("../assets/maps/test-level-v1_World.csv", "r")
        # Load the tileset image
        self.tile_map = pygame.image.load("../assets/sprites/tileset.png").convert_alpha() # convert_alpha() is needed or it will draw default black in the areas where there's no pixels in that square
        # Load the background image
        self.level_bg = Entity()
        self.level_bg.sprite = pygame.image.load("../assets/sprites/background.png").convert()
        self.level_bg.anim_frames.append(pygame.Rect(0, 0, constants.CANVAS_WIDTH, constants.CANVAS_HEIGHT))
        self.level_bg.pos_rect = pygame.Rect(0, -32, constants.CANVAS_WIDTH, constants.CANVAS_HEIGHT) # That -32 is just so you can see the hills with current level layout
        # Read the csv file line by line and split it by commas
        # and assign it to level list
        level_by_line = []
        for line in test_level:
            level_by_line.extend(line.split(","))
        
        # Load each individual tile's draw location based on the tileset 
        # into the dict by making the key the tileID, and the value is 
        # the section of the tileset for the tile using pygame.Rect
        for tile in level_by_line:
            tileObj = Tile()
            tile_id = int(tile)
            tileObj.set_tile_id(tile_id)
            if tile_id == -1:
                tileObj.set_draw_area(pygame.Rect(0, 0, 0, 0))
            else:
                tileObj.set_draw_area(((tile_id%13), (tile_id//13)))

            self.level.append(tileObj)

        # Set each loaded tile's position
        for i in range(len(self.level)):
            self.level[i].set_pos(((i%constants.LEVEL_TILE_WIDTH), (i//constants.LEVEL_TILE_WIDTH)))

        test_level.close()

        # Load in the positions for Player, Enemies, Pickups, and End of Level
        pos_file = open("../assets/maps/test-level-v1_Positions.csv", "r")
        positions = []
        for line in pos_file:
            positions.extend(line.split(","))
        
        for i in range(len(positions)):
            match(int(positions[i])):
                case 4:
                    self.player_pos = pygame.Rect((i%constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, (i//constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, 1, 1)
                case 5:
                    self.enemy_pos.append(pygame.Rect((i%constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, (i//constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, 1, 1))
                case 6:
                    self.pickup_pos.append(pygame.Rect((i%constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, (i//constants.LEVEL_TILE_WIDTH) * constants.TILE_SIZE, 1, 1))
        
        #print(f"Player Pos: {self.player_pos}\nEnemies: {self.enemy_pos}\nPickups: {self.pickup_pos}")
        pos_file.close()

    def draw(self, canvas) -> None:
        #Draw background first, and move background in order to be parallax
        if self.level_bg.pos_rect.x > 0:
            self.level_bg.pos_rect.x = -constants.CANVAS_WIDTH
        elif self.level_bg.pos_rect.right < 0:
            self.level_bg.pos_rect.x = 0

        # Two blits of the background are needed to create a parallax background
        canvas.blit(self.level_bg.sprite, self.level_bg.pos_rect, self.level_bg.anim_frames[0])
        canvas.blit(self.level_bg.sprite, (self.level_bg.pos_rect.x + constants.CANVAS_WIDTH, self.level_bg.pos_rect.y), self.level_bg.anim_frames[0])

        # reads the level list and for every tile that isn't -1,
        # draws it to the canvas using the tiles dict
        for tile in self.level:
            if tile.get_tile_id() == -1: continue
            canvas.blit(self.tile_map, tile.get_pos_rect(), tile.get_draw_area())
    
    def get_tile_at(self, x, y):
        # Keeping just in case there's another way similar to my old way
        tile_x = x // constants.TILE_SIZE
        tile_y = y // constants.TILE_SIZE

        tile_index = (tile_y * constants.LEVEL_TILE_WIDTH) + tile_x

        if tile_index > constants.LEVEL_TILE_WIDTH * 9 or tile_index < 0: # If where the entity is would be out of bounds
            tile_id = -1
        else:
            tile_id = self.level[tile_index].get_tile_id()

        #print(f"Tile ID is: {tile_id} -- Tile Index is: {tile_index} -- tile_x: {tile_x}, tile_y: {tile_y}")
        
        return tile_id
    
    def get_level_data(self):
        return self.level

    def get_level_bg(self):
        return self.level_bg

    def get_player_start_pos(self):
        return self.player_pos
    
    def get_enemy_positions(self):
        return self.enemy_pos
    
    def get_pickup_positions(self):
        return self.pickup_pos

    def reset(self):
        for tile in self.level:
            tile.reset()