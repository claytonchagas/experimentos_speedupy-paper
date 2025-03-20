import sys
sys.path.append('/home/joaopedrolopez/Downloads/AvaliacaoExperimental/Experimentos/Tiny-GSGP-with-speedupy/adapted_for_speedupy')
from speedupy.speedupy import maybe_deterministic
"\n\nTINY_GSGP.py: A Tiny and Efficient Implementation of Geometric Semantic Genetic Programming Using Higher-Order Functions and Memoization\n\nAuthor: Alberto Moraglio (albmor@gmail.com) \n\nFeatures:\n\n- Individuals are represented directly as Python (anonymous) functions.\n\n- Crossover and mutation are higher-order functions.\n\n- Offspring functions call parent functions rather than embed their definitions (no grwoth, implicit ancestry trace).\n\n- Memoization of individuals turns time complexity of fitness evalutation from exponential to constant.\n\n- The final solution is a compiled function. It can be extracted using the ancestry trace to reconstruct its 'source code'. \n\nThis implementation is to evolve Boolean expressions. It can be easily adapted to evolve arithmetic expressions or classifiers.\n\n"
from speedupy.speedupy import initialize_speedupy, deterministic
import random
import itertools
NUMVARS = 5
DEPTH = 4
POPSIZE = 20
GENERATIONS = 30
TRUNC = 0.5
vars = ['x' + str(i) for i in range(NUMVARS)]

@maybe_deterministic
def memoize(f):
    """Add a cache memory to the input function."""
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
def randexpr(dep):
    """Create a random Boolean expression."""
    if dep == 1 or random.random() < 1.0 / (2 ** dep - 1):
        return random.choice(vars)
    if random.random() < 1.0 / 3:
        return 'not' + ' ' + randexpr(dep - 1)
    else:
        return '(' + randexpr(dep - 1) + ' ' + random.choice(['and', 'or']) + ' ' + randexpr(dep - 1) + ')'

@maybe_deterministic
def randfunct():
    """Create a random Boolean function. Individuals are represented _directly_ as Python functions."""
    re = randexpr(DEPTH)
    temp1 = ', '
    rf = eval('lambda ' + temp1.join(vars) + ': ' + re)
    rf = memoize(rf)
    rf.geno = lambda : re
    return rf

@deterministic
def targetfunct(*args):
    """Parity function of any number of input variables"""
    return args.count(True) % 2 == 1

@maybe_deterministic
def fitness(individual):
    """Determine the fitness (error) of an individual. Lower is better."""
    fit = 0
    somelists = [[True, False] for i in range(NUMVARS)]
    for element in itertools.product(*somelists):
        if individual(*element) != targetfunct(*element):
            fit = fit + 1
    return fit

@maybe_deterministic
def crossover(p1, p2):
    """
    The crossover operator is a higher order function that takes parent functions and return an offspring function.
    The definitions of parent functions are _not substituted_ in the definition of the offspring function.
    Instead parent functions are _called_ from the offspring function. This prevents exponential growth.    
    """
    mask = randfunct()
    offspring = lambda *x: p1(*x) and mask(*x) or (p2(*x) and (not mask(*x)))
    offspring = memoize(offspring)
    offspring.geno = lambda : '((' + p1.geno() + ' and ' + mask.geno() + ') or (' + p2.geno() + ' and not ' + mask.geno() + '))'
    return offspring

@maybe_deterministic
def mutation(p):
    """The mutation operator is a higher order function. The parent function is called by the offspring function."""
    temp2 = ' and '
    mintermexpr = temp2.join([random.choice([x, 'not ' + x]) for x in vars])
    temp3 = ', '
    minterm = eval('lambda ' + temp3.join(vars) + ': ' + mintermexpr)
    if random.random() < 0.5:
        offspring = lambda *x: p(*x) or minterm(*x)
        offspring = memoize(offspring)
        offspring.geno = lambda : '(' + p.geno() + ' or ' + mintermexpr + ')'
    else:
        offspring = lambda *x: p(*x) and (not minterm(*x))
        offspring = memoize(offspring)
        offspring.geno = lambda : '(' + p.geno() + ' and not ' + mintermexpr + ')'
    return offspring

@maybe_deterministic
def evolve():
    """Main function."""
    pop = [randfunct() for _ in range(POPSIZE)]
    for gen in range(GENERATIONS + 1):
        graded_pop = [(fitness(ind), ind) for ind in pop]
        sorted_pop = [ind[1] for ind in sorted(graded_pop, key=lambda x: x[0])]
        print('gen: ', gen, ' min fit: ', fitness(sorted_pop[0]), ' avg fit: ', sum((ind[0] for ind in graded_pop)) / (POPSIZE * 1.0))
        parent_pop = sorted_pop[:int(TRUNC * POPSIZE)]
        if gen == GENERATIONS:
            break
        for i in range(POPSIZE):
            par = random.sample(parent_pop, 2)
            pop[i] = mutation(crossover(par[0], par[1]))
    print('Best individual in last population: ')
    print('Query best individual in last population with all True inputs:')
    print(sorted_pop[0](*[True] * NUMVARS))

@initialize_speedupy
def main():
    evolve()
main()