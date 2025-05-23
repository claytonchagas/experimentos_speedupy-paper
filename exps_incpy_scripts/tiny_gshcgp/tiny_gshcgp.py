"\n\nTINY_GSHCGP.py: An Implementation of Geometric Semantic ***Hill Climber*** Genetic Programming Using Higher-Order Functions and Memoization\n\nAuthor: Alberto Moraglio (albmor@gmail.com)\n\nFeatures:\n\n- Same as TINY_GSGP.py, substituting the evolutionary algorithm with a hill-climber.\n\n- The fitness landscape seen by Geometric Semantic operators is always unimodal. A hill climber can reach the optimum.\n\n- Offspring functions call parent functions rather than embed their definitions (no grwoth, implicit ancestry trace).\n\n- Even if offspring functions embedded parent function definition, the growth is linear in the number of generation (not exponential as with crossover). \n\n- Memoization of individuals turns time complexity of fitness evalutation from linear to constant (not exponential to constant as with crossover).\n\n- Implicit ancestry trace and memoization not strictly necessary with hill-climber for efficent implementation.\n\n- The final solution is a compiled function. It can be extracted using the ancestry trace to reconstruct its 'source code'. \n\nThis implementation is to evolve Boolean expressions. It can be easily adapted to evolve arithmetic expressions or classifiers.\n\n"

import sys
from speedupy.speedupy import maybe_deterministic, initialize_speedupy, deterministic
import random
import itertools

DEPTH = 4
GENERATIONS = 400

@maybe_deterministic
def memoize(f):
    f.cache = {}
    @maybe_deterministic
    def decorated_function(*args):
        if args in f.cache:
            return f.cache[args]
        else:
            f.cache[args] = f(*args)
            return f.cache[args]
    return decorated_function

@maybe_deterministic
def randexpr(dep, vars):
    if dep == 1 or random.random() < 1.0 / (2 ** dep - 1):
        return random.choice(vars)
    if random.random() < 1.0 / 3:
        return 'not ' + randexpr(dep - 1, vars)
    else:
        return '(' + randexpr(dep - 1, vars) + ' ' + random.choice(['and', 'or']) + ' ' + randexpr(dep - 1, vars) + ')'

@maybe_deterministic
def randfunct(vars):
    re = randexpr(DEPTH, vars)
    rf = eval('lambda ' + ', '.join(vars) + ': ' + re)
    rf = memoize(rf)
    rf.geno = lambda: re
    return rf

@deterministic
def targetfunct(*args):
    return args.count(True) % 2 == 1

@maybe_deterministic
def fitness(individual, numvars):
    fit = 0
    somelists = [[True, False] for _ in range(numvars)]
    for element in itertools.product(*somelists):
        if individual(*element) != targetfunct(*element):
            fit += 1
    return fit

@maybe_deterministic
def mutation(p, vars):
    mintermexpr = ' and '.join([random.choice([x, 'not ' + x]) for x in vars])
    minterm = eval('lambda ' + ', '.join(vars) + ': ' + mintermexpr)
    if random.random() < 0.5:
        offspring = lambda *x: p(*x) or minterm(*x)
        offspring = memoize(offspring)
        offspring.geno = lambda: '(' + p.geno() + ' or ' + mintermexpr + ')'
    else:
        offspring = lambda *x: p(*x) and not minterm(*x)
        offspring = memoize(offspring)
        offspring.geno = lambda: '(' + p.geno() + ' and not ' + mintermexpr + ')'
    return offspring

@maybe_deterministic
def climb(numvars, vars):
    curr = randfunct(vars)
    curr.fit = fitness(curr, numvars)
    for gen in range(GENERATIONS + 1):
        off = mutation(curr, vars)
        off.fit = fitness(off, numvars)
        if off.fit < curr.fit:
            curr = off
        if gen % 10 == 0:
            pass  # logging pode ser adicionado aqui

@initialize_speedupy
def main(numvars, vars):
    climb(numvars, vars)

if __name__ == '__main__':
    numvars = int(sys.argv[1])
    vars = ['x' + str(i) for i in range(numvars)]
    main(numvars, vars)
