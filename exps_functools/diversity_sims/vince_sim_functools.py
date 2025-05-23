import sys
import time

#sys.path.append('/home/ricardo/Downloads/selected/diversity-with-speedupy')
import numpy as np
from itertools import combinations
from collections import Counter
import datetime as dt
from functools import cache
np.random.seed(0)

@cache
def repeat_mutation_sim(G, N, L, mu=3e-08):
    """
    Generate N repeats of length L mutating at rate
    mu for G generations.
    """
    repeat_alleles = list()
    for i in range(N):
        num_mutations = np.random.poisson(L * mu * G)
        positions = np.random.choice(range(L), size=num_mutations, replace=False)
        repeat_alleles.append(tuple(positions))  # Convert each list to a tuple
    return tuple(repeat_alleles)  # Convert the list of tuples to a tuple

@cache
def count_shared_mutations(sims):
    counts = Counter()
    i = 0
    for p1, p2 in combinations(sims, 2):
        # if i % 10000000 == 0:
        #     print('\ttotal pairs counted: %d\n' % i)
        i += 1
        temp1 = set(p1)
        num_shared = len(temp1.intersection(set(p2)))
        counts[num_shared] += num_shared
    return counts

def main(N):
    x = repeat_mutation_sim(N, 12162, 156)
    t1 = dt.datetime.now()
    shared_counts = count_shared_mutations(x)
    t2 = dt.datetime.now()
    temp2 = t2 - t1
    #print(temp2.seconds)
    #print(shared_counts)
if __name__ == '__main__':
    N = float(sys.argv[1])
    rep = int(sys.argv[2])

    for i in range(rep):
        start = time.perf_counter()
        main(N)
        print(time.perf_counter() - start)