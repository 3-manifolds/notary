#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup
if sys.version_info.major != 3:
    raise RuntimeError("Use python 3")

setup(name='notabot',
    version='1.0',
    description='Automated notarization tool for macOS applications',
    long_description='''This module provides a base class for an automated notarizer.
Subclasses must provide a method for building a distribution disk image.''',
    author='Marc Culler, Nathan M. Dunfield, and Matthias Görner',
    url='https://github.com/3-manifolds/notabot/',
    classifiers = [
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
    'Operating System :: OS Independent',
    ],
    packages=['notabot'],
    )
