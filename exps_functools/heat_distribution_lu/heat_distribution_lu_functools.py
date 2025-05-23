from solver_functools import Solver
from model import Model
from functools import cache
import time
import sys

def main(n):
    dimensionality = (2, 2)
    nx = 0.15
    ny = 0.15
    delta_t = n
    start_time = time.perf_counter()
    model = Model(nx, ny, dimensionality)
    solver = Solver(model, delta_t)
    solver.solve()
    end_time = time.perf_counter()
    print(end_time - start_time)
if __name__ == '__main__':
    n = float(sys.argv[1])
    rep = int(sys.argv[2])
    for i in range(rep):
        dti = time.perf_counter()
        main(n)
        print(time.perf_counter() - dti)