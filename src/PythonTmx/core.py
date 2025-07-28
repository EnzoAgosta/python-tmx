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
  Type,
  TypeVar,
  overload,
)

ChildrenType = TypeVar("ChildrenType")
P = ParamSpec("P")
R = TypeVar("R", bound="AnyXmlElement", covariant=True)

DEFAULT_XML_FACTORY: AnyElementFactory[..., AnyXmlElement] | None = None


class AnyXmlElement(Protocol):
  """
  Protocol for a generic XML element abstraction.

  Defines the minimal interface required for XML element objects to be
  compatible with TMX element parsing and serialization. This protocol is
  intentionally lax and uses `Any` to allow for easy compatibility with both
  lxml and the standard library's `xml.etree.ElementTree` and their sometimes
  unreconcilable interfaces.

  Attributes:
      tag: The element's tag name or qualified name (usually a string or QName).
      text: The text content directly under this element, before any children.
      tail: The text following this element's end tag, if any.
      attrib: An attribute mapping supporting both `get` and `__getitem__`.

  Methods:
      __iter__(): Returns an iterator over the child elements.
      append(element): Appends the given element to the end of the child elements.
  """

  tag: Any
  text: Any
  tail: Any
  attrib: Any

  def __iter__(self) -> Iterator[Any]:
    """
    Iterate over the child elements.

    Returns:
        Iterator[Any]: An iterator of child elements.
    """
    ...

  def append(self, element: Any, /) -> None:
    """
    Appends the given element to the end of the child elements.

    Args:
        element: The element to append.
    """
    ...


def set_default_factory(
  factory: AnyElementFactory[..., AnyXmlElement] | None,
) -> None:
  """
  Set the global default XML factory for all TMX element serialization.

  Can be overridden per element or on each `to_xml` call.

  Args:
      factory: Callable that creates XML elements from tag/attrib,
          or None to unset the global default.
  """
  global DEFAULT_XML_FACTORY
  DEFAULT_XML_FACTORY = factory  # type: ignore # We're intentionally mutating the global


class AnyElementFactory(Protocol[P, R]):
  """
  Protocol for an XML element factory callable.

  Defines the expected signature for any factory function or callable that
  creates XML elements. Implementations must return an object that implements
  the `AnyXmlElement` protocol.

  Only `tag` and `attrib` are required; additional positional and keyword
  arguments are included for compatibility with various XML backends but are
  not used directly by this library.

  Args:
      tag: The tag name for the XML element.
      attrib: An attribute mapping supporting both `get` and `__getitem__`.
      *args: Additional positional arguments.
      **kwargs: Additional keyword arguments.

  Returns:
      R: An object implementing the `AnyXmlElement` protocol.
  """

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
  """
  Abstract base class for all TMX elements.

  .. warning::
    This is an abstract base class meant to provide a common interface for
    all Tmx Elements. This is NOT meant to and should NOT be instantiated directly.
    Instead, use the subclasses provided by the library instead.

  All Tmx xml elements have an implementation of the `BaseTmxElement` class
  that corresponds to it.
  """

  def set_default_factory(
    self, factory: AnyElementFactory[P, R] | None
  ) -> None:
    """
    Set or unset the default XML factory for this element instance.

    Args:
        factory: Callable that creates XML elements from tag/attrib,
            or None to unset the instance default.
    """
    self.xml_factory = factory

  @abstractmethod
  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R:
    """
    Convert this TMX element into an XML element.

    .. note::
        The `factory` doesn't necessarily have to be the same one that
        was used to parse the XML element. It's fully valid to use `LxmlParser`
        object to parse a file and create Tmx Elements but then export them
        using the Standard Library's `xml.etree.ElementTree.Element` class instead.

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
  def from_xml(cls:Type[Self], element: AnyXmlElement) -> BaseTmxElement:
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

  @abstractmethod
  def _make_attrib_dict(self) -> dict[str, str]:
    """
    Private method to create a dictionary of XML attributes
    from the element's fields.

    For `datetime` objects, the value is converted to a string in the
    form of `YYYYMMDDTHHMMSSZ`.

    For `Enum` objects, the value of that Enum field is used.

    For all other fields, the value is converted to a string using
    `str(value)`.

    For `lang` attributes, the value is converted to a string using
    `str(value)` and prefixed with `{http://www.w3.org/XML/1998/namespace}lang`.

    Returns:
      A dict mapping field names to string values for XML serialization.

    Raises:
      ValueError: If a required field is missing (i.e., has no value).
    """
    ...


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
    self,
    mask: str | tuple[str, ...] | None = None,
    mask_exclude: bool = False,
    default_factory: AnyElementFactory[..., AnyXmlElement] | None = None,
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

    if `default_factory` is not None, the given factory will be set as
    the default factory for all elements yielded by this parser.

    Implementations are also free to decide how to handle errors, but are
    encouraged to raise a `ParsingError` to align with the rest of the
    library's error handling.

    Args:
        mask: A tag name, tuple of tag names, or None.
        mask_exclude: Whether to yield only elements in the `mask` or all
          elements except those in the `mask`.
        default_factory: A callable that creates XML elements from tag/attrib,
          or None to unset the instance default.

    Yields:
        BaseTmxElement: Parsed TMX elements from the source file based on the
          provided `mask`.

    Raises:
        ParsingError: If a TMX element cannot be parsed.
        ValueError: If the provided mask includes unsupported tag names.
    """
    ...
