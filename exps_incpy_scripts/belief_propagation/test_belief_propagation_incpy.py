import numpy as np
import sys
import time

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

def main(n):
    for i in range(100, n + 1, 100):
        y = belief_propagation(i)

if __name__ == '__main__':
    n = int(sys.argv[1])
    dti = time.time()
    main(n)
    print time.time() - dti