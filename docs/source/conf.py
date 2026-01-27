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
sys.path.append(os.path.abspath(os.path.join('..', '..', 'sgio')))
sys.path.append(os.path.abspath(os.path.join('..', '..')))
sys.path.append(os.path.abspath('.'))
sys.path.append('.')
print(f'sys.path: {sys.path}')

# -- Project information -----------------------------------------------------

project = 'sgio'
copyright = '2023, su tian'
author = 'su tian'

# The full version, including alpha/beta/rc tags
from sgio import __version__
release = __version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',
    'sphinx_design',
    'sphinx_copybutton',
    # 'sphinx_immaterial',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    "sphinx.ext.githubpages",
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

root_doc = 'index'

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

numfig = True
numfig_format = {
    'figure': 'Figure %s',
    'table': 'Table %s',
    'code-block': 'Listing %s',
    'section': 'Section'}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'sphinx_book_theme'
html_theme = 'pydata_sphinx_theme'
# html_theme = 'sphinx_immaterial'  # Temporarily disabled due to compatibility issue

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_title = 'SGIO'
html_static_path = ['_static']

html_theme_options = {
#     'site_url': 'https://wenbinyugroup.github.io/sgio/',
#     'repo_url': 'https://github.com/wenbinyugroup/sgio',
#     'palette': {
#         'primary': 'red'
#     },
#     # 'logo': {
#     #     'text': 'sgio',
#     # },
#     'show_nav_level': 2,
#     # "path_to_docs": "doc/source",
#     # 'use_edit_page_button': True,
#     # "use_repository_button": True,
#     # "use_issues_button": True,
#     # 'collapse_navigation': True,
#     'navigation_depth': 4,
    "announcement": "Documentation is under construction.",
}

# html_logo = '_static/logo.png'

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'groupwise'
autosummary_generate = True
