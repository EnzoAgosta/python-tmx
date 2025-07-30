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
  """Protocol defining the interface for XML elements.
  
  This protocol provides a backend-agnostic abstraction for XML elements,
  allowing the library to work with any XML library (lxml, ElementTree, etc.)
  without being tied to specific implementations.
  
  The protocol defines the minimum interface required for XML element operations,
  enabling maximum flexibility while maintaining type safety through runtime checks.
  
  Attributes:
    tag: The element's tag name.
    text: The element's text content.
    tail: The element's tail text (text after the element).
    attrib: The element's attributes dictionary.
  """
  tag: Any
  text: Any
  tail: Any
  attrib: Any

  def __iter__(self) -> Iterator[Any]: ...
  """Iterate over child elements."""

  def append(self, element: Any, /) -> None: ...
  """Append a child element."""


def set_default_factory(
  factory: AnyElementFactory[..., AnyXmlElement] | None,
) -> None:
  """Set the global default XML element factory.
  
  This function allows users to configure a default factory for XML element
  creation across the entire library. The factory is used when no specific
  factory is provided to individual operations.
  
  The factory pattern enables backend-agnostic XML element creation, supporting
  different XML libraries (lxml, ElementTree, etc.) through a consistent interface.
  
  Args:
    factory: The factory to set as default, or None to clear the default.
  """
  global DEFAULT_XML_FACTORY
  DEFAULT_XML_FACTORY = factory  # type: ignore # We're intentionally mutating the global


class AnyElementFactory(Protocol[P, R]):
  """Protocol defining the interface for XML element factories.
  
  This protocol ensures that any factory used for XML element creation
  accepts at minimum a tag name and attributes dictionary. The ParamSpec
  allows for flexible parameter signatures while enforcing the required
  interface.
  
  The factory pattern enables backend-agnostic XML element creation,
  supporting different XML libraries through a consistent interface.
  
  Attributes:
    P: The parameter specification for the factory function.
    R: The return type (must be bound to AnyXmlElement).
  """
  def __call__(
    self,
    tag: str,
    attrib: dict[str, str],
    /,
    *args: Any,
    **kwargs: Any,
  ) -> R: ...
  """Create an XML element with the given tag and attributes.
  
  Args:
    tag: The element's tag name.
    attrib: The element's attributes dictionary.
    *args: Additional positional arguments for the factory.
    **kwargs: Additional keyword arguments for the factory.
  
  Returns:
    An XML element implementing the AnyXmlElement protocol.
  """


class BaseTmxElement(ABC):
  """Abstract base class for all TMX elements.
  
  This class provides the foundation for all TMX element implementations,
  defining the common interface for serialization and deserialization.
  It serves as the core abstraction layer, separating data structure
  from XML library implementation details.
  
  The class enforces a consistent pattern where all elements must implement
  XML serialization/deserialization while remaining backend-agnostic through
  the factory pattern.
  
  Attributes:
    xml_factory: Optional factory for creating XML elements. If None,
                uses the global default factory or raises an error.
  """
  xml_factory: AnyElementFactory[..., AnyXmlElement] | None
  __slots__ = ("xml_factory",)

  def set_default_factory(self, factory: AnyElementFactory[P, R] | None) -> None:
    """Set the XML factory for this element instance.
    
    This method allows individual elements to override the global default
    factory, providing fine-grained control over XML element creation.
    
    Args:
      factory: The factory to use for this element, or None to use defaults.
    """
    self.xml_factory = factory

  @abstractmethod
  def to_xml(self, factory: AnyElementFactory[P, R] | None = None) -> R: ...
  """Convert this TMX element to an XML element.
  
  This method must be implemented by all subclasses to provide
  XML serialization functionality. The factory parameter allows
  for backend-agnostic XML element creation.
  
  Args:
    factory: Optional XML element factory. If None, uses the element's
             xml_factory or the global default factory.
  
  Returns:
    An XML element representing this TMX element.
  """

  @classmethod
  @abstractmethod
  def from_xml(cls: Type[Self], element: AnyXmlElement) -> BaseTmxElement: ...
  """Create a TMX element from an XML element.
  
  This class method must be implemented by all subclasses to provide
  XML deserialization functionality. It parses XML elements into
  corresponding TMX element instances.
  
  Args:
    element: The XML element to parse.
  
  Returns:
    A new TMX element instance with the parsed data.
  """

  @abstractmethod
  def _make_attrib_dict(self) -> dict[str, str]: ...
  """Create a dictionary of XML attributes for this element.
  
  This method must be implemented by all subclasses to provide
  attribute serialization functionality. It builds the attribute
  dictionary that will be used when serializing to XML.
  
  Returns:
    A dictionary mapping attribute names to string values.
  """


