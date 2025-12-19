import lxml.etree as et
from collections.abc import Collection, Iterable, Iterator
from os import PathLike

from hypomnema.xml.backends.base import XmlBackend
from hypomnema.xml.utils import normalize_encoding, normalize_tag, prep_tag_set

__all__ = ["LxmlBackend"]


class LxmlBackend(XmlBackend[et._Element]):
  """Lxml Library-based XML backend."""

  def parse(self, path: str | bytes | PathLike[str] | PathLike[bytes]) -> et._Element:
    """
    Parses XML file at `path`.
    This will read the entire file and keep the entire tree in memory.
    If you need to parse a large file, consider using `iterparse`.

    Args:
      path: Path to XML file. Must be a string or a PathLike object.

    Returns:
      Element
    """
    return et.parse(path).getroot()

  def write(
    self,
    element: et._Element,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    encoding: str | None = None,
    *,
    force_short_empty_elements: bool = True,
  ) -> None:
    """
    Writes `element` to `path`.
    This will build the entire tree in memory and write it to disk.
    If you can stream the elements consider using `iterwrite`.

    Args:
      element: Element to write.
      path: Path to XML file. Must be a string or a PathLike object.
    """
    if force_short_empty_elements:
      for e in element.iter():
        if e.text is None:
          e.text = ""
    with et.xmlfile(path, encoding=normalize_encoding(encoding)) as f:
      f.write_declaration()
      f.write(element)

  def iterparse(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[et._Element]:
    """
    Incrementally parse XML from `path` and yield elements whose normalized
    tag matches `tags`. Elements are yielded on their end event and are
    structurally complete at the time they are yielded.

    Memory model:
    - Only elements whose tag matches `tags` are considered for yielding.
    - A stack tracks matching elements whose end tag has not yet been seen.
    - Any element encountered while this stack is empty is cleared
      immediately on its end event.
    - When a matching element is yielded, it is cleared as soon as the stack
      becomes empty, meaning no future yielded element can be a descendant.

    Usage:
    - Process each yielded element before advancing the iterator; previously
      yielded elements may be cleared after the next iteration step.
    - Do not retain element references beyond the current iteration.

    Tag filtering:
    - `tags` may be a string, a collection of strings, or None.
      * None, an empty string, or an empty collection means “yield all
        elements”.
    - Non-matching elements are not yielded but may appear as descendants of
      yielded elements.

    Special note:
    - When `tags` is None/empty, the entire document is effectively treated as
      matching; subtrees are only cleared once their ancestors close.
      This mode is correct but not memory-efficient.

    Parameters
    ----------
    path : file path or file-like object supported by ElementTree.iterparse
    tags : tag or tags to yield (normalized via `get_tag`)

    Yields
    ------
    xml.etree.ElementTree.Element
        Fully-built elements in document order, deepest children first.
    """
    tag_set: set[str] | None = prep_tag_set(tags)
    pending_yield_stack: list[et._Element] = []

    for event, elem in et.iterparse(path, ("start", "end")):
      if event == "start":
        tag = self.get_tag(elem)
        if tag_set is None or tag in tag_set:
          pending_yield_stack.append(elem)
        continue
      if not pending_yield_stack:
        self.clear(elem)
        continue
      if elem is pending_yield_stack[-1]:
        pending_yield_stack.pop()
        yield elem
      if not pending_yield_stack:
        self.clear(elem)

  def iterwrite(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    elements: Iterable[et._Element],
    encoding: str | None = None,
    root_elem: et._Element | None = None,
    *,
    max_item_per_chunk: int = 1000,
  ) -> None:
    """
    Stream a sequence of XML elements to `path`, wrapped inside a root
    element, without constructing the entire document tree in memory.

    The output document has the form:

        <?xml version="1.0" encoding="ENC"?>
        <root ...>
          [existing content of root_elem, if any]
          [all streamed elements, in order]
        </root>

    The caller is responsible for providing elements in valid document order
    and ensuring the resulting XML is well-formed and schema-compliant.

    Root element
    ------------
    - If `root_elem` is None, a `<tmx version="1.4">` element is created and
      used as the document root.
    - If `root_elem` is provided, it is serialized once and used as a
      template:
      * Any existing children and text of `root_elem` are written before the
        streamed `elements`.
      * The closing tag of `root_elem` is written after all streamed
        `elements`.
    - Attributes, namespaces, and other metadata of `root_elem` are preserved
      exactly as serialized by `ElementTree`.

    Streaming / buffering
    ---------------------
    - Elements from `elements` are serialized with `ElementTree.tostring`
      and written out in order.
    - Up to `max_items_per_chunk` serialized elements are buffered in memory
      before being flushed to disk with a single write.
    - This provides streaming behaviour in terms of element count; the full
      document is never held as a single in-memory string.

    Encoding and formatting
    -----------------------
    - `encoding` is normalized and used both for the XML declaration and for
      `ElementTree.tostring`.
    - The file is opened in binary mode with exclusive creation (`"xb"`); a
      `FileExistsError` is raised if `path` already exists.
    - No pretty-printing or additional whitespace is added. Whitespace is
      preserved exactly as produced by `ElementTree.tostring`, which is
      suitable for TMX where whitespace may be significant.

    Parameters
    ----------
    path :
        Target file path or file-like path object. The file must not already
        exist.
    elements :
        Iterable of fully-built `xml.etree.ElementTree.Element` instances to
        be written as children of `root_elem`, in order.
    encoding :
        Name of the output character encoding (e.g. "utf-8"). Used for both
        the XML declaration and element serialization.
    root_elem :
        Root element of the document. If None, a default `<tmx version="1.4">`
        element is used.
    max_items_per_chunk :
        Maximum number of serialized elements to buffer before flushing them
        to disk. Must be >= 1.
    """
    if max_item_per_chunk < 1:
      raise ValueError("buffer_size must be >= 1")
    _encoding: str = normalize_encoding(encoding)
    if root_elem is None:
      root_elem = et.Element("tmx", {"version": "1.4"})
      root_elem.text = ""
    root_string: bytes = et.tostring(root_elem, encoding=_encoding, xml_declaration=False)
    pos = root_string.rfind(b"</")
    if pos == -1:
      raise ValueError("Cannot find closing tag for root element: " + root_string.decode(_encoding))
    root_open = root_string[:pos]
    end_tag = root_string[pos:]

    buffer = bytearray()
    with open(path, "xb") as f:
      f.write(b'<?xml version="1.0" encoding="' + _encoding.encode("ascii") + b'"?>\n')
      f.write(root_open)
      counter = 0
      for elem in elements:
        buffer.extend(et.tostring(elem, encoding=_encoding, xml_declaration=False))
        counter += 1
        if counter == max_item_per_chunk:
          f.write(buffer)
          buffer.clear()
      if buffer:
        f.write(buffer)
      f.write(end_tag)

  def make_elem(self, tag: str) -> et._Element:
    return et.Element(tag)

  def set_attr(self, element: et._Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: et._Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: et._Element, child: et._Element) -> None:
    parent.append(child)

  def get_attr(self, element: et._Element, key: str, default: str | None = None) -> str | None:
    return element.attrib.get(key, default)

  def get_text(self, element: et._Element) -> str | None:
    return element.text

  def get_tail(self, element: et._Element) -> str | None:
    return element.tail

  def set_tail(self, element: et._Element, tail: str | None) -> None:
    element.tail = tail

  def iter_children(
    self, element: et._Element, tags: str | Collection[str] | None = None
  ) -> Iterator[et._Element]:
    tag_set = prep_tag_set(tags)
    for child in element:
      child_tag = self.get_tag(child)
      if tag_set is None or child_tag in tag_set:
        yield child

  def get_tag(self, element: et._Element) -> str:
    return normalize_tag(element.tag)

  def clear(self, element: et._Element) -> None:
    element.clear()
