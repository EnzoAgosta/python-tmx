from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
  WithChildren,
)
from PythonTmx.elements.header import Header
from PythonTmx.elements.tu import Tu
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  RequiredAttributeMissingError,
  SerializationError,
  ValidationError,
  WrongTagError,
)
from PythonTmx.utils import (
  check_element_is_usable,
  get_factory,
)

__all__ = ["Tmx"]


class Tmx(BaseTmxElement, WithChildren[Tu]):
  """Represents the root TMX element in a TMX file.

  The Tmx element is the root container for all TMX content. It contains a header
  element with metadata about the translation memory and a body element containing
  all the translation units (tu elements).

  A TMX file must have exactly one header element and one body element, with the
  body containing zero or more translation units.
  """

  __slots__ = ("header", "_children")
  header: Header
  """The header element containing TMX metadata and configuration."""
  _children: list[Tu]
  """List of Tu elements representing the translation units."""

  def __init__(
    self,
    header: Header,
    tus: list[Tu] | None = None,
  ) -> None:
    """Initialize a Tmx element.

    Args:
      header: The header element containing TMX metadata and configuration.
             This must be a valid Header instance.
      tus: Optional list of translation units. If None, starts with an empty list.
    """
    self.header = header
    self._children = [tu for tu in tus] if tus is not None else []

  @classmethod
  def from_xml(cls: type[Tmx], element: AnyXmlElement) -> Tmx:
    """Create a Tmx instance from an XML element.

    This method parses a TMX root element and creates a corresponding Tmx object.
    The XML element must have the tag "tmx" and cannot contain text content.

    The element must contain exactly one header element and one body element,
    with the body containing zero or more translation units.

    Args:
      element: The XML element to parse. Must have tag "tmx" and no text content.

    Returns:
      A new Tmx instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "tmx" or contains unexpected child tags.
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the tmx element has text content, missing header, or missing body.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "tmx":
        raise WrongTagError(element.tag, "tmx")
      if element.text is not None and not element.text.isspace():
        raise ValueError("Tmx element cannot have text")
      header: Header | None = None
      tus: list[Tu] | None = None
      for child in element:
        if child.tag == "header":
          if header is not None:
            raise WrongTagError(child.tag, "header") from ValueError("Multiple headers")
          header = Header.from_xml(child)
        elif child.tag == "body":
          if tus is not None:  # type: ignore
            raise WrongTagError(child.tag, "body") from ValueError("Multiple bodies")
          tus = []
          for tu in child:
            if not tu.tag == "tu":
              raise WrongTagError(tu.tag, "tu")
            tus.append(Tu.from_xml(tu))
        else:
          raise WrongTagError(child.tag, "header or body")
      if header is None:
        raise ValueError("Missing header")
      if tus is None:  # type: ignore
        raise ValueError("Missing body")
      return cls(header, tus)
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
      ValueError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    """Convert this Tmx instance to an XML element.

    Creates an XML element with tag "tmx" and the appropriate attributes.
    The header element is serialized and appended, followed by a body element
    containing all translation units.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Tmx.

    Raises:
      TypeError: If header is not a Header instance or any child is not a Tu instance.
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("tmx", self._make_attrib_dict())
      if not isinstance(self.header, Header):  # type: ignore
        raise TypeError(
          f"Unexpected child element in tmx element - Expected Header, got {type(self.header)!r}",
        )
      element.append(self.header.to_xml(factory=factory))
      body = _factory("body", {})
      for child in self:
        if not isinstance(child, Tu):  # type: ignore
          raise TypeError(
            f"Unexpected child element in tmx element - Expected Tu, got {type(child)!r}",
          )
        body.append(child.to_xml(factory=factory))
      element.append(body)
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Tmx.

    Builds the attribute dictionary that will be used when serializing
    this Tmx to XML. Currently only includes the version attribute.

    Returns:
      A dictionary mapping attribute names to string values.
    """
    return {"version": "1.4"}
