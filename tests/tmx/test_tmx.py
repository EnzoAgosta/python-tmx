import lxml.etree as et
import pytest

from python_tmx.tmx.models import Header, Tmx, Tu
from python_tmx.tmx.parse import parse_tmx


def test_parse_tmx_from_valid_element(tmx_lxml_elem: et._Element):
  tmx = parse_tmx(tmx_lxml_elem)
  assert isinstance(tmx, Tmx)
  assert isinstance(tmx.version, str)
  assert tmx.version == tmx_lxml_elem.attrib["version"]
  assert isinstance(tmx.header, Header)
  assert isinstance(tmx.body, list)
  assert all(isinstance(tu, Tu) for tu in tmx.body)
  assert len(tmx.body) == len(tmx_lxml_elem.findall(".//tu"))


def test_parse_tmx_incorrect_tag_raises(tmx_lxml_elem: et._Element):
  tmx_lxml_elem.tag = "wrong"
  with pytest.raises(ValueError):
    parse_tmx(tmx_lxml_elem)


def test_parse_tmx_missing_header_raises(tmx_lxml_elem: et._Element):
  header = tmx_lxml_elem.find("header")
  tmx_lxml_elem.remove(header)
  with pytest.raises(ValueError, match="no header"):
    parse_tmx(tmx_lxml_elem)


def test_parse_tmx_missing_body_raises(tmx_lxml_elem: et._Element):
  body = tmx_lxml_elem.find("body")
  tmx_lxml_elem.remove(body)
  with pytest.raises(ValueError, match="no body"):
    parse_tmx(tmx_lxml_elem)


def test_parse_tmx_empty_body_returns_empty_list(tmx_lxml_elem: et._Element):
  body = tmx_lxml_elem.find("body")
  for child in list(body):
    body.remove(child)
  tmx = parse_tmx(tmx_lxml_elem)
  assert isinstance(tmx, Tmx)
  assert tmx.body == []
