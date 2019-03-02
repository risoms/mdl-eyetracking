#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com

References:
    https://www.psychopy.org/api/hardware/pylink.html
"""
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import pylink
from calibration import calibration
from eyetracking import eyetracking