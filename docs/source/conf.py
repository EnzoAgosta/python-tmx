import sys
from pathlib import Path

sys.path.insert(0, str(Path("..", "..", "src", "PythonTmx").resolve()))
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "PythonTmx"
copyright = "2024, Enzo Agosta"
author = "Enzo Agosta"
release = "0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

templates_path = ["_templates"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_permalinks_icon = "<span>#</span>"
html_theme = "pydata_sphinx_theme"
html_static_path = ["_static"]
html_sidebars = {"**": ["sidebar-nav-bs", "page-toc"]}
html_theme_options: dict = {"secondary_sidebar_items": []}
