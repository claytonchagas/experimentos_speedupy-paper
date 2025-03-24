import sys
sys.path.append('/home/esc/Modelos/experimentos_speedupy_mar25/DNACC-with-speedupy/adapted_for_speedupy/examples/basic')
from speedupy.speedupy import maybe_deterministic
'\n=======================================================================\nConsistent units definitions for molecular systems (:mod:`dnacc.units`)\n=======================================================================\n\n.. currentmodule:: dnacc.units\n\nThe internal base units are GROMACS units, which are useful,\nconsistent, and internally yield numbers that are close to 1 in\nmost atomistic setups:\n\n- Length = nm\n- Mass = amu\n- Time = ps (together yield natural energy unit of kJ/mol)\n- Current = e / ps\n- Temperature = K\n\nElectrostatic formulas have all the usual SI prefactors.  We don\'t\nbother with the units relating to light (cd and related units) since\nthey are mostly irrelevant for condensed matter simulations.\n\nInitially, we express the SI base units in terms of GROMACS units,\nthen derive all other units from them.  For internal convenience,\nwe actually use g instead of kg for defining masses.\n\nAlmost all unit definitions also set up the related prefixed units\nfrom femto-X to tera-X.\n\nWhenever you read in a unitful quantity from the user, multiply\nit by the relevant units.  For example,\n\n   >>> myLength = fields[5] * units.nm\n\nWhenever you output unitful quantities, divide by the units you want\nto use.  For example,\n\n   >>> print("Total energy = %.2f kcal/mol" %\n             (E / (units.kcal / units.mol)))\n\n.. note::\n\n  The unit "Celsius" is not defined explicitly to not confuse it with\n  "Coulombs".\n\nBase units\n++++++++++\n\nAll of these can be prefixed with the usual SI prefixes, e.g. ``nm`` for\nnanometer.\n\n.. autodata:: m\n.. autodata:: g\n.. autodata:: s\n.. autodata:: Ampere\n.. autodata:: K\n.. autodata:: mol\n\nBy default, the unit for Amperes is :data:`.Ampere`, not ``A`` as usual.\nTo change this behaviour, call :func:`.add_amperes_unit`.\n\n.. autofunction:: add_amperes_unit\n\nDerived units\n+++++++++++++\n\nMost of these can also be prefixed with the usual SI prefixes, e.g. ``pN``\nfor pico-Newton.\n\n.. autodata:: Hz\n.. autodata:: rad\n.. autodata:: sr\n.. autodata:: N\n.. autodata:: Pa\n.. autodata:: J\n.. autodata:: W\n.. autodata:: C\n.. autodata:: V\n.. autodata:: F\n.. autodata:: Ohm\n.. autodata:: S\n.. autodata:: Wb\n.. autodata:: T\n.. autodata:: H\n\nNon-SI units\n++++++++++++\n\n.. autodata:: min\n.. autodata:: h\n.. autodata:: d\n.. autodata:: degree\n.. autodata:: arcmin\n.. autodata:: arcsec\n.. autodata:: ha\n.. autodata:: L\n.. autodata:: t\n\nPhysics units\n+++++++++++++\n\nSome units which are more properly considered physical constants are\ndefined in the :mod:`.physics` module.\n\n.. autodata:: G\n.. autodata:: bar\n.. autodata:: atm\n.. autodata:: Torr\n.. autodata:: mmHg\n.. autodata:: P\n\nChemistry units\n+++++++++++++++\n\nUnits that pop up regularly in chemistry.\n\n.. autodata:: AA\n.. autodata:: cal\n.. autodata:: kcal\n.. autodata:: M\n.. autodata:: cc\n\n'
from math import pi
_GSL_CONST_MKSA_UNIFIED_ATOMIC_MASS = 1.660538782e-27
_GSL_CONST_MKSA_ELECTRON_CHARGE = 1.602176487e-19
_GSL_CONST_NUM_AVOGADRO = 6.02214199e+23
_GSL_CONST_MKSA_GAUSS = 0.0001
_GSL_CONST_MKSA_BAR = 100000.0
_GSL_CONST_MKSA_STD_ATMOSPHERE = 101325.0
_GSL_CONST_MKSA_TORR = 133.322368421
_GSL_CONST_MKSA_METER_OF_MERCURY = 133322.368421
m = 1000000000.0
g = 0.001 / _GSL_CONST_MKSA_UNIFIED_ATOMIC_MASS
s = 1000000000000.0
Ampere = 1.0 / _GSL_CONST_MKSA_ELECTRON_CHARGE / s
K = 1.0
mol = _GSL_CONST_NUM_AVOGADRO

@maybe_deterministic
def add_amperes_unit():
    """Define ``A`` as the unit Ampere.

    By default, this definition is disabled to avoid accidental mixups with
    the unit for Angstroms (:data:`.AA`).  This mixup can result in some
    thoroughly puzzling bugs."""
    global A
    A = Ampere
_SI_prefixes = {'f': 1e-15, 'p': 1e-12, 'n': 1e-09, 'u': 1e-06, 'm': 0.001, 'c': 0.01, 'd': 0.1, 'da': 10.0, 'h': 100.0, 'k': 1000.0, 'M': 1000000.0, 'G': 1000000000.0, 'T': 1000000000000.0}

@maybe_deterministic
def _add_prefixes(name, realname=None):
    """Add standard SI prefixes to a base unit."""
    globs = globals()
    val = globs[realname or name]
    for prefix, factor in list(_SI_prefixes.items()):
        globs[prefix + name] = factor * val
_add_prefixes('m')
_add_prefixes('g')
_add_prefixes('s')
_add_prefixes('A', 'Ampere')
_add_prefixes('K')
_add_prefixes('mol')
Hz = 1 / s
rad = m / m
sr = m ** 2 / m ** 2
N = kg * m / s ** 2
Pa = N / m ** 2
J = N * m
W = J / s
C = Ampere * s
V = J / C
F = C / V
Ohm = V / Ampere
S = 1 / Ohm
Wb = J / Ampere
T = Wb / m ** 2
H = Wb / Ampere
_add_prefixes('Hz')
_add_prefixes('N')
_add_prefixes('Pa')
_add_prefixes('J')
_add_prefixes('W')
_add_prefixes('C')
_add_prefixes('V')
_add_prefixes('F')
_add_prefixes('Ohm')
min = 60 * s
h = 60 * min
d = 24 * h
degree = pi / 180.0
arcmin = degree / 60.0
arcsec = arcmin / 60.0
ha = 10000 * m ** 2
L = dm ** 3
t = 1000.0 * kg
G = _GSL_CONST_MKSA_GAUSS * T
bar = _GSL_CONST_MKSA_BAR * Pa
_add_prefixes('bar')
atm = _GSL_CONST_MKSA_STD_ATMOSPHERE * Pa
Torr = _GSL_CONST_MKSA_TORR * Pa
mmHg = 0.001 * _GSL_CONST_MKSA_METER_OF_MERCURY * Pa
P = 1 * g / (cm * s)
_add_prefixes('P')
AA = 1e-10 * m
cal = 4.184 * J
'Thermochemical calorie\n\n.. note::\n\n  The calorie here is the thermochemical calorie (4.184 J), not the\n  International Steam Table calorie (4.1868 J) used in GSL.\n'
kcal = 1000.0 * cal
M = mol / L
_add_prefixes('M')
cc = cm ** 3