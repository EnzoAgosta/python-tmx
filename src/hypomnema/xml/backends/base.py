from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable, Iterator
from os import PathLike


__all__ = ["XmlBackend"]


class XmlBackend[BackendElementType](ABC):
  @abstractmethod
  def get_tag(self, element: BackendElementType) -> str: ...
  @abstractmethod
  def make_elem(self, tag: str) -> BackendElementType: ...
  @abstractmethod
  def append(self, parent: BackendElementType, child: BackendElementType) -> None: ...
  @abstractmethod
  def get_attr(
    self, element: BackendElementType, key: str, default: str | None = None
  ) -> str | None: ...
  @abstractmethod
  def set_attr(self, element: BackendElementType, key: str, val: str) -> None: ...
  @abstractmethod
  def get_text(self, element: BackendElementType) -> str | None: ...
  @abstractmethod
  def set_text(self, element: BackendElementType, text: str | None) -> None: ...
  @abstractmethod
  def get_tail(self, element: BackendElementType) -> str | None: ...
  @abstractmethod
  def set_tail(self, element: BackendElementType, tail: str | None) -> None: ...
  @abstractmethod
  def iter_children(
    self, element: BackendElementType, tags: str | Collection[str] | None = None
  ) -> Iterator[BackendElementType]: ...
  @abstractmethod
  def parse(self, path: str | bytes | PathLike[str] | PathLike[bytes]) -> BackendElementType: ...
  @abstractmethod
  def write(
    self,
    element: BackendElementType,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    encoding: str | None = None,
  ) -> None: ...
  @abstractmethod
  def iterparse(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[BackendElementType]: ...
  @abstractmethod
  def iterwrite(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    elements: Iterable[BackendElementType],
    encoding: str | None = None,
    root_elem: BackendElementType | None = None,
    *,
    max_item_per_chunk: int = 1000,
  ) -> None: ...
  @abstractmethod
  def clear(self, element: BackendElementType) -> None: ...
