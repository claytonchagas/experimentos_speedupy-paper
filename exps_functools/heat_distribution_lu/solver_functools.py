import numpy as np
import fatoracao_lu_functools as lu
import math
import heat_map_functools
from scipy.sparse import csr_matrix

class Solver:

    def __init__(self, model, delta_t):
        self.current_distribution = model.initial_distribution
        self.nx = model.nx
        self.ny = model.ny
        self.delta_t = delta_t
        self.shape = model.shape

    def solve(self):
        heat_map_functools.clearFiles('images/tmp/')
        max_difference = 1.0
        heat_map_functools.draw(tuple(self.current_distribution.flatten()))
        system_to_solve = self.get_system()
        # Convert each sparse row to a tuple of tuples
        system_to_solve_hashable = tuple(tuple(row.toarray().flatten()) for row in system_to_solve)
        while max_difference > 0 and math.log(max_difference, 10) > -7:
            linearized_distribution = self.get_array_from_distribution(self.current_distribution)
            # Convert linearized_distribution to a tuple
            linearized_distribution_hashable = tuple(linearized_distribution)
            result = np.array(lu.resolve_lu(system_to_solve_hashable, linearized_distribution_hashable))
            max_difference = self.calculate_max_difference(linearized_distribution, result)
            self.current_distribution = result.reshape(self.shape[0], self.shape[1])
            heat_map_functools.draw(self.current_distribution)
        heat_map_functools.generateGif()

    def calculate_max_difference(self, initial, final):
        return np.max(np.abs(initial - final))

    def get_system(self):
        system_dimension = self.shape[0] * self.shape[1]
        system_to_solve = []
        for i in range(system_dimension):
            current_row = [0] * system_dimension
            if self.is_boundary(i):
                current_row[i] = 1
            else:
                current_row[i] = 2 * self.delta_t * (self.nx ** 2 + self.ny ** 2) / (self.nx ** 2 * self.ny ** 2) + 1.0
                current_row[i - self.shape[0]] = -self.delta_t / self.nx ** 2
                current_row[i + self.shape[0]] = -self.delta_t / self.nx ** 2
                current_row[i - 1] = -self.delta_t / self.ny ** 2
                current_row[i + 1] = -self.delta_t / self.ny ** 2
            sparse_row = csr_matrix(current_row)
            system_to_solve.append(sparse_row)
        return system_to_solve

    def get_array_from_distribution(self, matrix):
        return matrix.reshape(self.shape[0] * self.shape[1])

    def is_boundary(self, i):
        x_size = self.shape[0]
        y_size = self.shape[1]
        if i // x_size == 0:
            return True
        if i % x_size == 0:
            return True
        if (i + 1) % x_size == 0:
            return True
        if i // x_size == y_size - 1:
            return True
        return False