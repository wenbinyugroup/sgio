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
# sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath(os.path.join('..', '..', '..', '..', 'scripts')))
# sys.path.insert(0, os.path.abspath(os.path.join('..', '..', 'scripts', 'msgd')))

# print(sys.path)
# print(sys.modules)

# import msgd
# import msgd._global as mg

# print('{} {}.{}'.format(mg.NAME, mg.VERSION_MAJOR, mg.VERSION_MINOR))

# print(tags)
if not tags.has('ivabs'):
    tags.add('msg')


# -- Project information -----------------------------------------------------

project = u'SG Python Interface'
version = u'0.8'
release = u'0.8'
copyright = u'2022, Multiscale Structural Mechanics Group, Purdue University'
author = u'Su Tian, Haodong Du, Fei Tao and Wenbin Yu'



# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
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

if tags.has('ivabs'):
    rst_prolog = """
    .. |sg| replace:: CS
    .. |structure gene| replace:: cross-section
    """
else:
    rst_prolog = """
    .. |sg| replace:: SG
    .. |structure gene| replace:: structure gene
    """


language = 'en'


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_book_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# html_theme_options = {
#     # "path_to_docs": "doc/source",
#     'use_edit_page_button': True,
#     "use_repository_button": True,
#     "use_issues_button": True,
#     'collapse_navigation': True,
#     'navigation_depth': 4,
# }



# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'groupwise'
autosummary_generate = True

