# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys
# from pathlib import Path

sys.path.insert(0, os.path.abspath('../src/spice_rack'))

# add path to our own extensions
# _ext_path = Path(__file__).parent.parent.joinpath("_exts/")
# assert _ext_path.exists()
# sys.path.append(str(_ext_path))


# -- Project information -----------------------------------------------------

project = 'Spice Rack'
copyright = '2023, Tim Robin'
author = 'Tim Robin'

# The full version, including alpha/beta/rc tags
release = '0.0.1'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc", 
    "sphinx.ext.coverage", 
    "sphinx.ext.napoleon",
    "sphinxcontrib.autodoc_pydantic",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# changes the display from "path._to._class.MyClass" to "MyClass"
add_module_names = False

# pydantic autodoc config settings:
# https://autodoc-pydantic.readthedocs.io/en/stable/index.html
autodoc_pydantic_model_show_json = True
autodoc_pydantic_settings_show_json = False
autodoc_pydantic_model_members = True
autodoc_pydantic_model_undoc_members = True
autodoc_pydantic_model_show_config_summary = False
autodoc_pydantic_model_show_config_member = False
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_settings_members = False
