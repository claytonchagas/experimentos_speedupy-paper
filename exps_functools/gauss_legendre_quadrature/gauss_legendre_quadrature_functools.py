import numpy as np
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / 'speedupy'))
import time
from functools import cache

@cache
def integrand(t):
    return np.exp(t)

@cache
def cached_leggauss(n):
    return np.polynomial.legendre.leggauss(n)

@cache
def compute_quadrature(n):
    """
      Perform the Gauss-Legendre Quadrature at the prescribed order n
    """
    a = -3.0
    b = 3.0
    x, w = cached_leggauss(n)
    t = 0.5 * (x + 1) * (b - a) + a
    return sum(w * integrand(tuple(t))) * 0.5 * (b - a)

def main(order):
    compute_quadrature(order)
if __name__ == '__main__':
    order = int(sys.argv[1])
    rep = int(sys.argv[2])
    for i in range(rep):
        dti = time.perf_counter()
        main(order)
        print(time.perf_counter() - dti)