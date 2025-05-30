import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from solver_incpy import Solver
from model_incpy import Model

#absolute path:
#pythonic mode:
#import sys
#sys.path.insert(0, '/home/clayton/Dt/codes/intpy_dev/')
#4Lnx mode: export PYTHONPATH='/home/clayton/Dt/codes/intpy_dev/'
#4Win mode: SET PYTHONPATH='path/to/directory'
#echo $PYTHONPATH

import time
import sys

def main(n):
    dimensionality = (2,2)
    nx = 0.15
    ny = 0.15
    delta_t = n
    start_time = time.time()
    model = Model(nx, ny, dimensionality)
    solver = Solver(model, delta_t)
    solver.solve()
    end_time = time.time()
    print end_time - start_time

if __name__ == "__main__":
    n = float(sys.argv[1])
    main(n)
