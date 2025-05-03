import numpy as np
import sys
import time
from speedupy.speedupy import initialize_speedupy, deterministic

@deterministic
def integrand(t):
    return np.exp(t)

@deterministic
def cached_leggauss(n):
    return np.polynomial.legendre.leggauss(n)

@deterministic
def compute_quadrature(n):
    """
    Perform the Gauss-Legendre Quadrature at the prescribed order n
    """
    a = -3.0
    b = 3.0
    x, w = cached_leggauss(n)
    t = 0.5 * (x + 1) * (b - a) + a
    return sum(w * integrand(t)) * 0.5 * (b - a)

@initialize_speedupy
def main(order):
    compute_quadrature(order)

if __name__ == '__main__':
    order = int(sys.argv[1])
    dti = time.perf_counter()
    main(order)
    print(time.perf_counter() - dti)
