# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
import redsession

sys.path.insert(0, os.path.abspath("."))
sys.path.append(os.path.abspath(os.path.join(__file__, "../../")))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# General information about the project.
project = "red-session"
copyright = "2023, TheJecksMan"
author = "TheJecksMan"
version = redsession.__version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx.ext.extlinks",
]

# Don't show type hints in the signature - that just makes it hardly readable
# and we document the types anyway
autodoc_typehints = "none"

# Decides the language used for syntax highlighting of code blocks.
highlight_language = "python3"

# Use intersphinx to reference the python builtin library docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "redis-py": ("https://redis-py.readthedocs.io/en/stable/", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]

html_logo = "_static/logo_lib.png"
html_favicon = "_static/logo_lib.ico"
