import numpy as np
import sys
import time
from pathlib import Path
from functools import cache

@cache
def belief_propagation(N):
    """
        Run the belief propagation algorithm N times
    """
    np.random.seed(0)
    dim = 5000
    A = np.random.rand(dim, dim)
    x = np.ones((dim,))
    for i in range(N):
        x = np.log(np.dot(A, np.exp(x)))
        x -= np.log(np.sum(np.exp(x)))
    return x

def main(N):
    y = belief_propagation(N)
if __name__ == '__main__':
    N = int(sys.argv[1])
    rep = int(sys.argv[2])
    for i in range(rep):
        dti = time.perf_counter()
        main(N)
        print(time.perf_counter() - dti)
    belief_propagation.cache_clear()