#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys; 
import pkg_resources
#sys.path.append(os.path.dirname(os.path.realpath(__file__)))


__all__ = ['eyetracking']

pkg_resources.declare_namespace(__name__)

from . import *

del os, sys, pkg_resources
