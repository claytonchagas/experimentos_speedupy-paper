from __future__ import division
import sys
sys.path.append('/home/joaopedrolopez/Downloads/AvaliacaoExperimental/Experimentos/epr-with-speedupy')
from speedupy.speedupy import maybe_deterministic
from speedupy.speedupy import initialize_speedupy, deterministic
import numpy
import sys
import matplotlib
import gzip
import itertools
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib import pyplot as plt
from matplotlib import rcParams, colors
import matplotlib.gridspec as gridspec
rcParams['legend.loc'] = 'best'
rcParams['legend.fontsize'] = 8.5
rcParams['figure.facecolor'] = 'white'
rcParams['figure.edgecolor'] = 'white'
PARTICLE_SPIN = 1.0

@maybe_deterministic
def analyse(spin=PARTICLE_SPIN, PARAM=0):
    """Perform analysis on saved output files after the simulation is done"""
    alice_raw = numpy.load(gzip.open('Alice.npy.gz'))
    bob_raw = numpy.load(gzip.open('Bob.npy.gz'))
    coinc = numpy.abs(alice_raw[:, 1] * bob_raw[:, 1]) == 1.0
    alice = alice_raw[coinc]
    bob = bob_raw[coinc]
    ab = (alice[:, 0] - bob[:, 0]) % (numpy.pi * 2)
    abdeg = val(numpy.degrees(ab))
    adeg = val(numpy.degrees(alice[:, 0]))
    bdeg = val(numpy.degrees(bob[:, 0]))
    angles, o_angles, Eab, Corr = find_all_settings_used_in_simulation(abdeg, adeg, bdeg, alice, bob)
    display_results(abdeg, adeg, bdeg, alice, bob, angles, o_angles, Eab, Corr, spin, PARAM)

@deterministic
def find_all_settings_used_in_simulation(abdeg, adeg, bdeg, alice, bob):
    angles = numpy.append(numpy.unique(abdeg), [360.0])
    Eab = numpy.zeros_like(angles)
    Nab = numpy.zeros_like(angles)
    o_angles = numpy.unique(adeg)
    Corr = numpy.zeros((len(o_angles), len(o_angles)))
    for i, ax in enumerate(o_angles):
        for j in range(i, len(o_angles)):
            bx = o_angles[j]
            sel = (adeg == ax) & (bdeg == bx) | (bdeg == ax) & (adeg == bx) | (360 - adeg == ax) & (360 - bdeg == bx) | (360 - bdeg == ax) & (360 - adeg == bx)
            temp1 = alice[sel, 1] * bob[sel, 1]
            Corr[i, j] = sel.sum() > 0 and temp1.mean() or 0.0
            Corr[j, i] = Corr[i, j]
    for i, a in enumerate(angles):
        sel = (abdeg == a) | (abdeg == 360 - a)
        Nab[i] = sel.sum()
        temp2 = alice[sel, 1] * bob[sel, 1]
        Eab[i] = Nab[i] > 0.0 and temp2.mean() or 0.0
    return (angles, o_angles, Eab, Corr)

@maybe_deterministic
def display_results(abdeg, adeg, bdeg, alice, bob, angles, o_angles, Eab, Corr, spin, PARAM):
    setting_pairs = list(itertools.product(numpy.unique(adeg), numpy.unique(bdeg)))
    if len(setting_pairs) > 4:
        if PARAM == 0:
            setting_pairs = [(0, 22.5), (0, 67.5), (45, 22.5), (45, 67.5)]
        else:
            setting_pairs = setting_pairs[:PARAM]
    CHSH = []
    QM = []
    print('\nExpectation values')
    print('%10s %10s %10s %10s %10s' % ('Settings', 'N_ab', '<AB>_sim', '<AB>_qm', 'StdErr_sim'))
    for k, (i, j) in enumerate(setting_pairs):
        As = adeg == i
        Bs = bdeg == j
        Ts = As & Bs
        Ai = alice[Ts, 1]
        Bj = bob[Ts, 1]
        temp3 = Ai * Bj
        Cab_sim = temp3.mean()
        Cab_qm = QMFunc(numpy.radians(j - i), 0.5)
        desig = '%g, %g' % (i, j)
        print('%10s %10d %10.3f %10.3f %10.3f' % (desig, Ts.sum(), Cab_sim, Cab_qm, numpy.abs(Cab_sim / numpy.sqrt(Ts.sum()))))
        CHSH.append(Cab_sim)
        QM.append(Cab_qm)
    sel_same = abdeg == 0.0
    sel_oppo = abdeg == 90.0 / PARTICLE_SPIN
    temp4 = alice[sel_same, 1] * bob[sel_same, 1]
    SIM_SAME = sel_same.sum() > 0.0 and temp4.mean() or numpy.nan
    temp5 = alice[sel_oppo, 1] * bob[sel_oppo, 1]
    SIM_DIFF = sel_oppo.sum() > 0.0 and temp5.mean() or numpy.nan
    print()
    print('\tSame Angle <AB> = %+0.2f' % SIM_SAME)
    print('\tOppo Angle <AB> = %+0.2f' % SIM_DIFF)
    print('\tCHSH: <= 2.0, Sim: %0.3f, QM: %0.3f' % (abs(CHSH[0] - CHSH[1] + CHSH[2] + CHSH[3]), abs(QM[0] - QM[1] + QM[2] + QM[3])))
    X, Y = numpy.meshgrid(o_angles, o_angles)
    fig = plt.figure(figsize=plt.figaspect(0.4))
    ax1 = fig.add_subplot(121)
    ax1.plot(angles, Eab, 'm-o', label='Model: E(a,b)', lw=1)
    ax1.plot(angles, QMFunc(numpy.radians(angles), spin), 'b-+', label='QM', lw=0.5)
    bx, by = BellFunc(spin)
    ax1.plot(bx, by, 'r--', label='Bell', lw=1)
    ax1.legend()
    ax1.set_xlim(0, 360)
    ax2 = fig.add_subplot(122, projection='3d')
    ax2.plot_surface(X, Y, Corr, rstride=1, cstride=1, cmap=cm.coolwarm)
    ax2.view_init(elev=45.0, azim=45)
    plt.savefig('analysis.png', dpi=90)
    plt.show(block=False)

@deterministic
def QMFunc(a, spin):
    if spin == 0.5:
        return -numpy.cos(a)
    else:
        return numpy.cos(2 * a)

@deterministic
def BellFunc(spin):
    if spin == 0.5:
        return ([0.0, 180.0, 360.0], [-1.0, 1.0, -1.0])
    else:
        return ([0.0, 90.0, 180.0, 270.0, 360.0], [1.0, -1.0, 1.0, -1.0, 1.0])

@deterministic
def val(x):
    ANGLE_RESOLUTION = 3.75
    return numpy.round(x / ANGLE_RESOLUTION) * ANGLE_RESOLUTION

# Jeito que tava antes, tive que mudar pra ficar de acordo com os parâmetros da tabela

# if __name__ == '__main__':
#     if len(sys.argv) >= 2:
#         PARTICLE_SPIN = float(sys.argv[1])
#         PARAM = int(sys.argv[2])
#     else:
#         PARTICLE_SPIN = 1.0
#         PARAM = 0

#     @initialize_speedupy
#     def main():
#         analyse(PARTICLE_SPIN, PARAM)
#     main()


@initialize_speedupy
def main(PARAM):
    PARTICLE_SPIN = 0.5
    analyse(PARTICLE_SPIN, PARAM)

if __name__ == '__main__':
    PARAM = int(sys.argv[1])
    main(PARAM)