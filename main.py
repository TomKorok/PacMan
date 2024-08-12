import pickle
import sys

from bird import Bird
from pacman_env import PacManEnv
from pacman_game import PacmanGame
import pygame
from pygame.locals import *

# game and model parameters:
VICTORY_N = 0
GAME_N = 1000
SHOW_GAME = True
WAIT_KEY_END = False
WAIT_TIME = 50
UI_SCALE = 50
MAP_SIZE = 7
USE_TRAINED_MODEL = False
TRAIN_MODEL = True

env = PacManEnv(USE_TRAINED_MODEL, MAP_SIZE)
board = env.create_board()
print(f"Example board:")
board.print_board([Bird(env, -1, -1), Bird(env, -1, -1)])
print(f"Total food amount: {board.count_foods()}")
print(f"Maximum possible reward: {board.count_foods()*env.get_food_reward()}\n")

if TRAIN_MODEL:
    q_table = env.learn(board)
    with open('q_table_bird_trained.txt', "wb") as f:
        pickle.dump(env.get_q_table(), f)
else:
    with open('q_table_bird_trained.txt', 'rb') as f:
        q_table = pickle.load(f)


for i in range(GAME_N):
    if i % (GAME_N / 10) == 0:
        print(f"{round(i / GAME_N * 100)}% completed")
    game = PacmanGame(env, q_table, SHOW_GAME, WAIT_TIME, UI_SCALE)
    if game.play():
        VICTORY_N += 1
    else:
        if SHOW_GAME:
            print("Lose")

    if WAIT_KEY_END:
        print("Victory!")
        pygame.event.clear()
        while True:
            event = pygame.event.wait()
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_f:
                    break

print(f'Victories: {VICTORY_N}')
print(f'Winrate: {VICTORY_N / GAME_N * 100:.2f}%')
