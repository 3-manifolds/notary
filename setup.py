#!/usr/bin/env python

from distutils.core import setup

setup(name='Notary',
    version='1.0',
    description='Automated notarization for macOS applications',
    author='Marc Culler, Nathan M. Dunfield, and Matthias Görner',
    url='https://github.com/3-manifolds/notary/',
    python_requires = '>=3',
    packages=['notarize'],
    )
