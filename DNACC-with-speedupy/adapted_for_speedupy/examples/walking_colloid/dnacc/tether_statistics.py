"""
Explicit-tether interface
*************************

.. currentmodule:: dnacc.tether_statistics

Here, we describe the interface that must be provided by a
``tether_statistics`` object that can be used with :class:`.System` or its
more convenient subclasses (:class:`.Plates` and :class:`.Spheres`).

An ``tether_statistics`` object *must* implement the following methods:

.. function:: calc_boltz_exclusion(system, tether_info_i)

  Return :math:`\\exp( -\\beta G^{(rep)}_i )`, i.e., the Boltzmann factor
  corresponding to the free energy difference of confining a previously
  unconfined tether i.

.. function:: calc_boltz_binding_cnf(system, tether_info_i, tether_info_j)

  Returns :math:`\\exp( -\\beta G^{(cnf)}_{ij})` for the two tethers, i.e.
  the Boltzmann factor corresponding to the free energy between a system of
  two **unconfined** and a system of two bound and **confined** tethers.
  This quantitity is related to :math:`\\Delta G^{(cnf)}_{ij}` by

  .. math::

      \\Delta G^{(cnf)}_{ij} = G^{(cnf)}_{ij} - G^{(rep)}_i - G^{(rep)}_j

In both of these functions, the `tether_info` variables are dictionaries
with enough information to fully describe the tethers.  What information is
given is particular to each type of tether.  The returned value may depend
on system-wide parameters, which are accessed as attributes of `system`.

Optionally, a ``tether_statistics`` object *may* implement the following
methods to make sure that the appropriate attributes of a tether and a
system exist and have reasonable values:

.. function:: check_tether(system, tether_info_i)

  Raises a ``ValueError`` exception if the tether attributes are incomplete
  or invalid.

.. function:: check_system(system)

  Raises a ``ValueError`` exception if the system attributes are incomplete
  or invalid.

Additionally, for speed, a ``tether_statistics`` object *may* implement the
following method:

.. function:: calc_interaction_lists(system)

  For each tether i, produce a list, partners[i], that enumerates which
  tethers in system may have non-zero Boltzmann factors for binding.

  The returned list contains at least all of the tethers produced by the
  following code, but may contain others as well::

    [list(j
          for (j, info_j) in enumerate(system.tethers)
          if self.calc_boltz_binding_cnf(system, info_i, info_j) != 0.0)
     for (i, info_i) in enumerate(system.tethers)]

The common geometry that is explored in the paper (short, rod-like tethers
grafted at fixed points on parallel plates) is encoded in the
:class:`.RodsGraftedOnPlates` class.  For rods on spheres, use
:class:`.RodsGraftedOnSpheres`.

Mean field approximation
************************

For tethers grafted on parallel plates, we can make a mean field
approximation by replacing :math:`\\exp(-\\beta G^{(cnf)}_{ij})` by
:math:`M_{ab} \\sigma_b`, where :math:`\\sigma_b` is the grafting density of
b-type tethers and

.. math::

   M_{ab} = \\int dr_j\\, \\exp( - \\beta G^{(cnf)}_{ij} )

Here, i and j are any representative a-type and b-type tethers,
respectively, and the integration is over all possible grafting points of j.

The matrix :math:`M_{ij}` is related to :math:`K_{ij}` in the paper
as follows:

.. math::

   K_{ab} &= M_{ab} \\exp[-\\beta(-G^{(rep)}_a - G^{(rep)}_b)]\\\\
          &= \\int dr_j\\, \\exp( - \\beta \\Delta G^{(cnf)}_{ij} )

A ``tether_statistics`` object for use in :class:`.PlatesMeanField` *must*
implement the following methods:

.. function:: calc_boltz_exclusion( system, type_info_a )

  Return :math:`\\exp( -\\beta G^{(rep)}_a )`, i.e., the Boltzmann factor
  corresponding to the free energy difference of confining a previously
  unconfined a-type tether.

.. function:: calc_boltz_binding_cnf_bridge(system, type_info_a, type_info_b)

  Calculate :math:`M_{ab}` for binding of an a-type tether on one plate with
  a b-type tether on the opposite plate.

.. function:: calc_boltz_binding_cnf_loop(system, type_info_a, type_info_b)

  Calculate :math:`M_{ab}` for binding of an a-type tether on one plate with
  a b-type tether on the same plate.

As above, a ``tether_statistics`` object for use in
:class:`.PlatesMeanField` *may* define these checker methods:

.. function:: check_tether_type(system, type_info_a)

  Raises a ``ValueError`` exception if the tether type attributes are
  incomplete or invalid.

.. function:: check_system(system)

  Raises a ``ValueError`` exception if the system attributes are incomplete
  or invalid.
"""
__all__ = ['RodsGraftedOnPlates', 'RodsGraftedOnPlatesMeanField', '_segment_point_distance2', 'RodsGraftedOnSpheres']
import sys, os
PROJECT_FOLDER = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(PROJECT_FOLDER)
from speedupy.speedupy import deterministic
from math import sqrt, pi, asin, acos, atan, sin, cos, tan, exp, floor, ceil
from . import units
import numpy as np
import scipy
from .covertree import CoverTree

