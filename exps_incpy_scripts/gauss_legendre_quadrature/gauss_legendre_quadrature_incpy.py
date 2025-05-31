import numpy as np
import sys
import time

def integrand(t):
    return np.exp(t)

def cached_leggauss(n):
    return np.polynomial.legendre.leggauss(n)

def compute_quadrature(n):
    """
      Perform the Gauss-Legendre Quadrature at the prescribed order n
    """
    a = -3.0
    b = 3.0
    x, w = cached_leggauss(n)
    #(x, w) = np.polynomial.legendre.leggauss(n)
    t = 0.5 * (x + 1) * (b - a) + a
    return sum(w * integrand(t)) * 0.5 * (b - a)

def main(n):
    #for i in range(100, n + 1, 100):
        #compute_quadrature(i)
    compute_quadrature(n)

if __name__ == '__main__':
    n = int(sys.argv[1])
    dti = time.time()
    main(n)
    print time.time() - dti
