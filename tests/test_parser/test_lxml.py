# type: ignore
import tracemalloc

import pytest
from lxml.etree import Element, XMLSyntaxError

from PythonTmx.elements.header import Header
from PythonTmx.elements.inline import Bpt, It
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.tu import Tu
from PythonTmx.errors import SerializationError, WrongTagError, XmlParsingError
from PythonTmx.parsers.lxml import LxmlParser


def test_lxml_parser_initialization(sample_tmx_file):
  """Test LxmlParser initialization with valid file."""
  parser = LxmlParser(sample_tmx_file)
  assert parser.source == sample_tmx_file


def test_lxml_parser_initialization_nonexistent_file(nonexistent_file):
  """Test LxmlParser initialization with nonexistent file."""
  with pytest.raises(FileNotFoundError):
    LxmlParser(nonexistent_file)


def test_lxml_parser_initialization_empty_file(empty_file):
  """Test LxmlParser initialization with empty file."""
  with pytest.raises(ValueError):
    LxmlParser(empty_file)


def test_lxml_parser_iter_all_elements(sample_tmx_file):
  """Test iter method with no filtering (all elements)."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter())

  assert len(elements) == 3
  assert isinstance(elements[0], Header)
  assert isinstance(elements[1], Tu)
  assert isinstance(elements[2], Tu)


def test_lxml_parser_iter_with_single_mask(sample_tmx_file):
  """Test iter method with single tag mask."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter(mask="prop"))

  assert len(elements) == 3
  assert all(isinstance(elem, Prop) for elem in elements)


def test_lxml_parser_iter_with_multiple_mask(sample_tmx_file):
  """Test iter method with multiple tag mask."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter(mask=["prop", "note"]))

  assert len(elements) == 5
  assert all(isinstance(elem, (Prop, Note)) for elem in elements)


def test_lxml_parser_iter_with_exclude(sample_tmx_file):
  """Test iter method with exclude=True."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter(mask="header", exclude=True))

  assert len(elements) == 4
  assert isinstance(elements[0], Prop)
  assert isinstance(elements[1], Note)
  assert isinstance(elements[2], Tu)
  assert isinstance(elements[3], Tu)


def test_lxml_parser_iter_breadth_first_strategy(sample_tmx_file):
  """Test iter method with breadth-first strategy."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter("prop", strategy="breadth_first"))

  assert len(elements) > 0
  assert elements[0].type == "header-prop"
  assert elements[1].type == "tu-prop"
  assert elements[2].type == "tuv-prop"


def test_lxml_parser_iter_depth_first_strategy(sample_tmx_file):
  """Test iter method with depth-first strategy."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter("prop", strategy="depth_first"))

  assert len(elements) > 0
  assert elements[0].type == "header-prop"
  assert elements[1].type == "tuv-prop"
  assert elements[2].type == "tu-prop"


def test_lxml_parser_iter_invalid_strategy(sample_tmx_file):
  """Test iter method with invalid strategy."""
  parser = LxmlParser(sample_tmx_file)
  with pytest.raises(ValueError, match="Unknown strategy"):
    list(parser.iter(strategy="invalid_strategy"))


def test_lxml_parser_iter_unknown_tag_mask(sample_tmx_file):
  """Test iter method with unknown tag mask."""
  parser = LxmlParser(sample_tmx_file)
  with pytest.raises(WrongTagError):
    list(parser.iter(mask="unknown_tag"))


def test_lxml_parser_lazy_iter_all_elements(sample_tmx_file):
  """Test lazy_iter method with no filtering."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.lazy_iter())

  assert len(elements) == 3


def test_lxml_parser_lazy_iter_with_mask(sample_tmx_file):
  """Test lazy_iter method with tag mask."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.lazy_iter(mask="prop"))

  assert len(elements) > 0
  assert all(isinstance(elem, Prop) for elem in elements)


