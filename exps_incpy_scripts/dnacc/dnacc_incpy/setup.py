from setuptools import setup, Extension
import numpy

generic_module = Extension(
    'generic',
    sources=['generic.c'],
    include_dirs=[numpy.get_include()]  # Add NumPy's include directory
)

setup(
    name='generic',
    version='1.0',
    ext_modules=[generic_module],
)