PythonTmx
=========

A robust, type-safe Python library for working with TMX (Translation Memory eXchange) files.

.. image:: https://img.shields.io/badge/python-3.13+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python 3.8+

.. image:: https://img.shields.io/badge/type%20checker-mypy-blue.svg
   :target: https://mypy-lang.org/
   :alt: Type Checker: mypy

.. image:: https://img.shields.io/badge/type%20checker-pyright-blue.svg
   :target: https://microsoft.github.io/pyright/#/
   :alt: Type Checker: pyright

.. image:: https://img.shields.io/badge/license-MIT-green.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

Overview
--------

PythonTmx is a modern Python library designed for working with TMX (Translation Memory eXchange) files. Built with type safety and flexibility in mind, it provides a robust abstraction layer over XML processing while supporting multiple XML backends.

Key Features
------------

* **Type Safety**: Full type annotations with mypy support for catching errors early
* **Backend Agnostic**: Works with any XML library (lxml, ElementTree, etc.)
* **Flexible Input**: "Lax input, strict output" philosophy for handling various data sources
* **Comprehensive Error Handling**: Detailed error messages with full stack traces
* **Memory Efficient**: Streaming parsers for large TMX files
* **Extensible**: Easy to extend with custom elements and parsers

Quick Start
-----------

Install the library:

.. code-block:: bash

   uv add python-tmx

Basic usage:

.. code-block:: python

   from PythonTmx import Tmx, Header, Tu, Tuv, SEGTYPE, DATATYPE
   from lxml.etree import Element as LxmlElement
   from xml.etree.ElementTree import Element as StdElement
   
   # Create a simple TMX file
   header = Header(
       creationtool="PythonTmx",
       creationtoolversion="1.0.0",
       segtype=SEGTYPE.SENTENCE,
       tmf="TMX",
       adminlang="en",
       srclang="en",
       datatype=DATATYPE.PLAINTEXT
   )
   
   # Create translation units
   tu = Tu(
       tuid="1",
       children=[
           Tuv(lang="en", segment=["Hello, world!"]),
           Tuv(lang="fr", segment=["Bonjour, le monde!"])
       ]
   )
   
   tmx = Tmx(header, [tu])
   
   # Serialize to XML using either lxml or stdlib
   xml_element = tmx.to_xml(factory=LxmlElement)
   # or
   xml_element = tmx.to_xml(factory=StdElement)

Architecture
------------

PythonTmx is built around several core design principles:

* **Protocol-Based Abstractions**: Uses Python protocols for maximum flexibility
* **Generic Type System**: Type-safe operations with precise type checking
* **Factory Pattern**: Backend-agnostic XML element creation
* **Separation of Concerns**: Clear boundaries between data structures and XML processing

The library consists of:

* **Core Abstractions**: Protocols and base classes for XML interaction
* **TMX Elements**: Complete implementation of all TMX element types
* **Inline Elements**: Rich text formatting and markup support
* **Parsers**: Streaming parsers for efficient file processing
* **Utilities**: Helper functions and type conversions

Installation
------------

.. code-block:: bash

   uv add python-tmx

For development:

.. code-block:: bash

   git clone https://github.com/your-repo/python-tmx.git
   cd python-tmx
   uv sync

Requirements
------------

* Python 3.13+
* Any XML library (lxml recommended for performance)

API Reference
-------------
.. toctree::
   :maxdepth: 2
   :hidden:

   PythonTmx <PythonTmx>

.. toctree::
   :maxdepth: 1

   Elements <PythonTmx.elements>
   Enums <PythonTmx.enums>
   Core <PythonTmx.core>

License
-------

This project is licensed under the MIT License - see the `LICENSE <https://github.com/your-repo/python-tmx/blob/main/LICENSE>`_ file for details.

Support
-------

* `Documentation <https://python-tmx.readthedocs.io/>`_
* `Issue Tracker <https://github.com/your-repo/python-tmx/issues>`_
* `Discussions <https://github.com/your-repo/python-tmx/discussions>`_