from collections.abc import Collection, Iterator
from functools import cache
import lxml.etree as LET

from python_tmx.xml.utils import normalize_tag


__all__ = ["LxmlBackend"]


class LxmlBackend:
  """lxml-based XML backend."""

  def make_elem(self, tag: str) -> LET.Element:
    return LET.Element(tag)

  def set_attr(self, element: LET._Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: LET._Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: LET._Element, child: LET._Element) -> None:
    parent.append(child)

  def get_attr(self, element: LET._Element, key: str, default: str | None = None) -> str | None:
    return element.get(key, default)

  def get_text(self, element: LET._Element) -> str | None:
    return element.text

  def get_tail(self, element: LET._Element) -> str | None:
    return element.tail

  def set_tail(self, element: LET._Element, tail: str | None) -> None:
    element.tail = tail

  def iter_children(
    self, element: LET._Element, tag: str | Collection[str] | None = None
  ) -> Iterator[LET._Element]:
    for descendant in element:
      descendant_tag = self.get_tag(descendant)
      if tag is None or descendant_tag in tag:
        yield descendant

  @cache
  def get_tag(self, element: LET._Element) -> str:
    return normalize_tag(element.tag)
