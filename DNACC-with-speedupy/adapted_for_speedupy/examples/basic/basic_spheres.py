from speedupy.speedupy import initialize_speedupy
from dnacc.derjaguin import calc_spheres_potential
import dnacc
from dnacc.units import nm
import numpy as np
import sys

@initialize_speedupy
def main(n):
    plates = dnacc.PlatesMeanField()
    plates.add_tether_type(plate='lower', sticky_end='alpha', L=20 * nm, sigma=1 / (20 * nm) ** 2)
    plates.add_tether_type(plate='upper', sticky_end='alphap', L=20 * nm, sigma=1 / (20 * nm) ** 2)
    plates.beta_DeltaG0['alpha', 'alphap'] = -8
    temp1 = plates.at(41 * nm)
    temp1.set_reference_now()
    h_arr = np.linspace(1 * nm, 40 * nm, n)
    temp2 = [plates.at(h) for h in h_arr]
    V_plate_arr = [t.free_energy_density for t in temp2]
    R = 500 * nm
    V_sphere_arr = dnacc.calc_spheres_potential(h_arr, V_plate_arr, R)
    print('# h (nm)     V (kT)')
    for h, V in zip(h_arr, V_sphere_arr):
        print(h / nm, V)
if __name__ == '__main__':
    n = int(sys.argv[1])
    main(n)