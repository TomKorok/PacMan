
class Bird:
    def __init__(self, env, pos1, pos2):
        self.pos = [pos1, pos2]
        self.env = env

    def __sub__(self, other):
        return self.pos[0] - other.pos[0], self.pos[1] - other.pos[1]

    def __eq__(self, other):
        if self.pos[0] == other.pos[0] and self.pos[1] == other.pos[1]:
            return True
        else:
            return False

    def action(self, action):
        if action == 0:  # move left
            self.step(0, -1)
        elif action == 1:  # move up
            self.step(-1, 0)
        elif action == 2:  # move right
            self.step(0, 1)
        elif action == 3:  # move down
            self.step(1, 0)

    def step(self, x, y):
        self.pos[0] += x
        self.pos[1] += y

        if self.pos[0] < 0:
            self.pos[0] = 0
        elif self.pos[0] > self.env.get_size() - 1:
            self.pos[0] = self.env.get_size()-1

        if self.pos[1] < 0:
            self.pos[1] = 0
        elif self.pos[1] > self.env.get_size() - 1:
            self.pos[1] = self.env.get_size()-1

    def get_pos(self):
        return self.pos

