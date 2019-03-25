#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com.

Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 Plus (5.0),
but should be compatiable with earlier systems.
"""
import datetime
date = datetime.date.today().isoformat()

NAME = 'mdl-eyelink'
VERSION = '%s'%(date)
AUTHOR = 'Semeon Risom'
AUTHOR_EMAIL = 'semeon.risom@gmail.com'
URL = 'https://semeon.io/d/mdl-eyelink'
DESCRIPTION = "mdl-eyelink: Bindings for Eyelink and Python."
# get description
with open("README.md", "r") as d:			   
	LONG_DESCRIPTION = d.read()
DOWNLOAD_URL = 'https://github.com/risoms/mdl-eyelink/'
CLASSIFIERS = [
    'Intended Audience :: Science/Research',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'License :: OSI Approved :: MIT License',
    'Topic :: Scientific/Engineering',
    'Topic :: Scientific/Engineering :: Visualization',
    'Topic :: Scientific/Engineering :: Human Machine Interfaces',
    'Topic :: Multimedia :: Graphics',
    'Operating System :: Unix',
    'Operating System :: MacOS',
    'Operating System :: Microsoft :: Windows'
]
with open("LICENSE", "r") as d:			   
	LICENSE = d.read()
INSTALL_REQUIRES = [
    'numpy','scipy','pandas','psychopy','win32api','pyobjc'
]
PACKAGES = [
    'mdl',
    'mdl.eyetracking',
]
	
from setuptools import find_packages
try:
    from setuptools import setup
    is_setuptools = True
except ImportError:
    from distutils.core import setup

# Special handling for Anaconda / Miniconda
from setuptools.config import read_configuration
required = read_configuration('setup.cfg')['options']['install_requires']

if __name__ == "__main__":
    setup(
        name=NAME,
        version=VERSION,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR,
        maintainer_email=AUTHOR_EMAIL,	
        url=URL,
        description=DESCRIPTION,
        long_description=open("README.md").read(),
		long_description_content_type="text/markdown",		
        download_url=DOWNLOAD_URL,
        classifiers=CLASSIFIERS,	  				 
        license=open("LICENSE", "r").read(),
        install_requires=INSTALL_REQUIRES,
		packages=PACKAGES,
    )