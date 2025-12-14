from collections.abc import Collection, Iterable, Iterator
from os import PathLike
import hypomnema as hm
import lxml.etree as et

from hypomnema.xml.utils import normalize_encoding, normalize_tag, prep_tag_set


class StrictBackend(hm.XMLBackend[int]):
  """
  A test-only backend that passes integers (IDs) to handlers instead of objects.

  This guarantees handlers NEVER access underlying XML objects directly (e.g.,
  via .tag or .attrib). Any attempt to do so will result in an AttributeError
  on the integer.
  """

  def __init__(self) -> None:
    self.element_id_to_element: dict[int, et.Element] = {}
    self._object_id_to_element_id: dict[int, int] = {}
    self._counter = 0

  def _register(self, element: et.Element) -> int:
    object_id = id(element)
    existing = self._object_id_to_element_id.get(object_id)
    if existing is not None:
      return existing
    self._counter += 1
    handle = self._counter
    self.element_id_to_element[handle] = element
    self._object_id_to_element_id[object_id] = handle
    return handle

  def parse(self, path: str | bytes | PathLike[str] | PathLike[bytes]) -> int:
    root = et.parse(path).getroot()
    return self._register(root)

  def write(
    self,
    element: int,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    *,
    encoding: str = "utf-8",
    force_short_empty_elements: bool = True,
  ) -> None:
    root = self.element_id_to_element[element]
    if force_short_empty_elements:
      for e in root.iter():
        if e.text is None:
          e.text = ""
    tree = et.ElementTree(root)
    tree.write(
      path,
      encoding=normalize_encoding(encoding),
      xml_declaration=True,
    )

  def iterparse(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[int]:
    tag_set: set[str] | None = prep_tag_set(tags)
    pending_yield_stack: list[et.Element] = []

    for event, elem in et.iterparse(path, events=("start", "end")):
      if event == "start":
        tag = normalize_tag(elem.tag)
        if tag_set is None or tag in tag_set:
          pending_yield_stack.append(elem)
        continue
      if not pending_yield_stack:
        elem.clear()
        continue
      if elem is pending_yield_stack[-1]:
        pending_yield_stack.pop()
        yield self._register(elem)

      if not pending_yield_stack:
        elem.clear()

  def iterwrite(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    elements: Iterable[int],
    encoding: str = "utf-8",
    root_elem: int | None = None,
    *,
    max_item_per_chunk: int = 1000,
  ) -> None:
    if max_item_per_chunk < 1:
      raise ValueError("buffer_size must be >= 1")

    _encoding: str = normalize_encoding(encoding)

    if root_elem is None:
      root_obj = et.Element("tmx", {"version": "1.4"})
      root_obj.text = ""
    else:
      root_obj = self.element_id_to_element[root_elem]

    root_string: bytes = et.tostring(
      root_obj,
      encoding=_encoding,
      xml_declaration=False,
    )

    root_string: bytes = et.tostring(root_obj, encoding=_encoding, xml_declaration=False)
    pos = root_string.rfind(b"</")
    if pos == -1:
      raise ValueError("Cannot find closing tag for root element: " + root_string.decode(_encoding))
    root_open = root_string[:pos]
    end_tag = root_string[pos:]

    buffer = bytearray()
    buffered_items = 0
    with open(path, "xb") as f:
      f.write(b'<?xml version="1.0" encoding="' + _encoding.encode("ascii") + b'"?>\n')
      f.write(root_open)
      for elem_id in elements:
        buffer.extend(
          et.tostring(
            self.element_id_to_element[elem_id], encoding=_encoding, xml_declaration=False
          )
        )
        buffered_items += 1
        if buffered_items >= max_item_per_chunk:
          f.write(buffer)
          buffer.clear()
          buffered_items = 0
      if buffer:
        f.write(buffer)
      f.write(end_tag)

  def make_elem(self, tag: str) -> int:
    elem = et.Element(tag)
    return self._register(elem)

  def set_attr(self, element: int, key: str, val: str) -> None:
    self.element_id_to_element[element].set(key, val)

  def set_text(self, element: int, text: str | None) -> None:
    self.element_id_to_element[element].text = text

  def set_tail(self, element: int, tail: str | None) -> None:
    self.element_id_to_element[element].tail = tail

  def append(self, parent: int, child: int) -> None:
    self.element_id_to_element[parent].append(self.element_id_to_element[child])

  def get_text(self, element: int) -> str | None:
    return self.element_id_to_element[element].text

  def get_tail(self, element: int) -> str | None:
    return self.element_id_to_element[element].tail

  def get_attr(self, element: int, key: str, default: str | None = None) -> str | None:
    return self.element_id_to_element[element].attrib.get(key, default)

  def iter_children(self, element: int, tags: str | Collection[str] | None = None) -> Iterator[int]:
    real_elem = self.element_id_to_element[element]
    tag_set = prep_tag_set(tags)
    for child in real_elem:
      child_tag = normalize_tag(child.tag)
      if tag_set is None or child_tag in tag_set:
        yield self._register(child)

  def get_tag(self, element: int) -> str:
    return normalize_tag(self.element_id_to_element[element].tag)
 
  def clear(self, element: int) -> None:
    self.element_id_to_element[element].clear()
