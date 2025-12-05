import xml.etree.ElementTree as et
from collections.abc import Collection, Iterable, Iterator, Mapping
from functools import partial
from os import PathLike

from hypomnema.xml.backends.base import IterableXMLBackend
from hypomnema.xml.utils import normalize_encoding, normalize_tag, prep_tag_set

__all__ = ["StandardBackend"]


class StandardBackend(IterableXMLBackend[et.Element]):
  """Standard Library-based XML backend."""

  def parse(self, path: str | PathLike) -> et.Element:
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

  def write(self, element: et.Element, path: str | PathLike, *, encoding: str = "utf-8") -> None:
    """
    Writes `element` to `path`.
    This will build the entire tree in memory and write it to disk.
    If you can stream the elements consider using `iterwrite`.

    Args:
      element: Element to write.
      path: Path to XML file. Must be a string or a PathLike object.
    """
    et.ElementTree(element).write(path, normalize_encoding(encoding), xml_declaration=True, short_empty_elements=False)

  def iterparse(
    self,
    path: PathLike[str],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[et.Element]:
    """
    Yields elements whose tag matches `tags`, while keeping them in the
    tree as long as any ancestor that will be yielded still needs them.

    For memory efficiency, elements that are not needed by any future
    yielded ancestor are cleared and removed as soon as their end tag
    is parsed.
    Yielded elements may be cleared/removed from the underlying tree
    after you advance the iterator; do not rely on them remaining
    attached or retaining children after consuming further events.
    """
    yield from self._iterparse_core(path, tags, et.iterparse)

  def iterwrite(
    self,
    path: PathLike[str],
    elements: Iterable[et.Element],
    *,
    encoding: str = "utf-8",
    root: et.Element | None = None,
    root_tag: str | None = None,
    root_attr: Mapping[str, str] | None = None,
    flush_every: int = 1000,
    clear_on_write: bool = True,
  ) -> None:
    """
    Streams `elements` to `path`.

    This version is more memory efficient than `write` but can lead to
    invalid TMX files if the elements are not provided in the correct order.

    Root handling:
      - If `root` is specified, it must be an ElementTree.Element and will
        be used as the root element. `root_tag` and `root_attr` are ignored.
      - If `root` is None and `root_tag` is None, the root defaults to
        <tmx version="1.4"> and `root_attr` must be None.
      - If `root` is None and `root_tag` is not None, `root_tag` must be a
        string and `root_attr` (if provided) must be a Mapping[str, str].

    `flush_every` specifies how many elements should be written before forcing
    a flush to disk. A higher value will increase memory usage in the I/O
    stack but decrease flush overhead. Set to 0 to only flush once every
    element has been written to the buffer.

    `clear_on_write` specifies whether the element should be cleared after
    writing it. Only set this to False if you need to access the element or a
    tree containing it after writing; otherwise, Python will keep references
    to the full element structure, which can significantly increase memory
    usage for large streams.

    Args:
      path: Path to XML file. Must be a PathLike[str] object.
      elements: An iterable of ElementTree.Element to write. Ideally this
        should be a generator that creates the elements lazily.
      encoding: Encoding to use for the file (default is utf-8).
      root: Root element to write.
      root_tag: Tag of the root element. Ignored if `root` is not None.
      root_attr: Attributes of the root element. Ignored if `root` is not None.
      flush_every: Number of elements to buffer before flushing to disk.
      clear_on_write: Whether to clear the element after writing it.
    """
    self._iterwrite_core(
      path,
      elements,
      encoding=encoding,
      root=root,
      root_tag=root_tag,
      root_attr=root_attr,
      flush_every=flush_every,
      clear_on_write=clear_on_write,
      _tobytes=partial(
        et.tostring,
        encoding=encoding,
        xml_declaration=False,
        short_empty_elements=False,
      ),
    )

  def make_elem(self, tag: str) -> et.Element:
    return et.Element(tag)

  def set_attr(self, element: et.Element, key: str, val: str) -> None:
    element.set(key, val)

  def set_text(self, element: et.Element, text: str | None) -> None:
    element.text = text

  def append(self, parent: et.Element, child: et.Element) -> None:
    parent.append(child)

  def get_attr(self, element: et.Element, key: str, default: str | None = None) -> str | None:
    return element.attrib.get(key, default)

  def get_text(self, element: et.Element) -> str | None:
    return element.text

  def get_tail(self, element: et.Element) -> str | None:
    return element.tail

  def set_tail(self, element: et.Element, tail: str | None) -> None:
    element.tail = tail

  def iter_children(
    self, element: et.Element, tag: str | Collection[str] | None = None
  ) -> Iterator[et.Element]:
    tag_set = prep_tag_set(tag)
    for child in element:
      child_tag = self.get_tag(child)
      if tag_set is None or child_tag in tag_set:
        yield child

  def get_tag(self, element: et.Element) -> str:
    return normalize_tag(element.tag)

  def clear(self, element: et.Element) -> None:
    element.clear()

  def remove(self, parent: et.Element, child: et.Element) -> None:
    parent.remove(child)
