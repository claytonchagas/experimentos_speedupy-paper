from __future__ import division
from speedupy.speedupy import initialize_speedupy, deterministic
from scipy.linalg import eigh
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.tri import Triangulation
import numpy as np
import matplotlib.pyplot as plt
import sys

@deterministic
def coulomb_matrix(n):
    """
    Compute the Coulomb interaction matrix which has matrix elements

    C[j][k] = (psi_{2j+1},psi_{2k+1}/|x|) 

    Where psi is the normalized Hermite function
    """
    m = 2 * n + 1
    psi0 = np.zeros(m)
    psi0[0] = np.pi ** (-0.25)
    for k in range(1, m - 1):
        psi0[k + 1] = -np.sqrt(k / (k + 1.0)) * psi0[k - 1]
    A = np.eye(m) / 2
    A[0, 0] = 0.5
    A[0, 1:] = psi0[:-1] / np.sqrt(2 * np.sqrt(np.pi) * np.arange(1, m))
    A[1:, 0] = A[0, 1:]
    for j in range(1, m):
        for k in range(1, j):
            A[j, k] = psi0[j] * psi0[k - 1] / np.sqrt(2 * k) + np.sqrt(j / k) * A[j - 1, k - 1]
            A[k, j] = A[j, k]
    B = np.zeros((n, n))
    B[0, 0] = 2 / np.sqrt(np.pi)
    for k in range(1, n):
        B[0, k] = (4 * A[1, 2 * k] - 2 * np.sqrt(k) * B[0, k - 1]) / np.sqrt(2 * (2 * k + 1))
    B[1:, 0] = B[0, 1:]
    for j in range(1, n):
        for k in range(1, n):
            B[j, k] = (4 * A[2 * j + 1, 2 * k] - 2 * np.sqrt(k) * B[j, k - 1]) / np.sqrt(2 * (2 * k + 1))
    C = np.zeros((n, n))
    for j in range(n):
        for k in range(n):
            if not (j + k) % 2:
                C[j, k] = B[j, k]
    return C

@deterministic
def hermite_functions(x, n):
    """
    Evaluate the first n normalized Hermite functions on a grid x
    """
    m = len(x)
    psi = np.zeros((m, n))
    psi[:, 0] = np.pi ** (-0.25) * np.exp(-x ** 2 / 2)
    psi[:, 1] = np.sqrt(2) * x * psi[:, 0]
    a = np.sqrt(np.arange(0, n) / 2)
    for k in range(1, n - 1):
        psi[:, k + 1] = (x * psi[:, k] - a[k] * psi[:, k - 1]) / a[k + 1]
    return psi
if __name__ == '__main__':
    N = int(sys.argv[1])

    @initialize_speedupy
    def main(N):
        x = np.linspace(-10, 10, N)
        yy, xx = np.meshgrid(x, x)
        Q1 = (xx + yy) / np.sqrt(2)
        Q2 = (xx - yy) / np.sqrt(2)
        n = 16
        hf = hermite_functions(x, 2 * n + 1)
        phi = hf[:, 1::2]
        H0 = np.diag((3 + 4 * np.arange(n)) / 2)
        C = coulomb_matrix(n)
        H = H0 + C
        nu, Vhat = eigh(H)
        V = np.dot(phi, Vhat)
        Psi = np.outer(hf[:, 0], V[:, 0])
        psi = Psi.flatten()
        q1 = Q1.flatten()
        q2 = Q2.flatten()
        dex = np.where(q1 ** 2 + q2 ** 2 < 10)[0]
        tri = Triangulation(q2[dex], q1[dex])
        fig = plt.figure(1)
        ax = fig.add_subplot(projection='3d')
        ax.plot_trisurf(tri, psi[dex], cmap=cm.jet, linewidth=0.2)
        ax.set_xlabel('$q_1$', fontsize=18)
        ax.set_ylabel('$q_2$', fontsize=18)
        plt.show(block=False)
    main(N)