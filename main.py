import pygame
from game import Game
    
if __name__ == "__main__":
    game = Game()

    game.load()

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get(pygame.QUIT):
            if event.type == pygame.QUIT:
                running = False
        
        game.update(dt)

        game.draw()

    pygame.quit()