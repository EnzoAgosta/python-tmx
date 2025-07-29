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

__all__ = ["Note"]


class Note(BaseTmxElement):
  __slots__ = ("text", "encoding", "lang")
  text: str
  encoding: str | None
  lang: str | None

  def __init__(
    self,
    text: str,
    encoding: str | None = None,
    lang: str | None = None,
  ) -> None:
    self.text = text
    self.encoding = encoding
    self.lang = lang

  @classmethod
  def from_xml(cls: type[Note], element: AnyXmlElement) -> Note:
    try:
      check_element_is_usable(element)
      if element.tag != "note":
        raise WrongTagError(element.tag, "note")
      if element.text is None:
        raise ValueError("Note element must have text")
      return cls(
        text=element.text,
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
      element = _factory("note", self._make_attrib_dict())
      if not isinstance(self.text, str):  # type: ignore
        raise ValidationError("note", str, type(self.text), None)
      element.text = self.text
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.lang is not None:
      if not isinstance(self.lang, str):  # type: ignore
        raise ValidationError("lang", str, type(self.lang), None)
      attrs["{http://www.w3.org/XML/1998/namespace}lang"] = self.lang
    return attrs
