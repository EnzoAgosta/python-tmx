from __future__ import annotations

from dataclasses import dataclass, field
from types import NoneType

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
)
from PythonTmx.errors import SerializationError
from PythonTmx.utils import (
  ensure_element_structure,
  ensure_required_attributes_are_present,
  get_factory,
  raise_serialization_errors,
)


@dataclass(slots=True)
class Map(BaseTmxElement):
  unicode: str = field(metadata={"expected_types": (str,)})
  xml_factory: AnyElementFactory[..., AnyXmlElement] | None = None
  code: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )
  ent: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )
  subst: str | None = field(
    default=None, metadata={"expected_types": (str, NoneType)}
  )

  @classmethod
  def from_xml(cls: type[Map], element: AnyXmlElement) -> Map:
    ensure_element_structure(element, expected_tag="map")
    if element.text:
      raise SerializationError(
        f"Unexpected text in map element: {element.text!r}",
        "map",
        Exception(),
      )
    ensure_required_attributes_are_present(element, ("unicode",))
    try:
      return cls(
        unicode=element.attrib["unicode"],
        code=element.attrib.get("code", None),
        ent=element.attrib.get("ent", None),
        subst=element.attrib.get("subst", None),
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    return _factory("map", self._make_attrib_dict(tuple()))
