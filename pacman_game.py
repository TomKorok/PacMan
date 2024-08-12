import copy
import operator
from operator import itemgetter
import numpy as np
import pygame


class PacmanGame:
    def __init__(self, env, q_table_input, show_game, wait_time, scale):
        self.q_table = q_table_input
        self.env = env
        self.show_game = show_game
        self.wait_time = wait_time
        self.scale = scale

        # 0 is the bird -- 1 is the enemy_bird
        self.birds = self.env.create_birds()

        self.closest_food = None
        self.closest_wall = None

    def play(self):
        if self.show_game:
            pygame.init()
            win = pygame.display.set_mode((self.env.get_size() * self.scale, self.env.get_size() * self.scale))
        board = self.env.create_board()
        self.update_board(board)
        if self.show_game:
            board.print_board(self.birds)

        if self.show_game:
            # draw the game
            pygame.display.set_caption("Pac-man")
            self.draw(win, board)
            pygame.time.delay(self.wait_time)

        while board.count_foods() > 0:
            # find the closest food in the environment
            self.closest_food = self.env.find_closest_object(self.birds[0], board, 'O')

            # obs is the distance to the closest food and the enemy_bird
            obs = (self.birds[0] - self.closest_food, self.birds[0] - self.birds[1])

            available_act = {}
            for a in range(4):
                available_act[a] = self.q_table[obs][a]
            available_act = sorted(available_act.items(), key=operator.itemgetter(1), reverse=True)
            key_list = list(map(itemgetter(0), available_act))
            action = key_list[0]

            for i in range(4):
                action = key_list[i]
                copy_bird = copy.deepcopy(self.birds[0])
                copy_bird.action(action)
                if board.check_cell(copy_bird.get_pos()[0], copy_bird.get_pos()[1], 'X'):
                    continue
                else:
                    break

            # taking action for the bird and for the enemy
            self.birds[0].action(action)
            enemy_inc = np.random.randint(0, 4)
            self.birds[1].action(enemy_inc)

            # update board based on the actions
            self.update_board(board)

            # show the game after every step
            if self.show_game:
                board.print_board(self.birds)
                # draw the game
                pygame.display.set_caption("Pac-man")
                self.draw(win, board)
                pygame.time.delay(self.wait_time)

            if self.birds[0] == self.birds[1]:
                return False

        return True

    def update_board(self, board):
        if board.check_cell(self.birds[0].get_pos()[0], self.birds[0].get_pos()[1], 'O'):
            board.remove_element(self.birds[0].get_pos()[0], self.birds[0].get_pos()[1])

    def draw(self, win, board):
        # make the map black - it kinda refreshes it
        win.fill((0, 0, 0))
        # draw objects on the map
        for x in range(1, self.env.get_size() - 1):
            for y in range(1, self.env.get_size() - 1):
                if board.check_cell(x, y, 'O'):
                    pygame.draw.rect(win, (0, 255, 0), (y * self.scale, x * self.scale, self.scale, self.scale))
                if board.check_cell(x, y, 'X'):
                    pygame.draw.rect(win, (128, 128, 128), (y * self.scale, x * self.scale, self.scale, self.scale))

        # draw birds on the map
        pygame.draw.rect(win, (255, 255, 0), (
            self.birds[0].get_pos()[1] * self.scale, self.birds[0].get_pos()[0] * self.scale, self.scale, self.scale))
        pygame.draw.rect(win, (255, 0, 0), (
            self.birds[1].get_pos()[1] * self.scale, self.birds[1].get_pos()[0] * self.scale, self.scale, self.scale))
        pygame.display.update()
