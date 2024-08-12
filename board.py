import random


class Board:
    def __init__(self, maze_env):
        self.env = maze_env
        self.size = maze_env.get_size()
        self.board_elements = {}
        for x in range(self.size):
            for y in range(self.size):
                self.board_elements[(x, y)] = ' '

        for i in range(round(self.size * self.size / 25)):
            x = round(random.uniform(1, self.size - 3))
            y = round(random.uniform(1, self.size - 3))
            self.board_elements[(x, y)] = 'X'
            self.board_elements[(x + 1, y)] = 'X'
            self.board_elements[(x, y + 1)] = 'X'
            self.board_elements[(x + 1, y + 1)] = 'X'

        for x in range(1, self.size - 1):
            for y in range(1, self.size - 1):
                if self.board_elements[(x, y)] != 'X':
                    self.board_elements[(x, y)] = 'O'

    def check_cell(self, x, y, for_what):
        if x < 0 or x > self.size - 1 or y < 0 or y > self.size - 1:
            return False
        elif self.board_elements[(x, y)] == for_what:
            return True
        return False

    def print_board(self, birds):
        print("    ", end="")
        for i in range(1, self.size + 1):
            if i < 10:
                print(f"{i}  ", end=' ')
            else:
                print(f"{i} ", end=' ')
        print("")
        number = 1
        for x in range(self.size):
            if number < 10:
                print(f'{number} | ', end='')
            else:
                print(f'{number}| ', end='')
            for y in range(self.size):
                if x == birds[1].get_pos()[0] and y == birds[1].get_pos()[1]:
                    print('E', end=' | ')
                elif x == birds[0].get_pos()[0] and y == birds[0].get_pos()[1]:
                    print('B', end=' | ')
                else:
                    print(self.board_elements[(x, y)], end=' | ')
            print("")
            number += 1

    def remove_element(self, x, y):
        self.board_elements[(x, y)] = ' '

    def count_foods(self):
        food_count = 0
        for x in range(self.size):
            for y in range(self.size):
                if self.board_elements[(x, y)] == 'O':
                    food_count += 1
        return food_count

    def set_board_elements(self, elements):
        self.board_elements = elements

    def get_elements(self):
        return self.board_elements
