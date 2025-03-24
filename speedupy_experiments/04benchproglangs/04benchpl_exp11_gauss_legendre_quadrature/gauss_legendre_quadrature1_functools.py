import numpy as np
import sys
import time
from functools import cache

@cache
def integrand(t):
    return np.exp(t)

@cache
def compute_quadrature(n):
    """
      Perform the Gauss-Legendre Quadrature at the prescribed order n
    """
    a = -3.0
    b = 3.0
    (x, w) = np.polynomial.legendre.leggauss(n)
    t = 0.5 * (x + 1) * (b - a) + a
    return sum(w * integrand(t)) * 0.5 * (b - a)

def main(order):
    for i in range(100, order + 1, 100):
        compute_quadrature(i)
if __name__ == '__main__':
    order = int(sys.argv[1])
    dti = time.perf_counter()
    main(order)
    print(time.perf_counter() - dti)