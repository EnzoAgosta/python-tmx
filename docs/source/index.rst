.. toctree:: PythonTmx.classes
    :maxdepth: 4
    :hidden:

PythonTmx
=========

PythonTmx is a python library meant to make manipulating Translation
Memory Exchange (TMX) files easier and more pythonic.

Installation
------------

Install from pip

.. code:: bash

     pip install python-tmx


Description
-----------

The main philosophy behind PythonTmx is to be an abstraction layer above above
lxml/ElementTree (or any other as long as they follow a simple Protocol) when
dealing with TMX files specifically.

PythonTmx is `NOT` meant for beginners with tmx files. Though since it abstracts
away the xml parsing it doesn't necessarily require strong knowledge of xml file
handling. If you are new to tmx files and want to learn how to work with tmx
files, I recommend you to start with the
`official documentation <https://www.gala-global.org/tmx-14b>`_ to get to know
more about the format from the official source. A lot of the information in the
documentation is directly applicable to PythonTmx.

Every single element in the Tmx standard is represented by a class in PythonTmx.
The classes are named after the element they represent and use PascalCase.
For example, the ``<tuv>`` element is represented by the ``Tuv`` class.

From there every attribute of every element is accessible through dot notation.
For example, to get the ``lang`` attribute from a ``Note`` object called
``my_note`` simply do ``my_note.lang``.

Usage
-----

Creating PythonTmx objects
~~~~~~~~~~~~~~~~~~~~~~~~~~

Every object in PythonTmx can be created from an lxml Element or ElementTree
Element. Simply call the constructor with the element you want to use as the
first argument. If you want to override any attribute, simply pass it as a
keyword argument. During creation, the constructor will proritize the attributes
passed as keyword arguments over the attributes in the element.

.. note::
    You cannot create an PythonTmx object from an element and set any attribute
    to a value of None. If you want an attribute to be None but still use an
    xml element, you need to set the value to None `after` creating the object.

.. warning::
    If you pass an lxml Element to the constructor, a ValueError will be raised
    if the element's tag does not match the class name of the object you're
    trying to create. Meaning you can't create a ``Header`` object from an
    ``<tu>`` element.

Due to the fact that Tmx files can sometimes be very large, all PythonTmx objects
use `slots` to reduce memory usage. This means if you try to set or access an 
attribute that is not in the object's `slots` it will raise an
``AttributeError``.

.. note::
    When creating a PythonTmx object from an lxml Element, the constructor will
    ignore any attributes that are not in the object's `slots`.

Since PythonTmx is meant to make dealing with tmx files easier, it will also
try to coerce values to their relevant types where applicable. For example,
as long as the for the ``creationdate`` attribute follows the YYYYMMDDTHHMMSS
format, it will be converted to a ``datetime`` object when creating the object.
Same goes for the ``usagecount`` attribute, which will be converted to an
``int`` if possible.

.. note::
    If type coercion is not possible, the value parsed/provided will still be
    assigned to the attribute.

By default, any attribute meant to house an array of objects will be a list if
no children are present on the element and no value is provided as a keyword
argument.

For convenience, the ``utils`` module contains a function ``from_file`` that
will parse a tmx file and create a ``Tmx`` object from it.

Manipulating PythonTmx objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Every attribute of every element is accessible through dot notation.
For those who prefer accessing and setting attributes values using the bracket
notation, you can also do that. For example, to get the ``lang`` attribute from
a ``Note`` object called ``my_note`` you can use either ``my_note["lang"]`` or
``my_note.lang``.

.. note::
    You cannot delete attributes from a PythonTmx object. calling ``del``
    on an attribute will simply set it back to None.

Some Elements also implement the ``__iter__`` method, letting you iterate over
the children of the element a lot more easily. For example, to iterate over all
the ``Tu`` objects in a ``Tmx`` object called ``my_tmx`` you can do
``for tu in my_tmx.tus``.

.. note::
    For elements that can have multiple types of children, one type of children
    can be accessd this way. Please refer to the documentation of the element
    you're trying to iterate over for more information.

Exporting PythonTmx objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~

When it comes time to export a PythonTmx object, you can use the ``to_element``
method to get an lxml ElementTree object that can be written to a file or
string.

Note however that this is when PythonTmx will be the most restrictive in what
it lets you do. No object can be exported if it is missing `any` required
attribute. Furthermore, except for values that meant to not be strings (such as
``creationdate`` or ``notes``), any attribute that is not a string will raise
a TypeError.

.. note::
    The only attributes for which the actual value is checked are ``segtype``,
    ``pos`` and ``assoc`` as they are the only attributes that are restricted in
    what values they can have.

For convenience, the ``utils`` module contains a function ``to_file`` that will
write a ``Tmx`` object to a tmx file directly.

Examples
--------

Gathering information from a tmx file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    from PythonTmx.utils import from_file

    tmx_file = from_file("a.tmx")

    tu_count = len(tmx_file.tus)
    tuv_count = dict()
    tu_with_notes, tu_with_props = 0, 0
    tuv_with_notes, tuv_with_props = 0, 0
    old_tus = 0
    for tu in tmx_file:
        tu_with_notes += len(tu.notes)
        tu_with_props += len(tu.props)
        for tuv in tu:
            if tuv.lang not in tuv_count:
                tuv_count[tuv.lang] = 0
            else:
                tuv_count[tuv.lang] += 1
            tuv_with_notes += len(tuv.notes)
            tuv_with_props += len(tuv.props)

    print(f"""
    Total TUs: {tu_count}
    Total TUVs per language:
    {tuv_count}

    Total TUs with notes: {tu_with_notes}
    Total TUs with props: {tu_with_props}

    Total TUVs with notes: {tuv_with_notes}
    Total TUVs with props: {tuv_with_props}
    """)

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`__

.. |MIT License| image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: https://choosealicense.com/licenses/mit/
.. |Python Version from PEP 621 TOML| image:: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2FChonkyYoshi%2Fpython-tmx%2Frefs%2Fheads%2Fmain%2Fpyproject.toml
