import time

def _time(f):
    def wrapper(*args):
        start = time.time()
        r = f(*args)
        end = time.time()
        print("%s timed %f" % (f.__name__, end-start) )
        return r
    return  wrapper