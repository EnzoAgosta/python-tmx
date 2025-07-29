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
    self.text = text
    self.encoding = encoding
    self.lang = lang
    try:
      self.type = TYPE(type)
    except ValueError:
      self.type = type

  @classmethod
  def from_xml(cls: Type[Prop], element: AnyXmlElement) -> Prop:
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
