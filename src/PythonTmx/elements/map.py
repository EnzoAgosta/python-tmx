from __future__ import annotations

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
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

__all__ = ["Map"]


class Map(BaseTmxElement):
  """Represents a map element in a TMX file.

  A map element defines character mapping rules for text processing in TMX files.
  Maps are used to specify how certain characters or character sequences should
  be handled during translation, typically for special characters, entities,
  or encoding conversions.

  Maps are commonly used within user-defined entities (ude) elements to provide
  custom character mapping rules for specific translation contexts or tools.
  """

  __slots__ = ("unicode", "code", "ent", "subst")
  unicode: str
  """The Unicode character or sequence being mapped"""
  code: str | None
  """Optional code point or entity reference for the mapping."""
  ent: str | None
  """Optional entity name for the mapping."""
  subst: str | None
  """Optional substitution text for the mapping."""

  def __init__(
    self,
    unicode: str,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
  ) -> None:
    """Initialize a Map element.

    Args:
      unicode: The Unicode character or sequence being mapped. This is the
               source character(s) that will be mapped.
      code: Optional code point or entity reference (e.g., "&#x20AC;" for euro).
            If provided, will be serialized as the "code" attribute.
      ent: Optional entity name for the mapping (e.g., "&euro;").
           If provided, will be serialized as the "ent" attribute.
      subst: Optional substitution text that should replace the unicode character.
             If provided, will be serialized as the "subst" attribute.
    """
    self.unicode = unicode
    self.code = code
    self.ent = ent
    self.subst = subst

  @classmethod
  def from_xml(cls: type[Map], element: AnyXmlElement) -> Map:
    """Create a Map instance from an XML element.

    This method parses a TMX map element and creates a corresponding Map object.
    The XML element must have the tag "map" and cannot contain text content.

    Args:
      element: The XML element to parse. Must have tag "map" and no text content.

    Returns:
      A new Map instance with the parsed data.

    Raises:
      WrongTagError: If the element tag is not "map".
      RequiredAttributeMissingError: If the element lacks required attributes.
      NotMappingLikeError: If the element's attrib is not a mapping.
      ValueError: If the map element has text content.
      SerializationError: If any other parsing error occurs.
    """
    try:
      check_element_is_usable(element)
      if element.tag != "map":
        raise WrongTagError(element.tag, "map")
      if element.text is not None:
        raise ValueError("Map element cannot have text")
      return cls(
        unicode=element.attrib["unicode"],
        code=element.attrib.get("code", None),
        ent=element.attrib.get("ent", None),
        subst=element.attrib.get("subst", None),
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
    """Convert this Map instance to an XML element.

    Creates an XML element with tag "map" and the appropriate attributes.
    Map elements are self-closing and do not contain text content.

    Args:
      factory: Optional XML element factory. If None, uses the default factory
               or the instance's xml_factory.

    Returns:
      An XML element representing this Map.

    Raises:
      ValidationError: If any attribute has an invalid type.
      MissingDefaultFactoryError: If no factory is available.
      DeserializationError: If any other serialization error occurs.
    """
    _factory = get_factory(self, factory)
    try:
      return _factory("map", self._make_attrib_dict())
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(
    self,
  ) -> dict[str, str]:
    """Create a dictionary of XML attributes for this Map.

    Builds the attribute dictionary that will be used when serializing
    this Map to XML. Only includes attributes that have non-None values.

    Returns:
      A dictionary mapping attribute names to string values.

    Raises:
      ValidationError: If any attribute has an invalid type.
    """
    if not isinstance(self.unicode, str):  # type: ignore
      raise ValidationError("unicode", str, type(self.unicode), None)
    attrs: dict[str, str] = {"unicode": self.unicode}
    for k in ("code", "ent", "subst"):
      v = getattr(self, k)
      if v is None:
        continue
      if not isinstance(v, str):  # type: ignore
        raise ValidationError(k, str, type(v), None)
      attrs[k] = v
    return attrs
