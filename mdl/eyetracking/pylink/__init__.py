# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os, sys

if sys.platform == 'win32':
	from win import *
elif sys.platform == 'darwin':
	from osx import *