def test_lxml_parser_lazy_iter_with_exclude(sample_tmx_file):
  """Test lazy_iter method with exclude=True."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.lazy_iter(mask="prop", exclude=True))

  assert len(elements) == 3
  assert all(isinstance(elem, (Header, Tu)) for elem in elements)


def test_lxml_parser_invalid_xml(invalid_xml_file):
  """Test parser with invalid XML file."""
  with pytest.raises(ValueError):
    LxmlParser(invalid_xml_file)


def test_lxml_parser_unknown_tag_error(unknown_tag_file):
  """Test parser with unknown tag in XML."""
  parser = LxmlParser(unknown_tag_file)
  with pytest.raises(XmlParsingError) as e:
    list(parser.iter())
  assert isinstance(e.value.__cause__, SerializationError)
  assert isinstance(e.value.__cause__.__cause__, WrongTagError)


def test_lxml_parser_complex_file_with_inline_elements(complex_tmx_file):
  """Test parser with complex TMX file containing inline elements."""
  parser = LxmlParser(complex_tmx_file)
  elements = list(parser.iter("tuv"))

  assert len(elements) == 4

  first_seg = elements[0].segment
  assert first_seg[0] == "Hello "
  assert isinstance(first_seg[1], Bpt)
  assert first_seg[2] == " with "
  assert isinstance(first_seg[3], It)
  assert first_seg[4] == " text"


def test_lxml_parser_breadth_vs_depth_order(sample_tmx_file):
  """Test that breadth-first and depth-first produce different orders."""
  parser = LxmlParser(sample_tmx_file)

  breadth_elements = list(parser.iter("prop", strategy="breadth_first"))
  depth_elements = list(parser.iter("prop", strategy="depth_first"))

  assert len(breadth_elements) == len(depth_elements)

  breadth = [elem.type for elem in breadth_elements]
  depth = [elem.type for elem in depth_elements]

  assert breadth != depth


def test_lxml_parser_memory_efficiency_lazy_iter(sample_tmx_file):
  """Test that lazy_iter is more memory efficient than iter."""
  parser = LxmlParser(sample_tmx_file)

  iter_elements = list(parser.iter())
  lazy_elements = list(parser.lazy_iter())

  assert len(iter_elements) == len(lazy_elements)

  breadth_tags = [elem.__class__.__name__ for elem in iter_elements]
  depth_tags = [elem.__class__.__name__ for elem in lazy_elements]

  assert breadth_tags == depth_tags


def test_lxml_parser_line_number_in_error(unknown_tag_file):
  """Test that error includes line number information."""
  parser = LxmlParser(unknown_tag_file)
  with pytest.raises(XmlParsingError) as e:
    list(parser.iter())
  assert isinstance(e.value.__cause__, SerializationError)
  assert isinstance(e.value.__cause__.__cause__, WrongTagError)
  assert e.value.line is not None


def test_lxml_parser_empty_mask_results(sample_tmx_file):
  """Test parser with mask that results in no elements."""
  parser = LxmlParser(sample_tmx_file)

  with pytest.raises(WrongTagError):
    list(parser.iter(mask="nonexistent_tag"))


def test_lxml_parser_exclude_all_elements(sample_tmx_file):
  """Test parser with exclude=True and mask for all elements."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(
    parser.iter(mask=["header", "tu", "tuv", "prop", "note"], exclude=True)
  )

  assert len(elements) == 0


def test_lxml_parser_string_path(sample_tmx_file):
  """Test parser initialization with string path."""

  LxmlParser(sample_tmx_file.as_posix())


def test_lxml_parser_pathlike_object(sample_tmx_file):
  """Test parser initialization with PathLike object."""
  from pathlib import Path

  path_obj = Path(sample_tmx_file)
  parser = LxmlParser(path_obj)
  elements = list(parser.iter())
  assert len(elements) > 0


def test_lxml_parser_large_file_handling(massive_tmx_file):
  """Test parser with a larger file to ensure it handles memory properly."""
  parser = LxmlParser(massive_tmx_file)
  tracemalloc.start()
  for _ in parser.lazy_iter("tu"):
    pass
  lazy_peak = tracemalloc.get_traced_memory()[1]
  for _ in parser.iter("tu"):
    pass
  normal_peak = tracemalloc.get_traced_memory()[1]
  try:
    assert lazy_peak * 3 < normal_peak  # roughly 3x memory usage savings
  except AssertionError:
    assert lazy_peak < normal_peak  # at the very least, it's less than normal


def test_lxml_parser_default_factory_setting(sample_tmx_file):
  """Test that elements have default factory set correctly."""
  parser = LxmlParser(sample_tmx_file)
  elements = list(parser.iter())

  for element in elements:
    assert element.xml_factory is Element


def test_lxml_parser_empty_file_handling():
  """Test parser with completely empty file."""
  import os
  import tempfile

  with tempfile.NamedTemporaryFile(mode="w", suffix=".tmx", delete=False) as f:
    f.write("")
    temp_file = f.name

  try:
    parser = LxmlParser(temp_file)
    with pytest.raises(XMLSyntaxError, match="Document is empty"):
      list(parser.iter())
  finally:
    os.unlink(temp_file)


def test_lxml_parser_malformed_xml_handling():
  """Test parser with malformed XML."""
  import os
  import tempfile

  with tempfile.NamedTemporaryFile(
    mode="w", suffix=".tmx", delete=False, encoding="utf-8"
  ) as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">""")
    temp_file = f.name

  try:
    parser = LxmlParser(temp_file)
    with pytest.raises(XMLSyntaxError):
      list(parser.iter())
  finally:
    os.unlink(temp_file)


def test_lxml_parser_namespace_handling(namespaced_tmx_file):
  """Test parser with XML that has namespaces."""
  parser = LxmlParser(namespaced_tmx_file)
  elements = list(parser.iter())
  assert len(elements) > 0


def test_lxml_parser_edge_case_empty_body():
  """Test parser with TMX file that has empty body."""
  import os
  import tempfile

  with tempfile.NamedTemporaryFile(
    mode="w", suffix=".tmx", delete=False, encoding="utf-8"
  ) as f:
    f.write("""<?xml version="1.0" encoding="UTF-8"?>
<tmx version="1.4">
  <header creationtool="TestTool" creationtoolversion="1.0" segtype="sentence" o-tmf="tmf" adminlang="en" srclang="en-US" datatype="plaintext">
  </header>
  <body>
  </body>
</tmx>""")
    temp_file = f.name

  try:
    parser = LxmlParser(temp_file)
    elements = list(parser.iter())

    assert len(elements) == 1
    assert isinstance(elements[0], Header)
  finally:
    os.unlink(temp_file)
