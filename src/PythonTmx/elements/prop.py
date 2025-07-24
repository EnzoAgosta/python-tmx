from __future__ import annotations

from dataclasses import dataclass

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  P,
  R,
)
from PythonTmx.utils import (
  ensure_element_structure,
  ensure_required_attributes_are_present,
  raise_serialization_errors,
)


@dataclass(slots=True)
class Prop(BaseTmxElement):
  value: str
  type: str
  encoding: str | None = None
  lang: str | None = None

  @classmethod
  def from_xml(cls: type[Prop], element: AnyXmlElement) -> Prop:
    ensure_element_structure(element, expected_tag="prop")
    if not element.text:
      raise_serialization_errors(element.tag, ValueError(), missing="text")
    ensure_required_attributes_are_present(element, ("type",))
    try:
      return cls(
        value=element.text,
        type=element.attrib["type"],
        encoding=element.attrib.get("encoding"),
        lang=element.attrib.get("lang"),
      )
    except Exception as e:
      raise_serialization_errors(element.tag, e)

  def to_xml(self, factory: AnyElementFactory[P, R]) -> R:
    element = factory(
      "prop",
      self._make_attrib_dict(),
    )
    element.text = self.value
    return element
