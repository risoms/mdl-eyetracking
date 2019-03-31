# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os, sys
from pkgutil import extend_path
import pkg_resources

# set as module
__all__ = ['run','calibration','pylink','__version__']
pkg_resources.declare_namespace(__name__)

# relative paths
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

# imports
from .eyetracking import run
from .calibration import calibration

# pylink
if sys.platform == 'win32':
	from win import pylink
elif sys.platform == 'darwin':
	from osx import pylink

#----versioning
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

del os, sys, extend_path, pkg_resources