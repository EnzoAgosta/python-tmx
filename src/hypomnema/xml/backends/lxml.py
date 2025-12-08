from collections.abc import Collection, Iterator
from functools import cache

import lxml.etree as et

from hypomnema.xml.utils import normalize_tag

__all__ = ["LxmlBackend"]


class LxmlBackend:
  """lxml-based XML backend."""

  def make_elem(self, tag: str) -> et.Element:
    return et.Element(tag)

  def set_attr(self, element: et._Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: et._Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: et._Element, child: et._Element) -> None:
    parent.append(child)

  def get_attr(self, element: et._Element, key: str, default: str | None = None) -> str | None:
    return element.get(key, default)

  def get_text(self, element: et._Element) -> str | None:
    return element.text

  def get_tail(self, element: et._Element) -> str | None:
    return element.tail

  def set_tail(self, element: et._Element, tail: str | None) -> None:
    element.tail = tail

  def iter_children(
    self, element: et._Element, tag: str | Collection[str] | None = None
  ) -> Iterator[et._Element]:
    for descendant in element:
      descendant_tag = self.get_tag(descendant)
      if tag is None or descendant_tag in tag:
        yield descendant

  @cache
  def get_tag(self, element: et._Element) -> str:
    return normalize_tag(element.tag)
