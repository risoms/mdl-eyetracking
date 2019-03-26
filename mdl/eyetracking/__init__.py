# -*- coding: utf-8 -*-
#!/usr/bin/python3

import pylink
from .calibration import calibration
from .eyetracking import eyetracking

__name__ = 'eyetracking'

from ._version import get_versions
__version__ = get_versions()['date']
del get_versions
