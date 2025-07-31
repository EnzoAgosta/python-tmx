# type: ignore
# We're intentionally creating broken stuff for testing
# so we can test the error handling, so no type checking
# possible here.
from collections.abc import Callable
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement


@pytest.fixture(params=[LxmlElement, StdElement], scope="session")
def ElementFactory(request: Any) -> AnyElementFactory[..., AnyXmlElement]:
  return request.param


@pytest.fixture(scope="session")
def CustomElementLike() -> Callable[..., object]:
  class FakeAndBrokenElement:
    def __init__(self, tag=None, attrib=None, **kwargs) -> None:
      if tag is not None:
        self.tag = tag
      if attrib is not None:
        self.attrib = attrib
      self.tail = None
      for k, v in kwargs.items():
        setattr(self, k, v)

    def __iter__(self):
      yield from []

    def append(self, element: AnyXmlElement) -> None: ...

  return FakeAndBrokenElement


@pytest.fixture(scope="session")
def sample_tmx_file(tmp_path_factory) -> Path:
  """Create a sample TMX file for testing."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  tmx_file = tmp_path / "sample.tmx"

  tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0" segtype="sentence" 
          o-tmf="tmf" adminlang="en" srclang="en-US" datatype="plaintext">
    <prop type="header-prop">Header property</prop>
    <note>Header note</note>
  </header>
  <body>
    <tu tuid="1">
      <tuv xml:lang="en-US">
        <seg>Hello world</seg>
        <prop type="tuv-prop">TUV property</prop>
      </tuv>
      <tuv xml:lang="fr-FR">
        <seg>Bonjour le monde</seg>
      </tuv>
      <prop type="tu-prop">TU property</prop>
      <note>Translation unit note</note>
    </tu>
    <tu tuid="2">
      <tuv xml:lang="en-US">
        <seg>Good morning</seg>
      </tuv>
      <tuv xml:lang="fr-FR">
        <seg>Bonjour</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

  tmx_file.write_text(tmx_content, encoding="utf-8")
  return tmx_file


@pytest.fixture(scope="session")
def complex_tmx_file(tmp_path_factory) -> Path:
  """Create a complex TMX file with inline elements for testing."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  tmx_file = tmp_path / "complex.tmx"

  tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0" segtype="sentence" 
          o-tmf="tmf" adminlang="en" srclang="en-US" datatype="plaintext">
    <prop type="header-prop">Header property</prop>
    <note>Header note</note>
  </header>
  <body>
    <tu tuid="1">
      <tuv xml:lang="en-US">
        <seg>Hello <bpt i="1" type="bold">world</bpt> with <it pos="begin">italic</it> text</seg>
        <prop type="tuv-prop">TUV property</prop>
      </tuv>
      <tuv xml:lang="fr-FR">
        <seg>Bonjour <bpt i="1" type="bold">le monde</bpt> avec du texte <it pos="begin">italique</it></seg>
      </tuv>
      <prop type="tu-prop">TU property</prop>
      <note>Translation unit note</note>
    </tu>
    <tu tuid="2">
      <tuv xml:lang="en-US">
        <seg>Good <hi type="highlight">morning</hi></seg>
      </tuv>
      <tuv xml:lang="fr-FR">
        <seg>Bonjour</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

  tmx_file.write_text(tmx_content, encoding="utf-8")
  return tmx_file


@pytest.fixture(scope="session")
def invalid_xml_file(tmp_path_factory) -> Path:
  """Create an invalid XML file for testing error handling."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  xml_file = tmp_path / "invalid.xml"

  xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header>
    <prop>Unclosed tag
  </header>
  <body>
    <tu>
      <tuv>
        <seg>Content</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

  xml_file.write_text(xml_content, encoding="utf-8")
  return xml_file


@pytest.fixture(scope="session")
def unknown_tag_file(tmp_path_factory) -> Path:
  """Create a TMX file with unknown tags for testing error handling."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  tmx_file = tmp_path / "unknown_tag.tmx"

  tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0" segtype="sentence" 
          o-tmf="tmf" adminlang="en" srclang="en-US" datatype="plaintext">
    <unknown_tag>This should cause an error</unknown_tag>
  </header>
  <body>
    <tu tuid="1">
      <tuv xml:lang="en-US">
        <seg>Hello world</seg>
      </tuv>
    </tu>
  </body>
</tmx>"""

  tmx_file.write_text(tmx_content, encoding="utf-8")
  return tmx_file


@pytest.fixture(scope="session")
def empty_file(tmp_path_factory) -> Path:
  """Create an empty file for testing error handling."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  empty_file = tmp_path / "empty.txt"
  empty_file.write_text("", encoding="utf-8")
  return empty_file


@pytest.fixture(scope="session")
def nonexistent_file(tmp_path_factory) -> Path:
  """Create a path to a nonexistent file for testing error handling."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  return tmp_path / "nonexistent.tmx"


@pytest.fixture(scope="session")
def massive_tmx_file(tmp_path_factory) -> Path:
  """Create a large TMX file for testing."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  tmx_file = tmp_path / "massive.tmx"

  tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header creationtool="test" segtype="sentence" o-tmf="tmx" adminlang="en" srclang="en" datatype="plaintext" o-encoding="UTF-8">
  </header>
  <body>"""

  # Add 10_000 TUs
  for i in range(10_000):
    tmx_content += f"""
    <tu tuid="{i}">
      <tuv xml:lang="en">
        <seg>Hello world {i}</seg>
      </tuv>
      <tuv xml:lang="fr">
        <seg>Bonjour le monde {i}</seg>
      </tuv>
    </tu>"""
  tmx_content += """
  </body>
</tmx>"""

  tmx_file.write_text(tmx_content, encoding="utf-8")
  return tmx_file


@pytest.fixture(scope="session")
def namespaced_tmx_file(tmp_path_factory) -> Path:
  """Create a namespaced TMX file for testing."""
  tmp_path = tmp_path_factory.mktemp("tmx_test")
  tmx_file = tmp_path / "namespaced.tmx"

  tmx_content = """<?xml version="1.0" encoding="UTF-8"?>
<tmx:tmx version="1.4"
  xmlns:tmx="http://www.lisa.org/tmx14">
  <tmx:header creationtool="TestTool" creationtoolversion="1.0" segtype="sentence" o-tmf="tmf" adminlang="en" srclang="en-US" datatype="plaintext">
  </tmx:header>
  <tmx:body>
    <tmx:tu tuid="1">
      <tmx:tuv xml:lang="en-US">
        <tmx:seg>Hello world</tmx:seg>
      </tmx:tuv>
    </tmx:tu>
    <tmx:tu tuid="2">
      <tmx:tuv xml:lang="fr-FR">
        <tmx:seg>bonjour le monde</tmx:seg>
      </tmx:tuv>
    </tmx:tu>
  </tmx:body>
</tmx:tmx>"""

  tmx_file.write_text(tmx_content, encoding="utf-8")
  return tmx_file
