from collections.abc import Collection, Iterator
from functools import cache
import xml.etree.ElementTree as ET

from python_tmx.xml.utils import normalize_tag


__all__ = ["StandardBackend"]


class StandardBackend:
  """Standard Library-based XML backend."""

  def make_elem(self, tag: str) -> ET.Element:
    return ET.Element(tag)

  def set_attr(self, element: ET.Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: ET.Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: ET.Element, child: ET.Element) -> None:
    parent.append(child)

  def get_attr(self, element: ET.Element, key: str, default: str | None = None) -> str | None:
    return element.attrib.get(key, default)

  def get_text(self, element: ET.Element) -> str | None:
    return element.text

  def get_tail(self, element: ET.Element) -> str | None:
    return element.tail

  def set_tail(self, element: ET.Element, tail: str | None) -> None:
    element.tail = tail

  def iter_children(
    self, element: ET.Element, tag: str | Collection[str] | None = None
  ) -> Iterator[ET.Element]:
    for descendant in element:
      descendant_tag = self.get_tag(descendant)
      if tag is None or descendant_tag in tag:
        yield descendant

  @cache
  def get_tag(self, element: ET.Element) -> str:
    return normalize_tag(element.tag)
