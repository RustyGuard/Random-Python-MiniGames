from typing import List

from MyImage import MyImage
import random
import timeit


class Grid:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.EMPTY, self.WALL = 0, 1
        self.arr = []
        for x in range(self.width):
            self.arr.append([0] * self.height)

    def generate_random(self, chance):
        for y in range(self.height):
            for x in range(self.width):
                if random.randint(1, 100) < chance:
                    self.setTile(x, y, 1)

    def setTile(self, x, y, tile):
        if (x < 0 or x >= self.width or y < 0 or y >= self.height):
            return
        self.arr[x][y] = tile

    def tile_to_char(self, tile):
        if tile == self.EMPTY:
            return '~'
        elif tile == self.WALL:
            return '#'
        return 'error'

    def is_empty(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        if self.arr[x][y] == self.WALL:
            return False
        return True

    def get_neightbors(self, x, y):
        for j in range(-1, 2):
            for i in range(-1, 2):
                if self.is_empty(x + i, y + j):
                    yield x + i, y + j

    def __str__(self):
        res = ''
        for y in range(self.height):
            for x in range(self.width):
                res += self.tile_to_char(self.arr[x][y])
                res += ' '
            res += '\n'
        return res


class Node:
    def __init__(self, x, y, parent, step, world):
        self.x, self.y, self.parent, self.step = x, y, parent, step
        self.dirs = [[0, -1], [1, 0], [0, 1], [-1, 0]]
        self.iter = -1
        self.world = world

    def set_parent(self, parent):
        self.parent = parent

    def update_distance(self, xf, yf):
        self.distance = abs(xf - self.x) + abs(yf - self.y)

    def __eq__(self, other):
        if type(other) == Node:
            return self.step + self.distance == other.step + other.distance
        return False

    def __lt__(self, other):
        return self.step + self.distance < other.step + other.distance

    def __le__(self, other):
        return self.step + self.distance == other.step + other.distance

    def __str__(self):
        return 'Pos: {} {}; Step: {}; Value: {}'.format(self.x, self.y, self.step, self.distance)

    def __getitem__(self, i):
        x, y = self.x + self.dirs[i][0], self.y + self.dirs[i][1]
        if self.world.is_empty(x, y):
            return Node(x, y, self, self.step + 1, self.world)
        return None

    def get_next(self, x, y):
        return Node(x, y, self, self.step + 1, self.world)

    def __int__(self):
        return len(self.dirs)

    def DrawRecursively(self, image, color):
        if self.parent:
            self.parent.DrawRecursively(image, color)
        self.Draw(image, color)

    def Draw(self, image, color):
        image.Rect(self.x * 30, self.y * 30, 30, 30, color)
        image.Text(self.x * 30 + 2, self.y * 30, str(self.distance))
        image.Text(self.x * 30 + 2, self.y * 30 + 18, str(self.step))
        image.Text(self.x * 30 + 7, self.y * 30 + 9, str(self.step + self.distance))


def find_path_garbage(grid, xs, ys, xf, yf):
    if not grid.is_empty(xs, ys):
        print('Can not start from wall!')
        return None
    if not grid.is_empty(xf, yf):
        print('Finish inside a wall!')
        return None
    opened = []
    closed = []
    map = []
    for x in range(grid.width):
        map.append([0] * grid.height)
    start_node = Node(xs, ys, None, 0, grid)
    start_node.update_distance(xf, yf)
    map[xs][ys] = start_node
    opened.append(start_node)
    while True:
        if len(opened) == 0:
            return []

        curr = opened.pop(0)
        closed.append(curr)

        for coord in grid.get_neightbors(curr.x, curr.y):
            if coord[0] == xf and coord[1] == yf:
                return curr.get_next(*coord)

            if map[coord[0]][coord[1]] == 0:
                new = curr.get_next(*coord)
                new.update_distance(xf, yf)
                opened.insert(0, new)
                map[new.x][new.y] = new
            elif map[coord[0]][coord[1]] in opened:
                if curr.step + 1 < map[coord[0]][coord[1]].step:
                    map[coord[0]][coord[1]].set_parent(curr)
                    map[coord[0]][coord[1]].step = curr.step + 1


def find_path(grid, xs, ys, xf, yf):
    if not grid.is_empty(xs, ys):
        print('Can not start from wall!')
        return
    if not grid.is_empty(xf, yf):
        print('Finish inside a wall!')
        return
    opened = []
    closed = []
    map = []
    for x in range(grid.width):
        map.append([0] * grid.height)
    start_node = Node(xs, ys, None, 0, grid)
    start_node.update_distance(xf, yf)
    map[xs][ys] = start_node
    opened.append(start_node)
    while True:
        if len(opened) == 0:
            break
        curr = opened.pop(0)
        closed.append(curr)

        for x, y in grid.get_neightbors(curr.x, curr.y):
            new = curr.get_next(x, y)
            if map[x][y] == 0:
                new.update_distance(xf, yf)
                opened.insert(0, new)
                map[x][y] = new
            elif map[x][y] in opened:
                if curr.step + 1 < map[new.x][new.y].step:
                    map[x][y].set_parent(curr)
                    map[x][y].step = curr.step + 1
            if x == xf and y == yf:
                return curr.get_next(x, y)

        opened.sort()
