import numpy as np

def coinFlip(p=.5):
    #perform the binomial distribution (returns 0 or 1)
    return np.random.binomial(1,p)

import time

def _time(f):
    def wrapper(*args):
        start = time.time()
        r = f(*args)
        end = time.time()
        print("%s timed %f" % (f.__name__, end-start) )
        return r
    return  wrapper

if __name__ == '__main__':
    for i in range(10):
        print(f"Result {i}: {coinFlip()}")