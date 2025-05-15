import numpy as np
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'speedupy'))
from speedupy.speedupy import initialize_speedupy, deterministic

@deterministic
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

@initialize_speedupy
def main(N):
    y = belief_propagation(N)
if __name__ == '__main__':
    N = int(sys.argv[1])
    main(N)