class RodsGraftedOnPlates(object):
    """Tether statistics of rigid rods grafted on plates.

    This helper class is for use with :class:`.System` and :class:`.Plates`.

    Notes
    -----
    The :class:`.System` object should have the following attributes
    (the class :class:`.Plates` has these automatically):

      dims
        2-tuple of plate dimensions along x and y axes (the plates are
        perpendicular to the z axis)

      periodic
        boolean specifying whether periodic boundary conditions should be
        imposed along x and y

      separation
        perpendicular distance between plates

    Each tether should have the following properties (see
    :func:`dnacc.System.add_tether`):

      'plate'
        identifier of plate on which the tether is grafted.  If the 'plate'
        field of two tethers are equal, a loop forms; otherwise, a bridge
        forms.

      'L'
        length of tether

      'pos'
        2-tuple (x,y) coordinate of tether grafting point

    See also
    --------
    tether_statistics :
       A full description of this object's methods.
    """

    def check_system(self, system):
        """Checks that necessary system attributes are defined and valid.

        See also
        --------
        RodsGraftedOnPlates :
            List of necessary attribute given in Notes

        tether_statistics.check_system :
            Full description of this method
        """
        try:
            if len(system.dims) != 2 or any((x <= 0 for x in system.dims)):
                raise ValueError('Invalid System.dims')
        except AttributeError:
            raise ValueError('System must define a dims attribute')
        except Exception:
            raise ValueError('Invalid dims attribute in System')
        if not hasattr(system, 'periodic'):
            raise ValueError('System must define a periodic attribute')
        try:
            if system.separation <= 0:
                raise ValueError('Invalid System.separation')
        except AttributeError:
            raise ValueError('System must define a separation attribute')
        except Exception:
            raise ValueError('Invalid separation attribute in System')

    def check_tether(self, system, tether_info_i):
        """Checks that necessary tether properties are defined and valid.

        See also
        --------
        RodsGraftedOnPlates :
            List of necessary properties given in Notes

        tether_statistics.check_tether :
            Full description of this method
        """
        if not 'plate' in tether_info_i:
            raise ValueError('Tether must have a plate attribute')
        if not 'L' in tether_info_i:
            raise ValueError('Tether length must be stored in L attribute')
        if tether_info_i['L'] < 0:
            raise ValueError('Invalid tether length')
        try:
            if len(tether_info_i['pos']) != 2:
                raise ValueError('Tether position must be an (x,y) tuple')
            if not system.periodic:
                pos = tether_info_i['pos']
                dims = system.dims
                if pos[0] < 0 or pos[0] >= dims[0] or pos[1] < 0 or (pos[1] >= dims[1]):
                    raise ValueError('Tether position, (%g nm, %g nm), lies outside system boundaries, (%g nm, %g nm)' % (pos[0] / units.nm, pos[1] / units.nm, dims[0] / units.nm, dims[1] / units.nm))
        except KeyError:
            raise ValueError('Tether must have a pos attribute')
        except Exception:
            raise ValueError('Invalid pos tether attribute')

    def _cell_list_interaction_lists(self, system, max_L):
        boxLx, boxLy = system.dims
        num_cells = [int(floor(d / max_L)) for d in system.dims]
        cell_size = [d / n for d, n in zip(system.dims, num_cells)]
        cells = np.empty((num_cells[0] + 2, num_cells[1] + 2), dtype=object)
        for i in range(-1, num_cells[0] + 1):
            for j in range(-1, num_cells[1] + 1):
                cells[i, j] = []
        if system.periodic:
            for i in range(-1, num_cells[0] + 1):
                for j in range(-1, num_cells[1] + 1):
                    cells[i, j] = cells[i % num_cells[0], j % num_cells[1]]
        for i, t in enumerate(system.tethers):
            x, y = t['pos']
            if system.periodic:
                x %= boxLx
                y %= boxLy
            cells[floor(x / cell_size[0]), floor(y / cell_size[1])].append(i)
        result = [[] for t in system.tethers]
        for i in range(num_cells[0]):
            for j in range(num_cells[1]):
                for t_ij in cells[i, j]:
                    result[t_ij] += cells[i - 1, j]
                    result[t_ij] += cells[i, j]
                    result[t_ij] += cells[i + 1, j]
                    result[t_ij] += cells[i - 1, j - 1]
                    result[t_ij] += cells[i, j - 1]
                    result[t_ij] += cells[i + 1, j - 1]
                    result[t_ij] += cells[i - 1, j + 1]
                    result[t_ij] += cells[i, j + 1]
                    result[t_ij] += cells[i + 1, j + 1]
        return result

    def calc_interaction_lists(self, system):
        """Enumerate each tether's potential interaction partners.

        See also
        --------
        RodsGraftedOnPlates :
            List of necessary system attributes and tether properties given
            in Notes

        tether_statistics.calc_interaction_lists :
            Full description of this method
        """
        boxLx, boxLy = system.dims
        max_L = 2 * max((t['L'] for t in system.tethers))
        if True:
            return self._cell_list_interaction_lists(system, max_L)
        else:
            halfBoxLx, halfBoxLy = [0.5 * x for x in (boxLx, boxLy)]
            halfBoxLx2, halfBoxLy2 = [x ** 2 for x in (halfBoxLx, halfBoxLy)]
            if system.periodic:
                positions = list()
                for t in system.tethers:
                    x, y = t['pos']
                    positions.append((x % boxLx, y % boxLy))

                def distance(ri, rj):
                    dx = ri[0] - rj[0]
                    dx2 = dx ** 2
                    if dx2 > halfBoxLx2:
                        if dx < 0.0:
                            dx2 = (dx + boxLx) ** 2
                        else:
                            dx2 = (dx - boxLx) ** 2
                    dy = ri[1] - rj[1]
                    dy2 = dy ** 2
                    if dy2 > halfBoxLy2:
                        if dy < 0.0:
                            dy2 = (dy + boxLy) ** 2
                        else:
                            dy2 = (dy - boxLy) ** 2
                    return sqrt(dx2 + dy2)
            else:
                positions = list((t['pos'] for t in system.tethers))

                def distance(ri, rj):
                    return sqrt((ri[0] - rj[0]) ** 2 + (ri[1] - rj[1]) ** 2)
            data = np.array(positions)
            tree = CoverTree(data, distance, leafsize=4)
            return tree.query_ball_tree(tree, max_L)

    def calc_boltz_binding_cnf(self, system, tether_info_i, tether_info_j):
        """Calculate :math:`\\exp(-\\beta G^{(cnf)}_{ij})`.

        See also
        --------
        RodsGraftedOnPlates :
            List of necessary system attributes and tether properties given
            in Notes

        tether_statistics.calc_boltz_binding_cnf :
            Full description of this method
        """
        h = system.separation
        ri = tether_info_i['pos']
        rj = tether_info_j['pos']
        boxL = system.dims
        Li = tether_info_i['L']
        Lj = tether_info_j['L']
        if system.periodic:
            dr = ((ri[0] - rj[0] + boxL[0] / 2) % boxL[0] - boxL[0] / 2, (ri[1] - rj[1] + boxL[1] / 2) % boxL[1] - boxL[1] / 2)
        else:
            dr = (ri[0] - rj[0], ri[1] - rj[1])
        if tether_info_i['plate'] == tether_info_j['plate']:
            d2 = dr[0] ** 2 + dr[1] ** 2
        else:
            d2 = h ** 2 + dr[0] ** 2 + dr[1] ** 2
        if d2 > (Li + Lj) ** 2:
            return 0.0
        else:
            d = sqrt(d2)
            if tether_info_i['plate'] == tether_info_j['plate']:
                return self._calc_loop_boltz(Li, Lj, h, d)
            else:
                return self._calc_bridge_boltz(Li, Lj, h, d)

    def calc_boltz_exclusion(self, system, tether_info_i):
        """Calculate :math:`\\exp(-\\beta G^{(rep)}_i)`.

        See also
        --------
        RodsGraftedOnPlates :
            List of necessary system attributes and tether properties given
            in Notes

        tether_statistics.calc_boltz_exclusion :
            Full description of this method
        """
        L = tether_info_i['L']
        h = system.separation
        return self._Omega_unbound(L, h) / (2 * pi * L ** 2)

    def _calc_boltz_exclusion(self, L, h):
        return self._Omega_unbound(L, h) / (2 * pi * L ** 2)

    def _calc_loop_boltz(self, Li, Lj, h, d):
        if h <= 0 or not abs(Li - Lj) < d < Li + Lj:
            return 0.0
        else:
            return self._Omega_loop(Li, Lj, h, d) / (2 * pi * Li ** 2 * (2 * pi * Lj ** 2) * 1 * units.M)

    def _calc_bridge_boltz(self, Li, Lj, h, d):
        if h <= 0 or d > Li + Lj:
            return 0.0
        else:
            return self._Omega_bridge(Li, Lj, h, d) / (2 * pi * Li ** 2 * (2 * pi * Lj ** 2) * 1 * units.M)

    def _Omega_unbound(self, Li, h):
        return 2 * pi * Li * min(h, Li) if h >= 0 else 0.0

    def _Omega_loop(self, Li, Lj, h, d):
        assert Li > 0
        assert Lj > 0
        assert d >= 0
        if h <= 0.0 or not abs(Li - Lj) < d < Li + Lj:
            return 0.0
        cosAlpha = (d ** 2 + Li ** 2 - Lj ** 2) / (2 * d * Li)
        sinAlpha = sqrt(1 - cosAlpha ** 2)
        cosBeta = (d ** 2 + Lj ** 2 - Li ** 2) / (2 * d * Lj)
        sinBeta = sqrt(1 - cosBeta ** 2)
        bindingRad = Li * sinAlpha
        if h >= bindingRad:
            result = pi * bindingRad
        else:
            result = 2 * asin(h / bindingRad) * bindingRad
        result /= sinAlpha * cosBeta + sinBeta * cosAlpha
        return result

    def _Omega_bridge(self, Li, Lj, h, d):
        assert Li > 0
        assert Lj > 0
        assert d >= h
        if h <= 0.0:
            return 0.0
        if d + Li <= Lj or Li + Lj <= d or Lj + d <= Li:
            return 0.0
        if Li > Lj:
            Li, Lj = (Lj, Li)
        gammaA = acos((d ** 2 + Li ** 2 - Lj ** 2) / (2 * d * Li))
        gammaB = acos((d ** 2 + Lj ** 2 - Li ** 2) / (2 * d * Lj))
        assert gammaB <= gammaA
        r = sqrt(d ** 2 - h ** 2)
        tanTheta = r / h
        theta = atan(tanTheta)
        if gammaA <= pi / 2:
            OmegaAB = 2 * pi
            thetaCut1 = pi / 2 - gammaA
            thetaCut2 = pi / 2 - gammaB
            assert thetaCut1 <= thetaCut2
            if theta > thetaCut1:
                OmegaAB -= 2 * acos(1.0 / (tan(gammaA) * tanTheta))
            if theta > thetaCut2:
                OmegaAB -= 2 * acos(1.0 / (tan(gammaB) * tanTheta))
        else:
            OmegaAB = 0
            thetaCut1 = gammaA - pi / 2
            thetaCut2 = pi / 2 - gammaB
            assert thetaCut1 <= thetaCut2
            if theta > thetaCut1:
                OmegaAB += 2 * acos(1.0 / (tan(pi - gammaA) * tanTheta))
            if theta > thetaCut2:
                OmegaAB -= 2 * acos(1.0 / (tan(gammaB) * tanTheta))
            assert 0 <= OmegaAB <= 2 * pi
        return OmegaAB * Li * sin(gammaA) / sin(gammaA + gammaB)

