# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os, sys

if sys.platform == 'win32':
	from .win import pylink.pylink
elif sys.platform == 'darwin':
	from .osx import pylink.pylink