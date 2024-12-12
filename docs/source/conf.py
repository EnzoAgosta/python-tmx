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

extensions = [
  "sphinx.ext.autodoc",
  "sphinx.ext.napoleon",
  "sphinx.ext.intersphinx",
  "enum_tools.autoenum",
]
autodoc_type_aliases = {
  "TmxElement": "Note | Prop | Ude | Map | Header | Tu| Tuv | Tmx |Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude",
}

intersphinx_mapping = {
  "python": ("https://docs.python.org/3", None),
  "lxml": ("https://lxml.de/apidoc", None),
}

intersphinx_disabled_reftypes = ["*"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_permalinks_icon = "<span>#</span>"
html_theme = "pydata_sphinx_theme"
html_sidebars = {"**": ["page-toc"]}
html_theme_options = {
  "secondary_sidebar_items": ["sidebar-ethical-ads"],
  "external_links": [
    {"name": "Tmx Specification", "url": "https://www.gala-global.org/tmx-14b"}
  ],
}
