from collections.abc import Collection
from typing import Iterator
import xml.etree.ElementTree as ET

__all__ = ["StrictBackend"]


class StrictBackend:
  """
  A test-only backend that passes integers (IDs) to handlers instead of objects.

  This guarantees handlers NEVER access underlying XML objects directly (e.g.,
  via .tag or .attrib). Any attempt to do so will result in an AttributeError
  on the integer.
  """

  def __init__(self) -> None:
    # We use a dict to map IDs to real ElementTree objects internally
    self._store: dict[int, ET.Element] = {}
    self._counter = 0

  def _register(self, element: ET.Element) -> int:
    self._counter += 1
    self._store[self._counter] = element
    return self._counter

  def make_elem(self, tag: str) -> int:
    elem = ET.Element(tag)
    return self._register(elem)

  def set_attr(self, element: int, key: str, val: str) -> None:
    self._store[element].set(key, val)

  def set_text(self, element: int, text: str | None) -> None:
    self._store[element].text = text

  def set_tail(self, element: int, tail: str | None) -> None:
    self._store[element].tail = tail

  def append(self, parent: int, child: int) -> None:
    self._store[parent].append(self._store[child])

  def get_text(self, element: int) -> str | None:
    return self._store[element].text

  def get_tail(self, element: int) -> str | None:
    return self._store[element].tail

  def get_attr(self, element: int, key: str, default: str | None = None) -> str | None:
    return self._store[element].attrib.get(key, default)

  def iter_children(self, element: int, tag: str | Collection[str] | None = None) -> Iterator[int]:
    real_elem = self._store[element]
    for child in real_elem:
      if tag is None or child.tag in tag:
        yield self._register(child)

  def get_tag(self, element: int) -> str:
    return self._store[element].tag

  def find(self, element: int, tag: str) -> int | None:
    found = self._store[element].find(tag)
    return self._register(found) if found is not None else None
