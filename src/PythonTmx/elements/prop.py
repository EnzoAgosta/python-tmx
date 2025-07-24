from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  P,
  R,
)


@dataclass(slots=True)
class Prop(BaseTmxElement):
  tag: ClassVar[str] = "prop"
  value: str
  type: str
  encoding: str | None = None
  lang: str | None = None

  @classmethod
  def from_xml(cls, element: AnyXmlElement) -> Prop:
    return cls(
      value=element.text,
      type=element.attrib["type"],
      encoding=element.attrib.get("encoding"),
      lang=element.attrib.get("lang"),
    )

  def to_xml(self, factory: AnyElementFactory[P, R]) -> R:
    element = factory(
      self.tag,
      self._make_attrib_dict(),
    )
    element.text = self.value
    return element