class RodsGraftedOnPlatesMeanField(object):
    """Mean-field tether statistics of rigid rods grafted on plates.

    This helper class is for use with :class:`.PlatesMeanField`.

    Notes
    -----
    The :class:`.PlatesMeanField` object should define the following
    attributes:

      separation
        perpendicular distance between plates

    Each tether type should have the following properties (see
    :func:`dnacc.PlatesMeanField.add_tether_type`):

      'L'
        length of tether

    See also
    --------
    tether_statistics :
       A full description of this object's methods.
    """

    def calc_boltz_binding_cnf_bridge(self, system, type_info_a, type_info_b):
        """Calculate :math:`M_{ab}` for tethers on opposite plates.

        See also
        --------
        RodsGraftedOnPlatesMeanField :
            List of necessary system attributes and tether type properties
            given in Notes

        tether_statistics.calc_boltz_binding_cnf_bridge :
            Full description of this method
        """
        h = system.separation
        La = type_info_a['L']
        Lb = type_info_b['L']
        maxL = max(La, Lb)
        minL = min(La, Lb)
        from .units import M
        stdVol = 1.0 / units.M
        if La + Lb < h:
            return 0.0
        elif h < maxL:
            if h > minL:
                return stdVol / maxL
            else:
                return stdVol * h / (La * Lb)
        else:
            return stdVol * (La + Lb - h) / (La * Lb)

    def calc_boltz_binding_cnf_loop(self, system, type_info_a, type_info_b):
        """Calculate :math:`M_{ab}` for tethers on the same plate.

        See also
        --------
        RodsGraftedOnPlatesMeanField :
            List of necessary system attributes and tether type properties
            given in Notes

        tether_statistics.calc_boltz_binding_cnf_loop :
            Full description of this method
        """
        h = system.separation
        La = type_info_a['L']
        Lb = type_info_b['L']
        maxL = max(La, Lb)
        minL = min(La, Lb)
        from .units import M
        stdVol = 1.0 / units.M
        if h < maxL:
            if h > minL:
                return stdVol / maxL
            else:
                return stdVol * h / (La * Lb)
        else:
            return stdVol / max(La, Lb)

    def calc_boltz_exclusion(self, system, type_info_a):
        """Calculate :math:`\\exp(-\\beta G^{(rep)}_a)`.

        See also
        --------
        RodsGraftedOnPlatesMeanField :
            List of necessary system attributes and tether type properties
            given in Notes

        tether_statistics.calc_boltz_exclusion :
            Full description of this method
        """
        L = type_info_a['L']
        h = system.separation
        return h / L if h < L else 1.0

    def check_system(self, system):
        """Checks that necessary system attributes are defined and valid.

        See also
        --------
        RodsGraftedOnPlatesMeanField :
            List of necessary system attributes given in Notes

        tether_statistics.check_system :
            Full description of this method
        """
        if system.separation <= 0:
            raise ValueError('Invalid separation for DNACoatedPlatesMeanField')

    def check_tether_type(self, system, type_info_a):
        """Checks that necessary tether type properties are defined and valid.

        See also
        --------
        RodsGraftedOnPlatesMeanField :
            List of necessary tether type properties given in Notes

        tether_statistics.check_tether_type :
            Full description of this method
        """
        if not 'L' in type_info_a:
            raise ValueError('Length of tethers of this type must be stored in L attribute')
        if type_info_a['L'] < 0:
            raise ValueError('Invalid tether length')

