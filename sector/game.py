import pygame
from pygame.math import Vector2
from .settings import *
import ast
from .GameLogicClassesAndHandlers import *
import math


class Game:
    def __init__(self, player, obstacle_handler, difficulty):
        self.player = player
        self.obstacle_handler = obstacle_handler
        self.path_perc = 0
        self.initial_obstacle = False
        self.screen_change = (None, None, None)
        self.score = 0
        self.game_end = False
        self.exit_loop = False
        self.difficulty = DifficultyHandler(difficulty)

    def draw(self, screen, text_handler):
        screen.fill(color_palette['background'])
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        self.obstacle_handler.draw_obstacles(screen)
        text_handler.draw_text(screen, str(self.score), color_palette['text'], (width / 2, text_handler.font_size))

    def loop(self, dt):
        if not self.initial_obstacle:
            self.create_init_obstacle()
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        # Deletion of obstacles that reached an end. Increasing player score in case obstacle was removed.
        if self.obstacle_handler.delete_dead_obstacles():
            self.score += 1
        self.check_for_end()
        return self.give_current_game_status()

    def create_init_obstacle(self):
        self.obstacle_handler.create_new_obstacle()
        self.initial_obstacle = True

    def change_path_perc(self, val):
        self.path_perc += val

    def handle_events(self, dt, events):
        keys = pygame.key.get_pressed()
        # Player moves are binded to right and left arrows.
        if keys[pygame.K_RIGHT]:
            self.change_path_perc(dt * self.player.player_speed)
            self.player.move(self.path_perc)
        if keys[pygame.K_LEFT]:
            self.change_path_perc(-dt * self.player.player_speed)
            self.player.move(self.path_perc)

    def restart_game(self):
        self.player.is_alive = True
        self.player.player_position = self.player.move(0)
        self.obstacle_handler.obstacles = {}
        self.obstacle_handler.last_created_obstacle = None
        self.initial_obstacle = False
        self.path_perc = 0
        self.score = 0
        self.game_end = False

    def detect_collision(self):
        player_circle = pygame.Surface((2*self.player.radius, 2*self.player.radius), pygame.SRCALPHA)
        pygame.draw.circle(player_circle, [255, 255, 255], [self.player.radius, self.player.radius], self.player.player_radius)
        player_pos = Vector2(self.player.player_position)
        player_rect = player_circle.get_rect(center=player_pos)
        player_rect.center = player_pos
        obstacles_original = pygame.Surface((width, height), pygame.SRCALPHA)
        for obstacle in self.obstacle_handler.obstacles.values():
            pygame.draw.polygon(obstacles_original, (0, 0, 255), obstacle.rotate_obstacle(obstacle.start_angle))
        obst = obstacles_original
        pos_blue = Vector2(width / 2, height / 2)
        obstacle_rect = obst.get_rect(center=pos_blue)
        mask_obst = pygame.mask.from_surface(obst)
        mask_player = pygame.mask.from_surface(player_circle)
        offset_ = (obstacle_rect.x - player_rect.x), (obstacle_rect.y - player_rect.y)
        overlap_ = mask_player.overlap(mask_obst, offset_)
        if overlap_:
            self.game_end = True

    def check_for_end(self):
        if self.game_end:
            score = self.score
            f = open('scores.txt')
            s = f.read()
            f.close()
            scores = ast.literal_eval(s)
            if scores[self.difficulty.current_difficulty] < score:
                f = open('scores.txt', 'w')
                scores[self.difficulty.current_difficulty] = score
                f.write(str(scores))
                f.close()
            self.exit_loop = True
            self.restart_game()

    def change_game_settings(self, settings_dict):
        self.restart_game()
        # player settings
        self.player.radius = settings_dict['player']['radius']
        self.player.player_radius = settings_dict['player']['player_radius']
        self.player.curve_nr = settings_dict['player']['curve_nr']
        self.player.path_deviation = settings_dict['player']['path_deviation']
        self.player.player_speed = settings_dict['player']['player_speed']
        # obstacle_handler settings
        self.obstacle_handler.min_angle = settings_dict['obstacle_handler']['min_angle']
        self.obstacle_handler.max_angle = settings_dict['obstacle_handler']['max_angle']
        self.obstacle_handler.distance_between_obstacles = \
            settings_dict['obstacle_handler']['distance_between_obstacles']
        self.player.player_path = self.player.generate_player_path()

    def give_current_game_status(self):
        def get_inner_radius(obstacle):
            return obstacle.inner_radius
        info_dict = {'player_position_0': self.player.player_position[0],
                     'player_position_1': self.player.player_position[1],
                     'player_radius': self.player.player_radius,
                     'game_radius': self.player.radius,
                     'curve_nr': self.player.curve_nr,
                     'path_deviation': self.player.path_deviation,
                     'player_speed': self.player.player_speed,
                     'distance_between_obstacles': self.obstacle_handler.distance_between_obstacles
                     }
        obstacles_sorted = [obstacle for obstacle in self.obstacle_handler.obstacles.values()]
        obstacles_sorted.sort(key=get_inner_radius)
        distance_between_obstacles = self.difficulty.difficulties[self.difficulty.current_difficulty]['obstacle_handler']['distance_between_obstacles']
        max_possible_number_of_obstacles = int(math.sqrt((centre[0])**2 + (centre[1])**2) / distance_between_obstacles) + 1
        for i in range(max_possible_number_of_obstacles):
            if i < len(obstacles_sorted):
                info_dict[f'o{i}_inner_radius'] = obstacles_sorted[i].inner_radius
                info_dict[f'o{i}_outer_radius'] = obstacles_sorted[i].outer_radius
                info_dict[f'o{i}_start_angle'] = obstacles_sorted[i].start_angle
                info_dict[f'o{i}_angle'] = obstacles_sorted[i].angle

            else:
                info_dict[f'o{i}_inner_radius'] = 0
                info_dict[f'o{i}_outer_radius'] = 0
                info_dict[f'o{i}_start_angle'] = 0
                info_dict[f'o{i}_angle'] = 0
        return info_dict
