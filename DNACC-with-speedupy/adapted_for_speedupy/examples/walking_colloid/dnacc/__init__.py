"""
.. currentmodule:: dnacc

All physical quantities are unitful, with the units given in the
:mod:`.units` module.  If you always specify units (e.g., ``20 * nm``), you
will never make a mistake.  The :mod:`.physics` module provides the value of
many physical constants (e.g., :data:`.kB`)
in compatible units.

Main Classes
------------

.. autosummary::
   :toctree: generated/

   System
   Plates
   PlatesMeanField
   Spheres

Tether Statistics
-----------------

The description of the entropic costs for binding and confining tethers on a
DNACC are encapsulated in a tether statistics object (specified when
creating a System or PlatesMeanField object).  The methods defined in such
an object are described :mod:`here <dnacc.tether_statistics>`.

.. toctree::
   :hidden:

   tether_statistics

.. autosummary::
   :toctree: generated/

   RodsGraftedOnPlates
   RodsGraftedOnPlatesMeanField
   RodsGraftedOnSpheres

Derjaguin approximation
-----------------------

.. autosummary::
   :toctree: generated/

   calc_spheres_potential

Patches
-------

These methods simplify adding patches of tethers on plates, spheres and
other systems.

.. autosummary::
   :toctree: generated/

   add_circular_patch_to_plate
   add_circular_patch_to_sphere
   stamp_tethers

Low-level interface
-------------------

If you already have an NxN matrix of binding energies, :math:`\\Delta
G_{ij}`, you can directly solve the self-consistent equations for the
probability of each tether being free, and also calculate the free energy of
binding, using a :class:`Generic` object.

.. autosummary::
   :toctree: generated/

   Generic

Utility Modules
---------------

.. toctree::
   :maxdepth: 1

   generated/dnacc.utils
   generated/dnacc.units
   generated/dnacc.physics

.. HACK to autogenerate modules but not link to them directly
   .. autosummary::
      :toctree: generated/

      utils
      units
      physics
"""
from .version import version as __version__
from .system import *
from .plates import *
from .plates_meanfield import *
from .tether_statistics import *
from .spheres import *
from .derjaguin import *
from .patches import *
from .generic import *
from . import utils