from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from os import PathLike
from pathlib import Path
from typing import (
  Any,
  Generic,
  Iterator,
  ParamSpec,
  Protocol,
  Self,
  SupportsIndex,
  SupportsInt,
  Type,
  TypeVar,
  overload,
  runtime_checkable,
)

ChildrenType = TypeVar("ChildrenType")
P = ParamSpec("P")
R = TypeVar("R", bound="AnyXmlElement", covariant=True)

DEFAULT_XML_FACTORY: AnyElementFactory[..., AnyXmlElement] | None = None

__all__ = (
  "AnyXmlElement",
  "BaseTmxElement",
  "WithChildren",
  "TmxParser",
  "set_default_factory",
  "DEFAULT_XML_FACTORY",
  "AnyElementFactory",
  "ConvertibleToInt",
)


class AnyXmlElement(Protocol):
  tag: Any
  text: Any
  tail: Any
  attrib: Any

  def __iter__(self) -> Iterator[Any]: ...

  def append(self, element: Any, /) -> None: ...


def set_default_factory(
  factory: AnyElementFactory[..., AnyXmlElement] | None,
) -> None:
  global DEFAULT_XML_FACTORY
  DEFAULT_XML_FACTORY = factory  # type: ignore # We're intentionally mutating the global


class AnyElementFactory(Protocol[P, R]):
  def __call__(
    self,
    tag: str,
    attrib: dict[str, str],
    /,
    *args: Any,
    **kwargs: Any,
  ) -> R: ...


class BaseTmxElement(ABC):
  xml_factory: AnyElementFactory[..., AnyXmlElement] | None
  __slots__ = ("xml_factory",)

  def set_default_factory(
    self, factory: AnyElementFactory[P, R] | None
  ) -> None:
    self.xml_factory = factory

  @abstractmethod
  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R: ...

  @classmethod
  @abstractmethod
  def from_xml(cls: Type[Self], element: AnyXmlElement) -> BaseTmxElement: ...

  @abstractmethod
  def _make_attrib_dict(self) -> dict[str, str]: ...


class WithChildren(Generic[ChildrenType]):
  __slots__ = ()
  _children: list[ChildrenType]

  def __len__(self) -> int:
    return len(self._children)

  def __iter__(self) -> Iterator[ChildrenType]:
    return iter(self._children)

  @overload
  def __getitem__(self, idx: int) -> ChildrenType: ...
  @overload
  def __getitem__(self, idx: slice) -> list[ChildrenType]: ...
  def __getitem__(self, idx: int | slice) -> ChildrenType | list[ChildrenType]:
    return self._children[idx]

  @overload
  def __setitem__(self, idx: SupportsIndex, value: ChildrenType) -> None: ...
  @overload
  def __setitem__(self, idx: slice, value: Iterable[ChildrenType]) -> None: ...
  def __setitem__(
    self,
    idx: SupportsIndex | slice,
    value: ChildrenType | Iterable[ChildrenType],
  ) -> None:
    if isinstance(idx, slice):
      if not isinstance(value, Iterable):
        raise TypeError("value must be an iterable")
      self._children[idx] = value
    else:
      if isinstance(value, Iterable):
        raise TypeError("value must be a single element")
      self._children[idx] = value

  def __delitem__(self, idx: int | slice) -> None:
    del self._children[idx]

  def append(self, value: ChildrenType) -> None:
    self._children.append(value)

  def extend(self, values: Iterable[ChildrenType]) -> None:
    self._children.extend(values)

  def insert(self, idx: SupportsIndex, value: ChildrenType) -> None:
    self._children.insert(idx, value)

  def pop(self, idx: SupportsIndex = -1) -> ChildrenType:
    return self._children.pop(idx)

  def remove(self, value: ChildrenType) -> None:
    self._children.remove(value)

  def clear(self) -> None:
    self._children.clear()


class TmxParser(ABC):
  source: Path

  @abstractmethod
  def __init__(self, source: PathLike[str] | Path | str) -> None: ...

  @abstractmethod
  def iter(
    self,
    mask: str | tuple[str, ...] | None = None,
    mask_exclude: bool = False,
    default_factory: AnyElementFactory[..., AnyXmlElement] | None = None,
  ) -> Iterator[BaseTmxElement]: ...


@runtime_checkable
class SupportsTrunc(Protocol):
  def __trunc__(self) -> int: ...


type ConvertibleToInt = (
  str
  | bytes
  | bytearray
  | memoryview
  | SupportsInt
  | SupportsIndex
  | SupportsTrunc
)
