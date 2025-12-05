from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable, Iterator, Mapping, Sequence
from os import PathLike
from typing import Callable, Protocol, TypeVar

from hypomnema.xml.utils import normalize_encoding, prep_tag_set

T_XmlBackend = TypeVar("T_XmlBackend")


class tobytesCallback[T_XmlBackend](Protocol):
  def __call__(self, element: T_XmlBackend, /) -> bytes: ...


__all__ = ["XMLBackend", "T_XmlBackend", "tobytesCallback"]


class XMLBackend[T_XmlBackend](ABC):
  @abstractmethod
  def get_tag(self, element: T_XmlBackend) -> str: ...
  @abstractmethod
  def make_elem(self, tag: str) -> T_XmlBackend: ...
  @abstractmethod
  def append(self, parent: T_XmlBackend, child: T_XmlBackend) -> None: ...
  @abstractmethod
  def get_attr(self, element: T_XmlBackend, key: str, default: str | None = None) -> str | None: ...
  @abstractmethod
  def set_attr(self, element: T_XmlBackend, key: str, val: str) -> None: ...
  @abstractmethod
  def get_text(self, element: T_XmlBackend) -> str | None: ...
  @abstractmethod
  def set_text(self, element: T_XmlBackend, text: str | None) -> None: ...
  @abstractmethod
  def get_tail(self, element: T_XmlBackend) -> str | None: ...
  @abstractmethod
  def set_tail(self, element: T_XmlBackend, tail: str | None) -> None: ...
  @abstractmethod
  def iter_children(
    self, element: T_XmlBackend, tag: str | Collection[str] | None = None
  ) -> Iterator[T_XmlBackend]: ...
  @abstractmethod
  def parse(self, path: PathLike[str]) -> T_XmlBackend: ...
  @abstractmethod
  def write(self, element: T_XmlBackend, path: PathLike[str]) -> None: ...
  @abstractmethod
  def clear(self, element: T_XmlBackend) -> None: ...
  @abstractmethod
  def remove(self, parent: T_XmlBackend, child: T_XmlBackend) -> None: ...


class IterableXMLBackend(XMLBackend[T_XmlBackend], ABC):
  @abstractmethod
  def iterwrite(self, path: PathLike[str], elements: Iterable[T_XmlBackend]) -> None: ...
  @abstractmethod
  def iterparse(
    self,
    path: PathLike[str],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[T_XmlBackend]: ...

  def _iterparse_core(
    self,
    path: PathLike[str],
    tags: str | Collection[str] | None,
    iterparse: Callable[[PathLike[str], Sequence[str]], Iterator[tuple[str, T_XmlBackend]]],
  ) -> Iterator[T_XmlBackend]:
    def should_yield(tag: str) -> bool:
      return tag_set is None or tag in tag_set

    tag_set = prep_tag_set(tags)
    stack: list[tuple[T_XmlBackend, bool]] = []
    yielding_ancestors: int = 0
    context = iterparse(path, ("start", "end"))

    for event, elem in context:
      if event == "start":
        tag = self.get_tag(elem)
        y = should_yield(tag)
        stack.append((elem, y))
        if y:
          yielding_ancestors += 1
        continue

      cur_elem, cur_yield = stack[-1]
      assert cur_elem is elem

      parent: T_XmlBackend | None = stack[-2][0] if len(stack) >= 2 else None
      ancestor_will_be_yielded = yielding_ancestors - (1 if parent is None else 0) > 0

      if cur_yield:
        yield elem

      if not ancestor_will_be_yielded:
        self.clear(elem)
        if parent is not None:
          self.remove(parent, elem)

      stack.pop()
      if cur_yield:
        yielding_ancestors -= 1

    del context

  def _prep_root(
    self,
    root: T_XmlBackend | None,
    root_tag: str | None,
    root_attr: Mapping | None,
  ) -> tuple[str, dict[str, str]]:
    if root is not None:
      _root_tag = self.get_tag(root)
      if not isinstance(_root_tag, str):
        raise TypeError("root tag must be a string")
      attrib = getattr(root, "attrib", {})
      if not isinstance(attrib, Mapping):
        raise TypeError("root.attrib must be a Mapping")
      return _root_tag, {str(k): str(v) for k, v in attrib.items()}

    if root_tag is None:
      if root_attr is not None:
        raise ValueError("root_attr must be None if root_tag is None")
      return "tmx", {"version": "1.4"}

    if not isinstance(root_tag, str):
      raise TypeError("root_tag must be a string or None")

    if root_attr is None:
      root_attr = {}
    if not isinstance(root_attr, Mapping):
      raise TypeError("root_attr must be a Mapping")

    for k, v in root_attr.items():
      if not isinstance(k, str) or not isinstance(v, str):
        raise TypeError("root_attr must be a Mapping[str, str]")

    return root_tag, {k: v for k, v in root_attr.items()}

  def _root_open_close(
    self,
    root_tag: str,
    root_attr: dict[str, str],
    to_bytes: tobytesCallback,
  ) -> tuple[bytes, bytes]:
    temp_root = self.make_elem(root_tag)
    self.set_text(temp_root, "")
    for k, v in root_attr.items():
      self.set_attr(temp_root, k, v)
    bytes_element = to_bytes(temp_root)
    open_end = bytes_element.find(b">")
    if open_end == -1:
      raise RuntimeError("Failed to serialize root element")
    root_open = bytes_element[: open_end + 1]
    root_close = bytes_element[open_end + 1 :]
    return root_open, root_close

  def _iterwrite_core(
    self,
    path: PathLike[str],
    elements: Iterable[T_XmlBackend],
    encoding: str,
    root: T_XmlBackend | None,
    root_tag: str | None,
    root_attr: Mapping[str, str] | None,
    flush_every: int,
    clear_on_write: bool,
    _tobytes: tobytesCallback,
  ) -> None:
    encoding = normalize_encoding(encoding)

    if flush_every < 0:
      raise ValueError("flush_every must be >= 0")

    _root_tag, _root_attr = self._prep_root(root, root_tag, root_attr)
    root_open, root_close = self._root_open_close(_root_tag, _root_attr, _tobytes)

    with open(path, "wb") as f:
      decl = f'<?xml version="1.0" encoding="{encoding}"?>\n'
      f.write(decl.encode(encoding))
      f.write(root_open)
      if flush_every:
        for count, elem in enumerate(elements, start=1):
          data = _tobytes(elem)
          f.write(data)
          if count % flush_every == 0:
            f.flush()
          if clear_on_write:
            self.clear(elem)
        else:
          for elem in elements:
            data = _tobytes(elem)
            f.write(data)
            if clear_on_write:
              self.clear(elem)

      f.write(root_close)
      f.flush()
