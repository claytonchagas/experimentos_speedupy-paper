from solver import Solver
from model import Model
from speedupy.speedupy import initialize_speedupy
import time
import sys

@initialize_speedupy
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
    main(n)