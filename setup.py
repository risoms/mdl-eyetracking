#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 15:37:43 2019

@author: Semeon Risom
@email: semeon.risom@gmail.com.

Sample code to run SR Research Eyelink eyetracking system. Code is optimized for the Eyelink 1000 Plus (5.0),
but should be compatiable with earlier systems.
"""
import os
import datetime
import sys
from setuptools import find_packages
import importlib, pkg_resources

try:
    from setuptools import setup
    is_setuptools = True
except ImportError:
    from distutils.core import setup

# versioning
import versioneer
cmdclass = versioneer.get_cmdclass()
date = datetime.date.today().isoformat()

# required packages
setuptools_kwargs = {
    'install_requires': [
		'numpy >= %s'%(pkg_resources.get_distribution("numpy").version),
		'scipy >= %s'%(pkg_resources.get_distribution("scipy").version),
		'pandas >= %s'%(pkg_resources.get_distribution("pandas").version),
		'psychopy >= %s'%(pkg_resources.get_distribution("psychopy").version),
		'%s'%('win32api' if sys.platform == 'win32' else 'pyobjc'),
    ],
    'zip_safe': False
}

# setup
name = 'mdl-eyelink'
author = 'Semeon Risom'
author_email = 'semeon.risom@gmail.com'
maintainer = 'Semeon Risom'
maintainer_email = 'semeon.risom@gmail.com'
version = versioneer.get_version()
url = 'https://semeon.io/d/mdl-eyelink'
description = 'mdl-eyelink: Bindings for Eyelink and Python.'
download_url = 'https://github.com/risoms/mdl-eyelink/'
long_description = open('README.md').read()
long_description_content_type = 'text/markdown'
license_ = open('LICENSE', 'r').read()
classifiers = [
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
packages = ['mdl','mdl.eyetracking']

# init
setup(
	name=name,
	version=version,
	packages=packages,
	author=author,
	author_email=author_email,
	maintainer=maintainer,
	maintainer_email=maintainer_email,
	description=description,
	license=license_,
	cmdclass=cmdclass,
	url=url,	
	download_url=download_url,
	long_description = long_description,
	long_description_content_type = long_description_content_type,
	classifiers=classifiers,
	platforms='any',
	python_requires='>!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*!=3.5.*!=3.6.*!=3.7.*',
	**setuptools_kwargs
)