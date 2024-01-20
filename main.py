import settings
from ScreenClasses import *
from GameLogicClassesAndHandlers import *

pygame.init()

screen = pygame.display.set_mode((settings.width, settings.height))

clock = pygame.time.Clock()
running = True
music_play = True
dt = 0
player = Player(centre, 100, 15, curve_nr=0, path_deviation=0, player_speed=400)
obstacle_handler = ObstacleHandler(45, 270, 200)
game = SectorGame(player, obstacle_handler, 'easy')
text_handler = TextHandler(40)

#neat_config_file = "config.txt"
#config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation,
#                     neat_config_file)

while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    game.handle_screen(text_handler, screen, dt)
    game.handle_events(dt, events)
    game.detect_collision()

    mouse = pygame.mouse.get_pos()

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-independent physics.
    dt = clock.tick(60) / 1000


pygame.quit()
