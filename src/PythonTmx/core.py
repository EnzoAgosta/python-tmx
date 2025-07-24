from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import MISSING, dataclass, fields
from datetime import datetime
from enum import Enum
from os import PathLike
from pathlib import Path
from typing import Any, Iterator, ParamSpec, Protocol, TypeVar


class AnyXmlElement(Protocol):
  """
  Protocol for a generic XML element abstraction.

  Defines the minimal interface required for XML element objects to be
  compatible with TMX element parsing and serialization. This protocol
  is intentionally lax and uses `Any` to allow for easy compatibility
  with both lxml and the standard library's `xml.etree.ElementTree` and
  their sometimes unreconcilable interfaces.

  Attributes:
      tag: The element's tag name or qualified name.
        Usually a string or a QName-like object
      text: The text content directly under this element,
        and before any child, if any
      tail: The text following this element's end tag, if any.
      attrib: A mapping of the element's attributes. Expected to be
        a dict[str, str] or an object behaving like a dict.

  Methods:
      __iter__(): Returns an iterator over the child elements.
      __len__(): Returns the number of child elements.
  """

  tag: Any
  text: Any
  tail: Any
  attrib: Any

  def __iter__(self) -> Iterator[Any]: ...
  def __len__(self) -> int: ...


P = ParamSpec("P")  # Generic ParamSpec
R = TypeVar(
  "R", bound=AnyXmlElement, covariant=True
)  # Generic TypeVar for return type


class AnyElementFactory(Protocol[P, R]):
  """
  Protocol for an XML element factory callable.

  This protocol defines the expected signature for any factory function or
  callable that creates XML elements. Implementations should return an object
  which implements the `AnyXmlElement` protocol.

  The only required arguments here are `tag` and `attrib`, which are used to
  create the XML element. Additional positional and keyword arguments are
  included for wide compatibility but not used by this library.

  Args:
      tag: The tag name for the XML element.
      attrib: Dictionary of XML attributes for the element.
      *args: Additional positional arguments passed to the factory.
      **kwargs: Additional keyword arguments passed to the factory.

  Returns:
      R: An object that implements the `AnyXmlElement` protocol.
  """

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
  """
  Abstract base class for all TMX elements.

  .. warning::
    This is an abstract base class meant to provide a common interface for
    all Tmx Elements. This is NOT meant to and should NOT be instantiated directly.
    Instead, use the subclasses provided by the library instead.

  All Tmx xml elements have an implementation of the `BaseTmxElement` class
  that corresponds to it.
  """

  @abstractmethod
  def to_xml(self, factory: AnyElementFactory[P, R]) -> R:
    """
    Convert this TMX element into an XML element.

    .. note::
        The `factory` doesn't necessarily have to be the same one that
        was used to parse the XML element. It's fully valid to use `LxmlParser`
        object to parse a file and create Tmx Elements but then export them
        using the Standard Library's `xml.etree.ElementTree` module instead.

    Args:
        factory: A callable conforming to `AnyElementFactory`,
          used to create XML elements in a library-agnostic way.

    Returns:
        R: The XML element corresponding to this TMX element, returned by the
          `factory` callable.
    """
    ...

  @classmethod
  @abstractmethod
  def from_xml(cls, element: AnyXmlElement) -> BaseTmxElement:
    """
    Class method used to construct a TMX element from a raw XML element.
    This method is the primary way to create TMX elements from XML
    and is called by the Parser objects when yielding elements.

    Args:
      element: The XML element to parse.

    Returns:
        BaseTmxElement: An instance of the class populated from the XML.
    """
    ...

  def _make_attrib_dict(self) -> dict[str, str]:
    """
    Private method to create a dictionary of XML attributes
    from the element's fields.

    For `datetime` objects, the value is converted to a string in the
    form of `YYYYMMDDTHHMMSSZ`.

    For `Enum` objects, the value of that Enum field is used.

    For all other fields, the value is converted to a string using
    `str(value)`.

    Returns:
      A dict mapping field names to string values for XML serialization.

    Raises:
      ValueError: If a required field is missing (i.e., has no value).
    """
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
  """
  Abstract base class for TMX file parsers.

  Encapsulates the logic for iterating over TMX elements in a source file,
  allowing for backend-agnostic Tmx file parsing.

  As long as the object is a subclass of `TmxParser`, any custom implementation
  can also be used.

  The library provides four implementations of this class:

  - `LazyLxmlParser`: Uses the `lxml` library to parse XML files lazily by
    using `iterparse` under the hood. Useful for large files that don't fit
    into memory.
  - `LxmlParser`: Uses the `lxml` library to parse XML files the conventional
    way, by reading the entire file into memory.
  - `LazyStandardParser`: Uses the `xml.etree.ElementTree` library to parse
    XML files lazily by using `iterparse` under the hood. Useful for large
    files that don't fit into memory.
  - `StandardParser`: Uses the `xml.etree.ElementTree` library to parse XML
    files the conventional way, by reading the entire file into memory.
  """

  source: Path
  """
  A `Path` object pointing to the source file to parse.
  """

  @abstractmethod
  def __init__(self, source: PathLike[str] | Path | str) -> None:
    """
    Initialize the parser from a source file after performing
    some basic file validation.

    Args:
        source: The path to the source file to parse, can be a str,
          `Path` object or anything that's Pathlike.

    Raises:
        FileNotFoundError: If the source path does not exist.
        IsADirectoryError: If the source path is not a file.
    """
    ...

  @abstractmethod
  def iter(
    self, mask: str | tuple[str, ...] | None = None, mask_exclude: bool = False
  ) -> Iterator[BaseTmxElement]:
    """
    The core method for iterating over TMX elements in a source file.

    This method is responsible for generating or returning the proper
    TMX elements from the source file.

    The actual logic for how the file should be parsed is handled by
    the concrete implementation of this class. Lazy parsers may yield
    elements as they are parsed, while eager parsers may read the entire
    file into memory and then yield elements from a list/tuple/deque/etc.

    The `mask` parameter is used to filter out unwanted elements to make
    parsing more efficient. it is combined with the `mask_exclude` parameter
    to determine the behavior of the `mask` parameter.

    If `mask_exclude` is `True`, all elements EXCEPT those in the `mask`
    will be yielded. If `mask_exclude` is `False`, only elements in the
    `mask` will be yielded.

    Implementations are also free to decide how to handle errors, but are
    encouraged to raise a `ParsingError` to align with the rest of the
    library's error handling.

    Args:
        mask: A tag name, tuple of tag names, or None.
        mask_exclude: Whether to yield only elements in the `mask` or all
          elements except those in the `mask`.

    Yields:
        BaseTmxElement: Parsed TMX elements from the source file based on the
          provided `mask`.

    Raises:
        ParsingError: If a TMX element cannot be parsed.
        ValueError: If the provided mask includes unsupported tag names.
    """
    ...