class WithChildren(Generic[ChildrenType]):
  """Generic mixin providing list-like behavior for elements with children.
  
  This mixin provides a consistent, type-safe interface for elements that
  contain child elements. It implements the MutableSequence protocol,
  ensuring that all child-manipulation methods operate on the underlying
  `_children` attribute without requiring manual implementation in each class.
  
  The generic type parameter `ChildrenType` allows for precise type checking
  of child elements, ensuring that only appropriate child types can be added
  to specific element types.
  
  This design follows the "lax input, strict output" philosophy, providing
  runtime validation while maintaining type safety through generics.
  
  Attributes:
    _children: The list of child elements. Must be implemented by subclasses.
  """
  __slots__ = ()
  _children: list[ChildrenType]

  def __len__(self) -> int:
    """Return the number of child elements."""
    return len(self._children)

  def __iter__(self) -> Iterator[ChildrenType]:
    """Iterate over child elements."""
    return iter(self._children)

  @overload
  def __getitem__(self, idx: int) -> ChildrenType: ...
  @overload
  def __getitem__(self, idx: slice) -> list[ChildrenType]: ...
  def __getitem__(self, idx: int | slice) -> ChildrenType | list[ChildrenType]:
    """Get child element(s) by index or slice."""
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
    """Set child element(s) by index or slice.
    
    Args:
      idx: The index or slice to set.
      value: The child element(s) to set.
    
    Raises:
      TypeError: If the value type doesn't match the expected ChildrenType.
    """
    if isinstance(idx, slice):
      if not isinstance(value, Iterable):
        raise TypeError("value must be an iterable")
      self._children[idx] = value
    else:
      if isinstance(value, Iterable):
        raise TypeError("value must be a single element")
      self._children[idx] = value

  def __delitem__(self, idx: int | slice) -> None:
    """Delete child element(s) by index or slice."""
    del self._children[idx]

  def append(self, value: ChildrenType) -> None:
    """Append a child element to the end of the list."""
    self._children.append(value)

  def extend(self, values: Iterable[ChildrenType]) -> None:
    """Extend the child list with multiple elements."""
    self._children.extend(values)

  def insert(self, idx: SupportsIndex, value: ChildrenType) -> None:
    """Insert a child element at the specified index."""
    self._children.insert(idx, value)

  def pop(self, idx: SupportsIndex = -1) -> ChildrenType:
    """Remove and return a child element by index.
    
    Args:
      idx: The index of the element to pop. Defaults to -1 (last element).
    
    Returns:
      The removed child element.
    """
    return self._children.pop(idx)

  def remove(self, value: ChildrenType) -> None:
    """Remove the first occurrence of a child element."""
    self._children.remove(value)

  def clear(self) -> None:
    """Remove all child elements."""
    self._children.clear()


class TmxParser(ABC):
  """Abstract base class for TMX file parsers.
  
  This class defines the interface for TMX file parsing, separating
  the concerns of file I/O and XML library interaction from the
  data structure definitions. This enables different parsing strategies
  and XML library backends while maintaining a consistent interface.
  
  The parser abstraction allows for flexible file handling, supporting
  different input sources and XML processing libraries through a unified
  interface.
  
  Attributes:
    source: The path to the TMX file to be parsed.
  """
  source: Path

  @abstractmethod
  def __init__(self, source: PathLike[str] | Path | str) -> None: ...
  """Initialize the parser with a TMX file source.
  
  Args:
    source: The path to the TMX file to parse. Can be a string,
            Path object, or any PathLike object.
  """

  @abstractmethod
  def iter(
    self,
    mask: str | tuple[str, ...] | None = None,
    mask_exclude: bool = False,
    default_factory: AnyElementFactory[..., AnyXmlElement] | None = None,
  ) -> Iterator[BaseTmxElement]: ...
  """Iterate over TMX elements in the file.
  
  This method provides a streaming interface for processing large TMX files,
  allowing memory-efficient processing of translation units and other elements.
  
  Args:
    mask: Optional tag name(s) to filter elements. If None, returns all elements.
    mask_exclude: If True, exclude elements matching the mask. If False,
                  include only elements matching the mask.
    default_factory: Optional XML element factory to use for parsing.
                    If None, uses the global default factory.
  
  Yields:
    TMX elements matching the specified criteria.
  """


@runtime_checkable
class SupportsTrunc(Protocol):
  """Protocol for objects that support truncation to integers.
  
  This protocol defines the interface for objects that can be converted
  to integers through truncation. It's used for type-safe conversion
  of various numeric types to integers.
  """
  def __trunc__(self) -> int: ...
  """Return the truncated integer value."""


type ConvertibleToInt = (
  str | bytes | bytearray | memoryview | SupportsInt | SupportsIndex | SupportsTrunc
)
"""Type alias for values that can be converted to integers.

This type alias defines the set of types that can be safely converted
to integers, including strings, bytes, and various numeric protocols.
It's used throughout the library for flexible input handling while
maintaining type safety.
"""
