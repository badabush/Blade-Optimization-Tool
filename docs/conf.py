
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
#sys.path.insert(0, os.path.abspath('~/Documents/master-thesis/scripts/'))
sys.path.insert(0, os.path.abspath('../..'))


# -- Project information -----------------------------------------------------

project = 'BOT - Blade Optimization Tool'
copyright = '2021, Ga Man Liang'
author = 'Ga Man Liang'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc',
              'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'default'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

from sphinx.application import Sphinx
from sphinx.util.docfields import Field


def setup(app: Sphinx):
    app.add_object_type(
        'deap_restraints',
        'deap_restraints',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            Field('id', label='ID', has_arg=False, names=('id',)),
            Field('blade', label='Blade', has_arg=False, names=('blade',)),
            Field('minimum', label='Minimum', has_arg=False, names=('Minimum',)),
            Field('maximum', label='Maximum', has_arg=False, names=('Maximum',)),
            Field('default', label='Default', has_arg=False, names=('default',)),
            Field('digits', label='digits', has_arg=False, names=('digits',))
        ]
    )

    app.add_object_type(
        'ssh',
        'ssh',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            Field('host', label='Host', has_arg=False, names=('host',)),
            Field('user', label='User', has_arg=False, names=('user',)),
            Field('passwd', label='Password', has_arg=False, names=('passwd',)),
            Field('key', label='Key', has_arg=False, names=('key',)),
            Field('node', label='Node', has_arg=False, names=('node',)),
            Field('timeout', label='Timeout', has_arg=False, names=('timeout',)),
            Field('port', label='Port', has_arg=False, names=('port',))
        ]
    )

