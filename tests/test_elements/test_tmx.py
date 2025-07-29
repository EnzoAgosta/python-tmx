# type: ignore
import pytest

from PythonTmx.elements.header import Header
from PythonTmx.elements.tmx import Tmx
from PythonTmx.elements.tu import Tu
from PythonTmx.elements.tuv import Tuv
from PythonTmx.errors import (
  SerializationError,
)


def make_minimal_header():
  return Header(
    creationtool="Tool",
    creationtoolversion="1.0",
    segtype="sentence",
    tmf="tmf",
    adminlang="en",
    srclang="en-US",
    datatype="plaintext",
  )


def make_minimal_tu():
  tuv = Tuv("en-US")
  return Tu(children=[tuv])


def test_create_minimal_tmx():
  header = make_minimal_header()
  tu = make_minimal_tu()
  tmx = Tmx(header, [tu])
  assert tmx.header == header
  assert tmx._children == [tu]


def test_create_empty_tmx():
  header = make_minimal_header()
  tmx = Tmx(header, [])
  assert tmx.header == header
  assert tmx._children == []


def test_tmx_to_xml_and_from_xml(ElementFactory):
  header = make_minimal_header()
  tu = make_minimal_tu()
  tmx = Tmx(header, [tu])
  element = tmx.to_xml(factory=ElementFactory)
  tmx2 = Tmx.from_xml(element)
  assert isinstance(tmx2, Tmx)
  assert tmx2.header.creationtool == "Tool"
  assert len(tmx2._children) == 1
  assert isinstance(tmx2._children[0], Tu)


def test_tmx_from_xml_missing_header(ElementFactory):
  body = ElementFactory("body", {})
  element = ElementFactory("tmx", {})
  element.append(body)
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_from_xml_missing_body(ElementFactory):
  header = make_minimal_header().to_xml(factory=ElementFactory)
  element = ElementFactory("tmx", {})
  element.append(header)
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("not_tmx", {})
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_from_xml_multiple_headers(ElementFactory):
  header1 = make_minimal_header().to_xml(factory=ElementFactory)
  header2 = make_minimal_header().to_xml(factory=ElementFactory)
  body = ElementFactory("body", {})
  element = ElementFactory("tmx", {})
  element.append(header1)
  element.append(header2)
  element.append(body)
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_from_xml_multiple_bodies(ElementFactory):
  header = make_minimal_header().to_xml(factory=ElementFactory)
  body1 = ElementFactory("body", {})
  body2 = ElementFactory("body", {})
  element = ElementFactory("tmx", {})
  element.append(header)
  element.append(body1)
  element.append(body2)
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_from_xml_wrong_child_tag(ElementFactory):
  header = make_minimal_header().to_xml(factory=ElementFactory)
  element = ElementFactory("tmx", {})
  element.append(header)
  element.append(ElementFactory("not_body", {}))
  with pytest.raises(SerializationError):
    Tmx.from_xml(element)


def test_tmx_to_xml_invalid_header_type(ElementFactory):
  tmx = Tmx(header="not_a_header", tus=[])
  with pytest.raises(TypeError):
    tmx.to_xml(factory=ElementFactory)


def test_tmx_to_xml_invalid_tu_type(ElementFactory):
  header = make_minimal_header()
  tmx = Tmx(header, ["not_a_tu"])
  with pytest.raises(TypeError):
    tmx.to_xml(factory=ElementFactory)
