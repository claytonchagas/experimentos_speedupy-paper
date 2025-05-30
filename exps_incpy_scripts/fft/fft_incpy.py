import numpy as np
import numpy.random as rn
import sys
import time

def compute_FFT(n):
    """
        Compute the FFT of an n-by-n matrix of data
    """
    rn.seed(0)
    matrix = rn.rand(n, n) + 1j * rn.randn(n, n)
    result = np.fft.fft2(matrix)
    result = np.abs(result)
    return result

def main(n):
    for i in range(100, n + 1, 100):
        compute_FFT(i)

if __name__ == '__main__':
    n = int(sys.argv[1])
    dt1 = time.time()
    main(n)
    print time.time() - dt1