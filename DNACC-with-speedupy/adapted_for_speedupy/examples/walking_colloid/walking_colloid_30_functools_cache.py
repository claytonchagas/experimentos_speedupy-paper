import sys, os
from dnacc.derjaguin import calc_spheres_potential
import numpy as np
import subprocess
import operator
import dnacc
from dnacc.units import nm
plates = dnacc.PlatesMeanField()
L = 20 * nm
plates.set_tether_type_prototype(L=L, sigma=0.0)
ALPHA = plates.add_tether_type(plate='walker', sticky_end='alpha')
BETA_1 = plates.add_tether_type(plate='surface', sticky_end='beta1')
BETA_2 = plates.add_tether_type(plate='surface', sticky_end='beta2')
R = 500.0 * nm
ts = plates.tether_types

def do_it(beta_DeltaG0Mid):
    print('Working on beta_DeltaG0Mid = %g' % beta_DeltaG0Mid)
    for beta_Delta in range(0, 10):
        plates.beta_DeltaG0['alpha', 'beta1'] = beta_DeltaG0Mid - 0.5 * beta_Delta
        plates.beta_DeltaG0['alpha', 'beta2'] = beta_DeltaG0Mid + 0.5 * beta_Delta
        for S in (0.75, 0.25):
            sigma = 1 / (S * L) ** 2
            ts[ALPHA]['sigma'] = sigma * 0.5
            with open('walk-S%0.2f-G0Mid%.1f-delta%.1f.dat' % (S, beta_DeltaG0Mid, beta_Delta), 'w') as f:
                f.write('c\tF_rep (kT)\n')
                offset = 0
                for c in np.linspace(1.0, 0.0, 21):
                    ts[BETA_1]['sigma'] = c * sigma
                    ts[BETA_2]['sigma'] = (1 - c) * sigma
                    hArr = np.linspace(0.05 * L, 2.0 * L, 40)
                    VArr = [plates.at(h).free_energy_density for h in hArr]
                    Rplt = 1000.0 * R
                    betaF = calc_spheres_potential(hArr, VArr, R, Rplt)
                    (minH, minBetaF) = min(zip(hArr, betaF), key=operator.itemgetter(1))
                    if offset == 0:
                        offset = -minBetaF
                    f.write('%.2f\t%.4f\t%.4f\n' % (c, minBetaF + offset, minH / nm))

def main():
    for beta_DeltaG0Mid in range(-30, 1):
        do_it(beta_DeltaG0Mid)
main()