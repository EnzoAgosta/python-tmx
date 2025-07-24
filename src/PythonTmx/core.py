from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, fields
from datetime import datetime
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Any, ClassVar, Iterator, ParamSpec, TypeVar

from typing_extensions import Protocol

from PythonTmx.utils import ensure_file


# Ultra lax because resolving typing between lxml ElementTree is
# basically impossible, will rely on runtime checks instead
class AnyXmlElement(Protocol):
  tag: Any # The tag of the element
  text: Any # The text of the element (can be None)
  tail: Any # The tail of the element (can be None)
  attrib: Any # The attributes of the element as a dict or Mapping-like object

  def __iter__(self) -> Iterator[Any]: ... # Needs to be iterable
  def __len__(self) -> int: ... # Needs to have a length (corresponds to the number of children)


P = ParamSpec("P") # Generic ParamSpec
R = TypeVar("R", bound=AnyXmlElement, covariant=True) # Generic TypeVar for return type


class AnyElementFactory(Protocol[P, R]):
  def __call__(
    self,
    tag: str,
    attrib: dict[str, str],
    /,
    *args: Any,
    **kwargs: Any,
  ) -> R: ...


@dataclass(slots=True, init=False, repr=False, eq=False, match_args=False)
class BaseTmxElement(ABC):
  tag: ClassVar[str]

  @abstractmethod
  def to_xml(self, factory: AnyElementFactory[P, R]) -> R: ...

  @classmethod
  @abstractmethod
  def from_xml(cls, element: AnyXmlElement) -> BaseTmxElement: ...

  def _make_attrib_dict(self) -> dict[str, str]:
    attrib_dict: dict[str, str] = {}
    for field_data in fields(self):
      key, val = field_data.name, getattr(self, field_data.name)
      if val is None:
        if field_data.default is MISSING:
          raise ValueError(f"Missing required field {key}")
        else:
          continue
      match val:
        case datetime():
          attrib_dict[key] = val.strftime("%Y%m%dT%H%M%SZ")
        case Enum():
          attrib_dict[key] = val.value
        case _:
          attrib_dict[key] = str(val)
    return attrib_dict

class TmxParser(ABC):
  source: Path
  parser: Any

  def __init__(self, source: PathLike[str] | Path | str, parser: Any) -> None:
    source = ensure_file(source)
    self.source = source
    self.parser = parser

  @abstractmethod
  def iter(
    self, mask: str | tuple[str, ...] | None = None
  ) -> Iterator[BaseTmxElement]: ...
