from MyImage import MyImage
import random
import timeit


class Grid:
    def __init__(self, width, height):
        self.WIDTH, self.HEIGHT = width, height
        self.EMPTY, self.WALL = 0, 1
        self.arr = []
        for x in range(self.WIDTH):
            self.arr.append([0] * self.HEIGHT)

    def generate_random(self, chance):
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                if random.randint(1, 100) < chance:
                    self.setTile(x, y, 1)

    def setTile(self, x, y, tile):
        if (x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT):
            return
        self.arr[x][y] = tile

    def tile_to_char(self, tile):
        if tile == self.EMPTY:
            return '~'
        elif tile == self.WALL:
            return '#'
        return 'error'

    def is_empty(self, x, y):
        if x < 0 or x >= self.WIDTH or y < 0 or y >= self.HEIGHT:
            return False
        if self.arr[x][y] == self.WALL:
            return False
        return True

    def __str__(self):
        res = ''
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
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
    for x in range(grid.WIDTH):
        map.append([0] * grid.HEIGHT)
    start_node = Node(xs, ys, None, 0, grid)
    start_node.update_distance(xf, yf)
    map[xs][ys] = start_node
    opened.append(start_node)
    it = 0
    objs = 0
    adepted = 0
    while True:
        it += 1
        if (it <= 10):
            print(it)
        if (10 < it <= 100) and it % 10 == 0:
            print(it)
        if (100 < it) and it % 100 == 0:
            print(it)
        if len(opened) == 0:
            result = MyImage(grid.WIDTH * 30, grid.HEIGHT * 30)
            for i in closed:
                i.Draw(result, (50, 0, 200))
            for y in range(grid.HEIGHT):
                for x in range(grid.WIDTH):
                    if not grid.is_empty(x, y):
                        result.Rect(x * 30, y * 30, 30, 30, fill=(255, 255, 0))
            result.Text(xs * 30, ys * 30, 'Start')
            result.Text(xf * 30, yf * 30, 'Finish')

            result.Save('path.png')
            print('Can not find a path')
            break
        curr = opened.pop(0)
        closed.append(curr)
        for i in range(int(curr)):
            new = curr[i]
            if not new:
                continue
            objs += 1
            if map[new.x][new.y] == 0:
                new.update_distance(xf, yf)
                opened.insert(0, new)
                map[new.x][new.y] = new
            elif map[new.x][new.y] in opened:
                if curr.step + 1 < map[new.x][new.y].step:
                    adepted += 1
                    map[new.x][new.y].set_parent(curr)
                    map[new.x][new.y].step = curr.step + 1
            if new.x == xf and new.y == yf:
                print('Path founded.')
                print('Objects created: ', objs)
                print('Objects adepted: ', adepted)
                result = MyImage(grid.WIDTH * 30, grid.HEIGHT * 30)
                for i in opened:
                    i.Draw(result, (150, 150, 150))
                for i in closed:
                    i.Draw(result, (100, 0, 175))
                for y in range(grid.HEIGHT):
                    for x in range(grid.WIDTH):
                        if not grid.is_empty(x, y):
                            result.Rect(x * 30, y * 30, 30, 30, fill=(255, 255, 0))
                new.DrawRecursively(result, "#75BBFD")
                result.Rect(xs * 30, ys * 30, 30, 30, (255, 125, 125))
                result.Text(xs * 30, ys * 30, 'Start')
                result.Rect(xf * 30, yf * 30, 30, 30, (125, 255, 125))
                result.Text(xf * 30, yf * 30, 'Finish')

                result.Save('path.png')
                return
        opened.sort()
        # input()


map = Grid(27, 27)
map.generate_random(15)
xs, ys, xf, yf = 1, 1, 26, 26
map.setTile(xs, ys, 0)
map.setTile(xf, yf, 0)
t = timeit.Timer(lambda: find_path(map, xs, ys, xf, yf))
print(t.timeit(number=1))
