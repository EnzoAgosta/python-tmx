import lxml.etree as et
import pytest

from python_tmx.base.models import SegmentPart, SegmentPartType
from python_tmx.xml.converters import parse_segment_parts


def test_parse_segment_parts_text_only(text_only_seg_lxml_elem: et._Element):
  parts = parse_segment_parts(text_only_seg_lxml_elem)
  assert isinstance(parts, list)
  assert len(parts) == 1
  part = parts[0]
  assert part.type == SegmentPartType.STRING
  assert part.content == text_only_seg_lxml_elem.text


def test_parse_segment_parts_complex_structure(seg_with_children_1_level_lxml_elem: et._Element):
  parts = parse_segment_parts(seg_with_children_1_level_lxml_elem)
  assert isinstance(parts, list)
  assert len(parts) > 1
  assert all(isinstance(p, SegmentPart) for p in parts)


def test_parse_segment_parts_includes_child_text_and_tail(seg_with_children_1_level_lxml_elem: et._Element):
  parts = parse_segment_parts(seg_with_children_1_level_lxml_elem)
  texts = [child.text for child in seg_with_children_1_level_lxml_elem]
  tails = [child.tail for child in seg_with_children_1_level_lxml_elem]
  strings = []
  for part in parts:
    if isinstance(part.content, str):
      strings.append(part.content)
    else:
      strings.extend(subpart.content for subpart in part.content if isinstance(subpart.content, str))
  assert all(isinstance(string, str) for string in strings)
  assert all(isinstance(text, str) for text in texts)
  assert all(isinstance(tail, str) for tail in tails)
  for text in texts:
    assert text in strings
  for tail in tails:
    assert tail in strings


def test_parse_segment_parts_handles_none_input():
  assert parse_segment_parts(None) == []


def test_parse_segment_parts_valid_segment_types(seg_with_children_1_level_lxml_elem: et._Element):
  parts = parse_segment_parts(seg_with_children_1_level_lxml_elem)
  elem_parts = [part for part in parts if part.type is not SegmentPartType.STRING]
  for part, child in zip(elem_parts, seg_with_children_1_level_lxml_elem.iterchildren()):
    assert part.type.value == child.tag
  assert all(part.type is SegmentPartType.STRING for part in parts if part not in elem_parts)


def test_parse_segment_parts_invalid_segment_tag(seg_with_children_1_level_lxml_elem: et._Element):
  seg_with_children_1_level_lxml_elem.append(et.Element("wrong"))
  with pytest.raises(ValueError):
    parse_segment_parts(seg_with_children_1_level_lxml_elem)


def test_parse_segment_part_attributes_are_correctly_parsed(seg_with_children_1_level_lxml_elem: et._Element):
  parts = parse_segment_parts(seg_with_children_1_level_lxml_elem)
  elem_parts = [part for part in parts if part.type is not SegmentPartType.STRING]
  for part, child in zip(elem_parts, seg_with_children_1_level_lxml_elem.iterchildren()):
    assert child.attrib == part.attributes
