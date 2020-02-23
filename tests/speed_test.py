import timeit

def main():
    a = []
    for i in range(1000):
        a.insert(0, i)
    while len(a) > 0:
        b = a.pop(0)


t = timeit.Timer(lambda: main())
res = t.repeat(100, 1)
print(min(res))
print(max(res))
print(sum(res) / len(res))
