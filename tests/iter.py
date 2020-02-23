
class Directions:
    def __init__(self):
        self.a = 0

    def __iter__(self):
        print('dd')
        return self

    def __next__(self):
        self.a += 1
        if self.a > 7:
            raise StopIteration()
        return self.a

dirs = Directions()
for i in dirs:
    print(i)