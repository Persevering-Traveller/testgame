import pygame
from tile import Tile
import constants

class Map():
    def __init__(self) -> None:
        self.tile_map = None # Will hold the tileset image
        self.level_bg = None # Will hold the background image
        self.level_bg_rect = None
        self.level = [] # Holds the tiles of a level

    def load(self) -> None:
        # Load the .csv file with open()
        test_level = open("../assets/maps/test-level.csv", "r")
        # Load the tileset image
        self.tile_map = pygame.image.load("../assets/sprites/tileset.png").convert_alpha() # convert_alpha() is needed or it will draw default black in the areas where there's no pixels in that square
        # Load the background image
        self.level_bg = pygame.image.load("../assets/sprites/background.png").convert()
        self.level_bg_rect = pygame.Rect(0, 0, constants.CANVAS_WIDTH, constants.CANVAS_HEIGHT)
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
            self.level[i].set_pos(((i%10), (i//10)))

        test_level.close()

    def draw(self, canvas) -> None:
        #Draw background first
        canvas.blit(self.level_bg, (0, -32), self.level_bg_rect) # That -32 is just so you can see the hills with current level layout

        # reads the level list and for every tile that isn't -1,
        # draws it to the canvas using the tiles dict
        for tile in self.level:
            if tile.get_tile_id() == -1: continue
            canvas.blit(self.tile_map, tile.get_pos_rect(), tile.get_draw_area())
    
    def get_tile_at(self, x, y):
        tile_x = x // constants.TILE_SIZE
        tile_y = y // constants.TILE_SIZE
    
        tile_index = (tile_y * constants.CANVAS_WIDTH//constants.TILE_SIZE) + tile_x
        #print(f"Tile Index is: {tile_index} -- tile_x: {tile_x}, tile_y: {tile_y}")

        tile_id = self.level[tile_index].get_tile_id()
        return tile_id
