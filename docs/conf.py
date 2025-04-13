# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

# Project information
project = 'SentinelPC'
copyright = '2024, SentinelPC Team'
author = 'SentinelPC Team'
release = '1.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML output options
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_title = 'SentinelPC Documentation'

# Extension configuration
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napolean_google_docstring = True
napolean_include_init_with_doc = True

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'psutil': ('https://psutil.readthedocs.io/en/latest/', None),
}

# Todo configuration
todo_include_todos = True