from abc import ABC, abstractmethod
from collections.abc import Collection, Iterable, Iterator
from os import PathLike
from typing import TypeVar


T = TypeVar("T")

__all__ = ["XMLBackend"]


class XMLBackend[T](ABC):
  @abstractmethod
  def get_tag(self, element: T) -> str: ...
  @abstractmethod
  def make_elem(self, tag: str) -> T: ...
  @abstractmethod
  def append(self, parent: T, child: T) -> None: ...
  @abstractmethod
  def get_attr(self, element: T, key: str, default: str | None = None) -> str | None: ...
  @abstractmethod
  def set_attr(self, element: T, key: str, val: str) -> None: ...
  @abstractmethod
  def get_text(self, element: T) -> str | None: ...
  @abstractmethod
  def set_text(self, element: T, text: str | None) -> None: ...
  @abstractmethod
  def get_tail(self, element: T) -> str | None: ...
  @abstractmethod
  def set_tail(self, element: T, tail: str | None) -> None: ...
  @abstractmethod
  def iter_children(self, element: T, tags: str | Collection[str] | None = None) -> Iterator[T]: ...
  @abstractmethod
  def parse(self, path: str | bytes | PathLike[str] | PathLike[bytes]) -> T: ...
  @abstractmethod
  def write(
    self,
    element: T,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    encoding: str | None = None,
  ) -> None: ...
  @abstractmethod
  def iterparse(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    tags: str | Collection[str] | None = None,
  ) -> Iterator[T]: ...
  @abstractmethod
  def iterwrite(
    self,
    path: str | bytes | PathLike[str] | PathLike[bytes],
    elements: Iterable[T],
    encoding: str | None = None,
    root_elem: T | None = None,
    *,
    max_item_per_chunk: int = 1000,
  ) -> None: ...
  @abstractmethod
  def clear(self, element: T) -> None: ...
