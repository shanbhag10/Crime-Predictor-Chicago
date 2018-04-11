#!/usr/local/bin/python3

"""Script for compiling code to external module."""

from Cython.Build import cythonize
from distutils.core import setup
from distutils.extension import Extension

extensions = [
    Extension("colocation", ["colocationAlgo.pyx"],
              include_dirs=["."]),
]

setup(
    name='colocation',
    version='0.0.1',
    description='''External module for colocationAlgo''',
    install_requires=[
        'math',
        'os',
        'sys',
        'time',
    ],
    ext_modules=cythonize(extensions)
)
