# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------
import os
import sys
import datetime
import sphinx_bootstrap_theme

# module directory
#osx
if sys.platform == 'darwin':
    sys.path.append('/Users/mdl-admin/Desktop/mdl-eyetracking/')
    sys.path.append('/anaconda3/lib/python3.6/site-packages/')
    sys.path.append(os.path.abspath('../../../'))

# -- Path setup --------------------------------------------------------------
autodoc_mock_imports = ["numpy","pandas","scipy","PIL","psychopy"]

# -- General configuration ---------------------------------------------------
# Add any Sphinx extension module names here, as strings. 
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'numpydoc',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.autosummary',
    'sphinx.ext.githubpages',
    'nbsphinx'
]

# Generate the API documentation when building
autosummary_generate = False
numpydoc_show_class_members = True

# Include the example source for plots in API docs
plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
source_suffix = ['.rst', '.md', '.ipynb']

# The master toctree document.
master_doc = 'index'

# -- Project information -----------------------------------------------------
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
import mdl

# General information about the project.
project = u'mdl-eyetracking'
author = 'Semeon Risom'
import time
copyright = u'{}, Semeon Risom'.format(time.strftime("%Y"))

#datetime = datetime.datetime.now().replace(microsecond=0).replace(second=0).isoformat()
date = datetime.date.today().isoformat()
# The short X.Y version
version = '%s'%(date)
# The full version, including alpha/beta/rc tags
release = mdl.eyetracking.__version__

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '**.ipynb_checkpoints']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# Sort by source
autodoc_member_order = 'bysource'

# -- Options for HTML output -------------------------------------------------
# The theme to use for HTML and HTML Help pages.
html_theme = 'bootstrap'
html_static_path = ['_static']
html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_theme_options = {
    'source_link_position': "footer",
    'bootswatch_theme': "paper",
    'navbar_sidebarrel': False,
    'bootstrap_version': "3",
    'navbar_links': [
         ("Glossary", "genindex"),
         ("Install", "install"),
    ],
}
# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# -- nbsphinx -------------------------------------------------
nbsphinx_allow_errors = False
nbsphinx_execute = 'never'
# This is processed by Jinja2 and inserted before each notebook
nbsphinx_prolog = r"""
{% set docname = env.doc2path(env.docname, base='doc') %}
.. only:: html
    .. role:: raw-html(raw)
        :format: html
    .. nbinfo::
        This page was generated from `{{ docname }}`__.
        Interactive online version:
        :raw-html:`<a href="https://mybinder.org/v2/gh/spatialaudio/nbsphinx/{{ env.config.release }}?filepath={{ docname }}"><img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>`
    __ https://github.com/spatialaudio/nbsphinx/blob/
        {{ env.config.release }}/{{ docname }}
.. raw:: latex
    \nbsphinxstartnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{The following section was generated from
    \sphinxcode{\sphinxupquote{\strut {{ docname | escape_latex }}}} \dotfill}}
"""
# This is processed by Jinja2 and inserted after each notebook
nbsphinx_epilog = r"""
.. raw:: latex
    \nbsphinxstopnotebook{\scriptsize\noindent\strut
    \textcolor{gray}{\dotfill\ \sphinxcode{\sphinxupquote{\strut
    {{ env.doc2path(env.docname, base='doc') | escape_latex }}}} ends here.}}
"""

# -- Options for HTMLHelp output ---------------------------------------------
# Output file base name for HTML help builder.
htmlhelp_basename = 'mdl-eyetracking'

# -- Options for manual page output ------------------------------------------
# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'mdl-eyetracking', 'mdl-eyetracking', [author], 1)
]
# -- Options for Texinfo output ----------------------------------------------
# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'mdl-eyetracking', 'mdl-eyetracking', author, 'mdl-eyetracking', 'One line description of project.', 'Miscellaneous'),
]
# -- Options for Epub output -------------------------------------------------
# Bibliographic Dublin Core info.
epub_title = project

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

# -- Extension configuration -------------------------------------------------

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}
# -- Options for todo extension ----------------------------------------------

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True