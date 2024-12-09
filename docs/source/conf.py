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

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.intersphinx"]
autodoc_type_aliases = {
  "XmlElement": "lxml.etree._Element | xml.ElementTree.Element",
  "TmxElement": "Note | Prop | Ude | Map | Header | Tu| Tuv | Tmx |Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude",
  "SupportsNote": "Header | Tu | Tuv",
  "SupportsProp": "Header | Tu | Tuv",
  "SupportsBpt": "Tuv | Hi | Sub",
  "SupportsEpt": "Tuv | Hi | Sub",
  "SupportsIt": "Tuv | Hi | Sub",
  "SupportsPh": "Tuv | Hi | Sub",
  "SupportsHi": "Tuv | Hi | Sub",
  "SupportsUt": "Tuv | Hi | Sub",
  "SupportsSub": "Bpt | Ept | It | Ph | Ut",
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
