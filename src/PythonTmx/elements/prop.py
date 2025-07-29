from __future__ import annotations

from typing import Type

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
from PythonTmx.enums import TYPE
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

__all__ = ["Prop"]


class Prop(BaseTmxElement):
  """Represents a property element in a TMX file.

  A property element contains metadata or configuration information about
  translation units or other TMX elements. Properties are key-value pairs
  that can store additional information not covered by standard TMX attributes.

  Properties are commonly used to store tool-specific settings, workflow
  information, or custom metadata that needs to be preserved during
  translation processes.

  Attributes:
    text: The property value/content.
    type: The property type/category (e.g., "project", "client", "domain").
    encoding: Optional encoding specification for the property text.
    lang: Optional language specification for the property content.
  """

  __slots__ = ("text", "type", "encoding", "lang")
  text: str
  type: str | TYPE
  encoding: str | None
  lang: str | None

  def __init__(
    self,
    text: str,
    type: str | TYPE,
    encoding: str | None = None,
    lang: str | None = None,
  ) -> None:
    """Initialize a Prop element.

    Args:
      text: The property value/content. Must be a non-empty string.
      type: The property type/category. Can be a string or TYPE enum value.
            Examples: "project", "client", "domain", "priority".
      encoding: Optional encoding specification (e.g., "UTF-8", "ISO-8859-1").
                If provided, will be serialized as the "o-encoding" attribute.
      lang: Optional language code for the property content (e.g., "en", "fr").
            If provided, will be serialized as the "xml:lang" attribute.

    Raises:
      ValueError: If text is empty or None.
    """
    self.text = text
    self.encoding = encoding
    self.lang = lang
    try:
      self.type = TYPE(type)
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Prop], element: AnyXmlElement) -> Prop:
    """Create a Prop instance from an XML element.

    This method parses a TMX property element and creates a corresponding Prop object.
    The XML element must have the tag "prop" and contain text content.

    Args:
      element: The XML element to parse. Must have tag "prop" and contain text.

    Returns:
      A new Prop instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "prop".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the prop element has no text content.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "prop":
        raise WrongTagError(element.tag, "prop")
      if element.text is None:
        raise ValueError("Prop element must have text")
      return cls(
        text=element.text,
        type=element.attrib["type"],
        encoding=element.attrib.get("o-encoding"),
        lang=element.attrib.get("{http://www.w3.org/XML/1998/namespace}lang"),
      )
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
    """Convert this Prop instance to an XML element.

    Creates an XML element with tag "prop" and the appropriate attributes.
    The property text becomes the element's text content.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Prop.

    Raises:
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      element = _factory("prop", self._make_attrib_dict())
      if not isinstance(self.text, str):  # type: ignore
        raise ValidationError("text", str, type(self.text), None)
      element.text = self.text
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Prop.

    Builds the attribute dictionary that will be used when serializing
    this Prop to XML. Only includes attributes that have non-None values.

    Returns:
      A dictionary mapping attribute names to string values.

    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.type, (TYPE, str)):  # type: ignore
      raise ValidationError("type", TYPE, type(self.type), None)
    attrs: dict[str, str] = {
      "type": self.type.value if isinstance(self.type, TYPE) else self.type
    }
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.lang is not None:
      if not isinstance(self.lang, str):  # type: ignore
        raise ValidationError("lang", str, type(self.lang), None)
      attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
    return attrs
