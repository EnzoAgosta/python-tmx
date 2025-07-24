from __future__ import annotations

from dataclasses import dataclass

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  P,
  R,
)
from PythonTmx.utils import raise_serialization_errors


@dataclass(slots=True)
class Prop(BaseTmxElement):
  value: str
  type: str
  encoding: str | None = None
  lang: str | None = None

  @classmethod
  def from_xml(cls: type[Prop], element: AnyXmlElement) -> Prop:
    try:
      if str(element.tag) != "prop":
        raise_serialization_errors(
          element.tag, ValueError(), expected="prop", actual=str(element.tag)
        )
      if not element.text:
        raise_serialization_errors(element.tag, ValueError(), missing="text")
      if "type" not in element.attrib:
        raise_serialization_errors(element.tag, KeyError(), missing="type")
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
