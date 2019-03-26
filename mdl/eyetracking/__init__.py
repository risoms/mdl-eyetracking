# -*- coding: utf-8 -*-
#!/usr/bin/python3

import pkg_resources
pkg_resources.declare_namespace(__name__)
 

import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import pylink

from eyetracking import eyetracking

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
