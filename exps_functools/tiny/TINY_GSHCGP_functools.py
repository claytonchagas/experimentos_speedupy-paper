import sys
import time
#sys.path.append('/home/joaopedrolopez/Downloads/AvaliacaoExperimental/Experimentos/Tiny-GSGP-with-speedupy/adapted_for_speedupy')
#"\n\nTINY_GSHCGP.py: An Implementation of Geometric Semantic ***Hill Climber*** Genetic Programming Using Higher-Order Functions and Memoization\n\nAuthor: Alberto Moraglio (albmor@gmail.com)\n\nFeatures:\n\n- Same as TINY_GSGP.py, substituting the evolutionary algorithm with a hill-climber.\n\n- The fitness landscape seen by Geometric Semantic operators is always unimodal. A hill climber can reach the optimum.\ n\n- Offspring functions call parent functions rather than embed their definitions (no grwoth, implicit ancestry trace).\n\n- Even if offspring functions embedded parent function definition, the growth is linear in the number of generation (not exponential as with crossover). \n\n- Memoization of individuals turns time complexity of fitness evalutation from linear to constant (not exponential to constant as with crossover).\n\n- Implicit ancestry trace and memoization not strictly necessary with hill-climber for efficent implementation.\n\n- The final solution is a compiled function. It can be extracted using the ancestry trace to reconstruct its 'source code'. \n\nThis implementation is to evolve Boolean expressions. It can be easily adapted to evolve arithmetic expressions or classifiers.\n\n"
from functools import cache
import random
import itertools
DEPTH = 4
GENERATIONS = 400

@cache
def memoize(f):
    """Add a cache memory to the input function."""
    f.cache = {}

    @cache
    def decorated_function(*args):
        if args in f.cache:
            return f.cache[args]
        else:
            f.cache[args] = f(*args)
            return f.cache[args]
    return decorated_function

@cache
def randexpr(dep, vars):
    """Create a random Boolean expression."""
    if dep == 1 or random.random() < 1.0 / (2 ** dep - 1):
        return random.choice(vars)
    if random.random() < 1.0 / 3:
        return 'not' + ' ' + randexpr(dep - 1, vars)
    else:
        return '(' + randexpr(dep - 1, vars) + ' ' + random.choice(['and', 'or']) + ' ' + randexpr(dep - 1, vars) + ')'

@cache
def randfunct(vars):
    """Create a random Boolean function. Individuals are represented _directly_ as Python functions."""
    re = randexpr(DEPTH, vars)
    temp1 = ', '
    rf = eval('lambda ' + temp1.join(vars) + ': ' + re)
    rf = memoize(rf)
    rf.geno = lambda: re
    return rf

@cache
def targetfunct(*args):
    """Parity function of any number of input variables"""
    return args.count(True) % 2 == 1

@cache
def fitness(individual, numvars):
    """Determine the fitness (error) of an individual. Lower is better."""
    fit = 0
    somelists = [[True, False] for i in range(numvars)]
    for element in itertools.product(*somelists):
        if individual(*element) != targetfunct(*element):
            fit = fit + 1
    return fit

@cache
def mutation(p, vars):
    """The mutation operator is a higher order function. The parent function is called by the offspring function."""
    temp2 = ' and '
    mintermexpr = temp2.join([random.choice([x, 'not ' + x]) for x in vars])
    temp3 = ', '
    minterm = eval('lambda ' + temp3.join(vars) + ': ' + mintermexpr)
    if random.random() < 0.5:
        offspring = lambda *x: p(*x) or minterm(*x)
        offspring = memoize(offspring)
        offspring.geno = lambda: '(' + p.geno() + ' or ' + mintermexpr + ')'
    else:
        offspring = lambda *x: p(*x) and (not minterm(*x))
        offspring = memoize(offspring)
        offspring.geno = lambda: '(' + p.geno() + ' and not ' + mintermexpr + ')'
    return offspring

@cache
def climb(numvars, vars):
    """Main function. As the landscape is always unimodal the climber can find the optimum."""
    curr = randfunct(vars)
    curr.fit = fitness(curr, numvars)
    for gen in range(GENERATIONS + 1):
        off = mutation(curr, vars)
        off.fit = fitness(off, numvars)
        if off.fit < curr.fit:
            curr = off
        if gen % 10 == 0:
            curr.fit

def main(numvars, vars):
    climb(numvars, tuple(vars))
if __name__ == '__main__':
    numvars = int(sys.argv[1])
    vars = ['x' + str(i) for i in range(numvars)]
    rep = int(sys.argv[2])
    for i in range(rep):
        t0 = time.perf_counter()
        main(numvars, vars)
        print(time.perf_counter() - t0)