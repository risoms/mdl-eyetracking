# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import pylink
from calibration import calibration
from eyetracking import eyetracking

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions