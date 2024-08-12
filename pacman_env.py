import math
import operator
import pickle
import statistics
from operator import itemgetter
import numpy as np
from bird import Bird
import random
from board import Board
import copy
import matplotlib.pyplot as plt


class PacManEnv:
    def __init__(self, use_previous_q, size):
        self.use_previous_q = use_previous_q
        self.size = size

    action_n = 4

    # rewards for the bird
    MOVEMENT_REWARD_TO_ENEMY = -1
    MOVEMENT_REWARD_FROM_ENEMY = 1
    MOVEMENT_REWARD_NEUTRAL = 0
    FOOD_REWARD = 100
    DYING_REWARD = -1000

    # rewards for the enemy
    # currently not used as the enemy takes random action
    MOVEMENT_REWARD_ENEMY = -1
    KILL_REWARD = 1000

    def get_food_reward(self):
        return self.FOOD_REWARD

    EPISODES = 2000
    SHOW_FREQ = 100
    LR = 0.1
    DELTA = 0.95
    episode_rewards = []

    # random factor in learning
    epsilon = 0.9
    epsilon_decay = 0.9998
    q_table = {}

    def get_q_table(self):
        return self.q_table

    def get_size(self):
        return self.size

    def create_board(self):
        return Board(self)

    def learn(self, board):
        save_board = copy.deepcopy(board.get_elements())

        if self.use_previous_q:
            with open('q_table_bird_trained.txt', 'rb') as f:
                self.q_table = pickle.load(f)
                print("Q table loaded")
        else:
            for x1 in range(-self.size + 2, self.size - 1):
                for y1 in range(-self.size + 2, self.size - 1):  # closest food statespace
                    for x2 in range(-self.size + 1, self.size):
                        for y2 in range(-self.size + 1, self.size):  # closest enemy statespace
                            self.q_table[((x1, y1), (x2, y2))] = [np.random.uniform(-1, 0) for i in
                                                                  range(self.action_n)]

        for eps in range(1, self.EPISODES):
            board.set_board_elements(copy.deepcopy(save_board))

            # gen birds
            birds = self.create_birds()
            bird = birds[0]
            enemy_bird = birds[1]

            if eps % self.SHOW_FREQ == 0:
                print(f"Episode: {eps}")
                mean = statistics.mean(self.episode_rewards[-self.SHOW_FREQ:])
                pos_max_rew = self.FOOD_REWARD * board.count_foods()
                print(f"Reward mean for the last {self.SHOW_FREQ} episodes: {mean}")
                print(f"In average {mean / pos_max_rew * 100:.2f}% of the maximum possible reward was reached\n")

            episode_reward = 0
            for i in range(100):
                # find the closest food
                closest_food = self.find_closest_object(bird, board, 'O')

                # obs is the distance to the closest food and the enemy_bird and to the closest wall
                obs = (bird - closest_food, bird - enemy_bird)

                # calculate distance to enemy before action
                distance_to_enemy = math.dist(bird.get_pos(), enemy_bird.get_pos())

                # collect q_values from q_table and sort them
                available_act = {}
                for a in range(self.action_n):
                    available_act[a] = self.q_table[obs][a]
                available_act = sorted(available_act.items(), key=operator.itemgetter(1), reverse=True)
                key_list = list(map(itemgetter(0), available_act))
                action = key_list[0]

                # making random moves while training
                for a in range(self.action_n):
                    if self.epsilon < np.random.random():  # smaller the epsilon the more "trained" move the model takes
                        action = key_list[a]
                        copy_bird = Bird(self, bird.get_pos()[0], bird.get_pos()[1])
                        copy_bird.action(action)
                        # if moves leads to wall choose second best...
                        if board.check_cell(copy_bird.get_pos()[0], copy_bird.get_pos()[1], 'X'):
                            continue
                        else:
                            break
                    else:
                        action = np.random.randint(0, 4)

                # our bird takes the action
                bird.action(action)

                # recalculate distance to enemy after bird action
                new_distance_to_enemy = math.dist(bird.get_pos(), enemy_bird.get_pos())

                # enemy movement
                enemy_inc = np.random.randint(0, 4)
                enemy_bird.action(enemy_inc)

                # set rewards
                if bird == enemy_bird:
                    reward = self.DYING_REWARD
                elif bird == closest_food:
                    reward = self.FOOD_REWARD
                    board.remove_element(bird.get_pos()[0], bird.get_pos()[1])
                else:
                    if new_distance_to_enemy > distance_to_enemy:
                        reward = self.MOVEMENT_REWARD_FROM_ENEMY
                    elif new_distance_to_enemy < distance_to_enemy:
                        reward = self.MOVEMENT_REWARD_TO_ENEMY
                    else:
                        reward = self.MOVEMENT_REWARD_NEUTRAL

                closest_food = self.find_closest_object(bird, board, 'O')
                new_obs = (bird - closest_food, bird - enemy_bird)
                max_new_q = np.max(self.q_table[new_obs])
                current_q = self.q_table[obs][action]

                if reward == self.FOOD_REWARD:
                    new_q = self.FOOD_REWARD
                else:
                    new_q = (1 - self.LR) * current_q + self.LR * (
                            reward + self.DELTA * max_new_q)

                self.q_table[obs][action] = new_q

                episode_reward += reward
                if board.count_foods() == 0 or reward == self.DYING_REWARD:
                    break

            self.episode_rewards.append(episode_reward)
            self.epsilon *= self.epsilon_decay

        moving_avg = np.convolve(self.episode_rewards, np.ones((self.SHOW_FREQ,)) / self.SHOW_FREQ, mode='valid')

        plt.plot([i for i in range(len(moving_avg))], moving_avg)
        plt.title("Learning Curve")
        plt.ylabel(f"Mean reward for a {self.SHOW_FREQ} games interval")
        plt.xlabel("Episode number")
        plt.show()

        return self.q_table

    # this method is used to calculate which food object is the closest to our bird
    def find_closest_object(self, bird, board, obj):
        closest_obj = Bird(self, 0, 0)
        closest_dist = self.size * 1.42
        for x in range(1, self.size - 1):
            for y in range(1, self.size - 1):
                if board.get_elements()[(x, y)] == obj:
                    new_closest_dist = math.dist(bird.get_pos(), [x, y])
                    if new_closest_dist < closest_dist:
                        closest_dist = new_closest_dist
                        closest_obj = Bird(self, x, y)

        return closest_obj

    # this method creates the 2 birds on the 2 opposite side of the map
    def create_birds(self):
        bird_x = round(random.uniform(0, self.size - 1))
        bird_y = round(random.uniform(0, self.size - 1))
        side = round(random.uniform(0, 2))
        if side == 0:
            if bird_x < bird_y:
                return [Bird(self, bird_x, 0), Bird(self, self.size - 1 - bird_x, self.size - 1)]
            else:
                return [Bird(self, 0, bird_y), Bird(self, self.size - 1, self.size - 1 - bird_y)]
        else:
            if bird_x < bird_y:
                return [Bird(self, self.size - 1 - bird_x, self.size - 1), Bird(self, bird_x, 0)]
            else:
                return [Bird(self, self.size - 1, self.size - 1 - bird_y), Bird(self, 0, bird_y)]
