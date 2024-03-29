from sector import *
import neat
import pygame

pygame.init()

screen = pygame.display.set_mode((width, height))

clock = pygame.time.Clock()
running = True
dt = 0
player = Player(centre, 100, 15, curve_nr=0, path_deviation=0, player_speed=400)
obstacle_handler = ObstacleHandler(45, 270, 200)
# Game class has the optional argument "difficulty". If not provided the game will launch with the vales provided by the
# user above.
# In case the "difficulty parameter is provided, the user provided values will be overwritten by the ones saved in the
# difficulty. Available options are 'easy', 'medium', 'hard' and 'insane'.
game = Game(player, obstacle_handler)
text_handler = TextHandler(40)

neat_config_file = "config.txt"
# config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, neat_config_file)


class SectorGame:
    def __init__(self):
        pass

    def test_ai(self, net):
        pass

    def train_ai(self, genome, config, draw=False):
        pass

    def move_player(self, net):
        pass

    def calculate_fitness(self, game_info, score):
        pass


def eval_genomes(genomes, config):
    pass


def run_neat(config):
    p = neat.Population(config)
    # p = neat.Checkpointer.restore_checkpoint("name")
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter((neat.Checkpointer(1)))
    p.run(eval_genomes, 50)


def test_best_network(config):
    pass


while running and not game.exit_loop:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    info = game.loop(dt)
    game.draw(screen, text_handler)
    game.handle_events(dt, events)
    game.detect_collision()

    mouse = pygame.mouse.get_pos()

    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-independent physics.
    dt = clock.tick(60) / 1000

print(info)
pygame.quit()