@deterministic
def _segment_point_distance2(a, b, r):
    """Minimum squared distance between r and segment joining a and b."""
    v_ba = b - a
    v_ra = r - a
    t = np.dot(v_ra, v_ba) / np.sum(v_ba ** 2)
    if t < 0:
        return np.sum((r - a) ** 2)
    elif t > 1:
        return np.sum((r - b) ** 2)
    else:
        rp = a + t * v_ba
        return np.sum((r - rp) ** 2)

class RodsGraftedOnSpheres(object):
    """Tether statistics of rigid rods grafted on Spheres.

    This helper class is for use with :class:`.System` and
    :class:`.Spheres`.

    Parameters
    ----------
    num_samples : integer
        Number of samples to use in integrations for estimating Boltzmann
        factors of binding and exclusion.

    Notes
    -----
    The :class:`.System` object should have the following attributes
    (the class :class:`.Spheres` has these automatically):

      sphere_info
        a dictionary describing each sphere in the system.  Tethers are
        attached to particular spheres, corresponding to the keys of this
        dictionary.  The entries are themselves dictionaries that should
        contain the following entries

          centre
            3-tuple (x,y,z) coordinate of the sphere centre
          radius
            radius of sphere

    Each tether should have the following properties (see
    :func:`dnacc.System.add_tether`):

      'sphere'
        identifier of sphere on which the tether is grafted, used to look up
        properties in the system's sphere_info dictionary

      'L'
        length of tether

      'pos'
        3-tuple (x,y,z) coordinate of tether grafting point **relative to
        the sphere centre** (so that spheres can be moved about easily)

    See also
    --------
    tether_statistics :
       A full description of this object's methods.
    """

    def __init__(self, num_samples=40):
        self.num_samples = 40

    def check_system(self, system):
        """Checks that necessary system attributes are defined and valid.

        See also
        --------
        RodsGraftedOnSpheres :
            List of necessary attribute given in Notes

        tether_statistics.check_system :
            Full description of this method
        """
        if not hasattr(system, 'sphere_info'):
            raise ValueError('System must define a sphere_info attribute')
        for S in system.sphere_info.values():
            try:
                if len(S['centre']) != 3:
                    raise ValueError('Sphere centre must be an (x,y,z) tuple')
            except KeyError:
                raise ValueError('Sphere must define a centre attribute')
            try:
                if S['radius'] <= 0:
                    raise ValueError('Sphere radius must be positive')
            except KeyError:
                raise ValueError('Sphere must define a radius attribute')

    def check_tether(self, system, tether_info_i):
        """Checks that necessary tether properties are defined and valid.

        See also
        --------
        RodsGraftedOnSpheres :
            List of necessary properties given in Notes

        tether_statistics.check_tether :
            Full description of this method
        """
        if 'sphere' not in tether_info_i:
            raise ValueError('Tether must have a sphere attribute')
        S_name = tether_info_i['sphere']
        if S_name not in system.sphere_info:
            raise ValueError('Missing sphere_info for sphere %s' % S_name)
        S = system.sphere_info[S_name]
        if not 'L' in tether_info_i:
            raise ValueError('Tether length must be stored in L attribute')
        if tether_info_i['L'] < 0:
            raise ValueError('Invalid tether length')
        try:
            if len(tether_info_i['pos']) != 3:
                raise ValueError('Tether position must be an (x,y,z) tuple')
        except KeyError:
            raise ValueError('Tether must have a pos attribute')
        except Exception:
            raise ValueError('Invalid pos tether attribute')
        ri = np.asarray(tether_info_i['pos'])
        R = S['radius']
        if abs(np.sum(ri ** 2) - R ** 2) > (1e-05 * R) ** 2:
            raise ValueError('Tether is not properly grafted on sphere surface')

    def calc_boltz_binding_cnf(self, system, tether_info_i, tether_info_j):
        """Calculate :math:`\\exp(-\\beta G^{(cnf)}_{ij})`.

        See also
        --------
        RodsGraftedOnSpheres :
            List of necessary system attributes and tether properties given
            in Notes

        tether_statistics.calc_boltz_binding_cnf :
            Full description of this method
        """
        return self._omega_bound(system, tether_info_i, tether_info_j) / (2 * pi * tether_info_i['L'] ** 2 * (2 * pi * tether_info_j['L'] ** 2) * 1 * units.M)

    def _omega_bound(self, system, tether_info_i, tether_info_j):
        Si = system.sphere_info[tether_info_i['sphere']]
        Sj = system.sphere_info[tether_info_j['sphere']]
        rsi = np.asarray(Si['centre'])
        rsj = np.asarray(Sj['centre'])
        Ri = Si['radius']
        Rj = Sj['radius']
        Li = tether_info_i['L']
        Lj = tether_info_j['L']
        ri = np.array(tether_info_i['pos'])
        assert abs(np.sum(ri ** 2) - Ri ** 2) < (1e-05 * Ri) ** 2
        ri += rsi
        rj = np.array(tether_info_j['pos'])
        assert abs(np.sum(rj ** 2) - Rj ** 2) < (1e-05 * Rj) ** 2
        rj += rsj
        rji = rj - ri
        d2 = np.sum(rji ** 2)
        if d2 > (Li + Lj) ** 2:
            return 0.0
        else:
            integral = 0.0
            xc = (d2 + Li ** 2 - Lj ** 2) / (2 * d2)
            rc = ri + xc * rji
            _, u, v = np.linalg.qr(np.array([rji, [1, 0, 0], [0, 1, 0], [0, 0, 1]]).T)[0].T
            R = np.sqrt(Li ** 2 - xc ** 2 * d2)
            u *= R
            v *= R

            def integrand(phi):
                r = rc + sin(phi) * u + cos(phi) * v
                if _segment_point_distance2(ri, r, rsi) < Ri ** 2:
                    return 0.0
                if _segment_point_distance2(rj, r, rsi) < Ri ** 2:
                    return 0.0
                if _segment_point_distance2(ri, r, rsj) < Rj ** 2:
                    return 0.0
                if _segment_point_distance2(rj, r, rsj) < Rj ** 2:
                    return 0.0
                return 1.0
            good_fraction = 1.0 / self.num_samples * sum((integrand(phi) for phi in np.linspace(0, 2 * pi, self.num_samples, endpoint=False)))
            d = np.sqrt(d2)
            gammaA = acos((d2 + Li ** 2 - Lj ** 2) / (2 * d * Li))
            gammaB = acos((d2 + Lj ** 2 - Li ** 2) / (2 * d * Lj))
            jacobian_fac = 1.0 / sin(gammaA + gammaB)
            return 2 * pi * R * jacobian_fac * good_fraction

    def calc_boltz_exclusion(self, system, tether_info_i):
        """Calculate :math:`\\exp(-\\beta G^{(rep)}_i)`.

        See also
        --------
        RodsGraftedOnSpheres :
            List of necessary system attributes and tether properties given
            in Notes

        tether_statistics.calc_boltz_exclusion :
            Full description of this method
        """
        Li = tether_info_i['L']
        return self._omega_unbound(system, tether_info_i) / (2 * pi * Li ** 2)

    def _omega_unbound(self, system, tether_info_i):
        Si = system.sphere_info[tether_info_i['sphere']]
        rsi = np.asarray(Si['centre'])
        Ri = Si['radius']
        ri = np.array(tether_info_i['pos'])
        assert abs(np.sum(ri ** 2) - Ri ** 2) < (1e-05 * Ri) ** 2
        ri += rsi
        Li = tether_info_i['L']
        [zHat, xHat, yHat], _ = np.linalg.qr(np.array([ri - rsi, [1, 0, 0], [0, 1, 0], [0, 0, 1]]).T)

        def integrand(phi, theta):
            r = ri + (xHat * Li * sin(theta) * cos(phi) + yHat * Li * sin(theta) * sin(phi) + zHat * Li * cos(theta))
            for Sj in system.sphere_info.values():
                rsj = np.asarray(Sj['centre'])
                Rj = Sj['radius']
                if np.all(rsj == rsi) and Ri == Rj:
                    continue
                if _segment_point_distance2(ri, r, rsj) < Rj ** 2:
                    return 0.0
            return 1.0
        good_fraction = (1.0 / self.num_samples) ** 2 * sum((integrand(phi, theta) for phi in np.linspace(0, 2 * pi, self.num_samples, endpoint=False) for theta in np.linspace(0, pi / 2.0, self.num_samples, endpoint=False)))
        return 2 * pi * Li ** 2 * good_fraction