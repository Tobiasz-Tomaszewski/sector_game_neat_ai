import pygame
from pygame.math import Vector2
from settings import *
import ast
import GameLogicClassesAndHandlers
import math


class SectorGame:
    """
    This is one of the most important class in the project. It combines information from Player class and
    ObstacleHandler class to create the game logic. This class also fills the role of game screen, so it does have
    all necessary Screen methods and screen_change attribute.

    Attributes:
        player (GameLogicClassesAndHandlers.Player): Instance of Player class. It contains all information about the
            player.
        obstacle_handler (GameLogicClassesAndHandlers.ObstacleHandler): Instance of ObstacleHandler object. It contains
            all information about current obstacles, can generate and draw new obstacles.
        path_perc (float): Percentage of the path that tells where the player is currently located in the relation to
            the path. Is used as argument passed to "move" method.
        initial_obstacle (bool): Logical value used to initialize the creation of the obstacles.
        screen_change (tuple): Screen class attribute.
        score (int): Score of the player. It is calculated based on the number of obstacles that reach the end.
        game_end (bool): Logical value that indicates whether the player has lost.
        difficulty (GameLogicClassesAndHandlers.DifficultyHandler): Instance of DifficultyHandler class. Contains all
            information needed to create new game.

    Methods:
        create_init_obstacle(): Initializes the process of generating obstacles.
        change_path_perc(val: float): Changes the player position by changing the "path_perc" attribute.
        handle_screen(text_handler: GameLogicClassesAndHandlers.TextHandler, screen: pygame.surface.Surface, dt: float):
            Deals with all action that takes places in a single frame of main pygame loop. This method must be
            implemented for all screens.
        handle_events(dt: float, events: list): Handles player events. Should have an event or other condition that can
            change current screen. This method must be implemented for all screens.
        reset_next(): Sets "screen_change" parameter to (None, None, None). This method must be implemented for all
            screens.
        restart_game(): Performs all actions necessary to consider the current instance of Game class to be "new".
        detect_collision(): Is responsible for collision logic.
        check_for_end(): Checks if a game ended, if yes performs all actions necessary at the end of the game.
        get_from_prev_screen(Any): Is used to pass any type of information to the next screen. This method must be
            implemented for all screens.
        change_game_settings(dict): Changes the game difficulty settings. The dict passed as an argument should be
            an attribute of DifficultyHandler object
    """
    def __init__(self, player, obstacle_handler, difficulty):
        """
        __init__ method of Game class.

        Args:
            player (GameLogicClassesAndHandlers.Player): Instance of Player class. It contains all information about the
                player.
            obstacle_handler (GameLogicClassesAndHandlers.ObstacleHandler): Instance of ObstacleHandler object. It contains
                all information about current obstacles, can generate and draw new obstacles.
        """
        self.player = player
        self.obstacle_handler = obstacle_handler
        self.path_perc = 0
        self.initial_obstacle = False
        self.screen_change = (None, None, None)
        self.score = 0
        self.game_end = False
        self.difficulty = GameLogicClassesAndHandlers.DifficultyHandler(difficulty)

    def loop(self):
        pass

    def create_init_obstacle(self):
        """
        Initializes the process of generating obstacles by creating the new obstacle. Changes "initial_obstacle" value
        to True, so the process is not repeated.

        Returns:
            None: None
        """
        self.obstacle_handler.create_new_obstacle()
        self.initial_obstacle = True

    def change_path_perc(self, val):
        """
        Changes value of "path_perc" attribute by value passed in the argument.

        Args:
            val (float): Value that is added to "path_perc" attribute.

        Returns:
            None: None
        """
        self.path_perc += val

    def handle_screen(self, text_handler, screen, dt):
        """
        Deals with all action that takes places in a single frame of main pygame loop. For details check comments in the
        code.

        Args:
            text_handler (GameLogicClassesAndHandlers.TextHandler): Instance of TextHandler class. Is used to deal with
                text.
            screen (pygame.surface.Surface): Screen that the object are being drawn on.
            dt (float): Delta time in seconds since last frame.

        Returns:
            None: None
        """
        # Fill the screen with the color specified in setting file.
        screen.fill(color_palette['background'])
        # Draw player related attributes.
        self.player.draw_player(screen)
        self.player.draw_player_path(screen)
        # Initialize the creation of obstacle in case it was not done yet.
        if not self.initial_obstacle:
            self.create_init_obstacle()
        # Perform obstacle related actions, such as drawing, generating, moving.
        self.obstacle_handler.draw_obstacles(screen)
        self.obstacle_handler.move_all_obstacles(dt)
        self.obstacle_handler.generate_next()
        # Deletion of obstacles that reached an end. Increasing player score in case obstacle was removed.
        if self.obstacle_handler.delete_dead_obstacles():
            self.score += 1
        # Draw player score
        text_handler.draw_text(screen, str(self.score), color_palette['text'], (width / 2, text_handler.font_size))
        # Check if the game should be finished.
        self.check_for_end()

    def handle_events(self, dt, events):
        """
        This method is responsible for handling all events that take place on the screen, such as pressing a key. This
        includes event that changes the screen, so "handle_events" should have action that updates "screen_change"
        attribute. For details check comments in the code.

        Args:
            dt (float): Delta time in seconds since last frame.
            events (list): Events that happened in a single iteration of pygame "while run" loop - pygame.event.get().

        Returns:
            None: None
        """
        keys = pygame.key.get_pressed()
        # Player moves are binded to right and left arrows.
        if keys[pygame.K_RIGHT]:
            self.change_path_perc(dt * self.player.player_speed)
            self.player.move(self.path_perc)
        if keys[pygame.K_LEFT]:
            self.change_path_perc(-dt * self.player.player_speed)
            self.player.move(self.path_perc)

        for event in events:
            if pygame.KEYUP:
                # Escape key changes the current screen to the pause screen.
                if keys[pygame.K_ESCAPE]:
                    self.screen_change = (True, 'pause', self.score)
                # Game can be restarted with 'r' key.
                if keys[pygame.K_r]:
                    self.restart_game()

    def restart_game(self):
        """
        Performs all actions necessary to consider the current instance of Game class to be "new". This includes:

        Returns:
            None: None
        """
        self.player.is_alive = True
        self.player.player_position = self.player.move(0)
        self.obstacle_handler.obstacles = {}
        self.obstacle_handler.last_created_obstacle = None
        self.initial_obstacle = False
        self.path_perc = 0
        self.score = 0
        self.game_end = False

    def detect_collision(self):
        """
        Is responsible for collision logic. It uses "overlap" method of pygame.Mask object. In case the collision
        between player and obstacle happens, the "game_end" is set to True.

        Returns:
            None: None
        """
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
        """
        Check if game ended, based on "game_end" attribute. If yes, overwrites the file with best scores, restarts the
        game status and changes "screen_change", so the loosing screen can be displayed.

        Returns:
            None: None
        """
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
            self.restart_game()
            self.screen_change = (True, 'lost', score)

    def change_game_settings(self, settings_dict):
        """
        Restarts the game and changes the attributes of a player and obstacle handler in order to impact game
            difficulty.

        Args:
            settings_dict (dict): Dictionary containing all game difficulty info. Those dictionaries have specific
                format and are stored in DifficultyHandler properties.

        Returns:
            None: None
        """
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
