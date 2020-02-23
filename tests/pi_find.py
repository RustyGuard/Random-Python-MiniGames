import random
import math

in_circle = 0
summar = 0
r = 10000000
diff = 1000
pi = 4.0
record = pi
PI = 3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933
while True:
    p1, p2 = random.randint(-r, r), random.randint(-r, r)
    range = math.sqrt(p1 * p1 + p2 * p2)
    if range < r:
        in_circle += 1
    summar += 1
    pi = 4.0 * (float(in_circle) / float(summar))
    diffPI = abs(math.pi - pi)
    if diffPI < diff:
        diff = diffPI
        record = pi
        print(record)