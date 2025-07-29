from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  R,
  WithChildren,
)
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.ude import Ude
from PythonTmx.enums import DATATYPE, SEGTYPE
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
  try_parse_datetime,
)

__all__ = ["Header"]


class Header(BaseTmxElement, WithChildren[Note | Prop | Ude]):
  __slots__ = (
    "creationtool",
    "creationtoolversion",
    "segtype",
    "tmf",
    "adminlang",
    "srclang",
    "datatype",
    "encoding",
    "creationdate",
    "creationid",
    "changedate",
    "changeid",
    "_children",
  )
  creationtool: str
  creationtoolversion: str
  segtype: SEGTYPE
  tmf: str
  adminlang: str
  srclang: str
  datatype: str | DATATYPE
  encoding: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  _children: list[Note | Prop | Ude]

  def __init__(
    self,
    creationtool: str,
    creationtoolversion: str,
    segtype: SEGTYPE | str,
    tmf: str,
    adminlang: str,
    srclang: str,
    datatype: str | DATATYPE,
    encoding: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    children: Sequence[Note | Prop | Ude] | None = None,
  ) -> None:
    self.creationtool = creationtool
    self.creationtoolversion = creationtoolversion
    self.tmf = tmf
    self.adminlang = adminlang
    self.srclang = srclang
    self.encoding = encoding
    self.creationid = creationid
    self.creationdate = try_parse_datetime(creationdate, False)
    self.changeid = changeid
    self.changedate = try_parse_datetime(changedate, False)
    self._children = [child for child in children] if children is not None else []
    self.segtype = SEGTYPE(segtype)
    try:
      self.datatype = DATATYPE(datatype)
    except ValueError:
      self.datatype = datatype

  @property
  def notes(self) -> list[Note]:
    return [note for note in self._children if isinstance(note, Note)]

  @property
  def props(self) -> list[Prop]:
    return [prop for prop in self._children if isinstance(prop, Prop)]

  @property
  def udes(self) -> list[Ude]:
    return [ude for ude in self._children if isinstance(ude, Ude)]

  @classmethod
  def from_xml(cls: type[Header], element: AnyXmlElement) -> Header:
    def _dispatch(child: AnyXmlElement) -> Note | Prop | Ude:
      if child.tag == "ude":
        return Ude.from_xml(child)
      elif child.tag == "note":
        return Note.from_xml(child)
      elif child.tag == "prop":
        return Prop.from_xml(child)
      else:
        raise WrongTagError(child.tag, "ude, note or prop")

    try:
      check_element_is_usable(element)
      if element.tag != "header":
        raise WrongTagError(element.tag, "header")
      if element.text is not None:
        raise ValueError("Header element cannot have text")

      header: Header = cls(
        creationtool=element.attrib["creationtool"],
        creationtoolversion=element.attrib["creationtoolversion"],
        segtype=SEGTYPE(element.attrib["segtype"]),
        tmf=element.attrib["o-tmf"],
        adminlang=element.attrib["adminlang"],
        srclang=element.attrib["srclang"],
        datatype=element.attrib["datatype"],
        encoding=element.attrib.get("o-encoding", None),
        creationdate=element.attrib.get("creationdate", None),
        creationid=element.attrib.get("creationid", None),
        changedate=element.attrib.get("changedate", None),
        changeid=element.attrib.get("changeid", None),
        children=[_dispatch(child) for child in element],
      )
      try:
        header.datatype = DATATYPE(header.datatype)
      except ValueError:
        pass
      return header
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
      element = _factory("header", self._make_attrib_dict())
      for child in self:
        if not isinstance(child, Note | Prop | Ude):  # type: ignore
          raise TypeError(
            f"Unexpected child element in header element - Expected Ude, Note or Prop, got {type(child)!r}",
          )
        element.append(child.to_xml(factory=factory))
      return element
    except (TypeError, ValidationError) as e:
      raise DeserializationError(self, e) from e

  # Defensive coding, lots of type: ignore to shut up type checkers
  def _make_attrib_dict(self) -> dict[str, str]:
    if not isinstance(self.creationtool, str):  # type: ignore
      raise ValidationError("creationtool", str, type(self.creationtool), None)
    if not isinstance(self.creationtoolversion, str):  # type: ignore
      raise ValidationError(
        "creationtoolversion", str, type(self.creationtoolversion), None
      )
    if not isinstance(self.segtype, SEGTYPE):  # type: ignore
      raise ValidationError("segtype", SEGTYPE, type(self.segtype), None)
    if not isinstance(self.tmf, str):  # type: ignore
      raise ValidationError("tmf", str, type(self.tmf), None)
    if not isinstance(self.adminlang, str):  # type: ignore
      raise ValidationError("adminlang", str, type(self.adminlang), None)
    if not isinstance(self.srclang, str):  # type: ignore
      raise ValidationError("srclang", str, type(self.srclang), None)
    attrs: dict[str, str] = {
      "creationtool": self.creationtool,
      "creationtoolversion": self.creationtoolversion,
      "segtype": self.segtype.value,
      "o-tmf": self.tmf,
      "adminlang": self.adminlang,
      "srclang": self.srclang,
    }
    if not isinstance(self.datatype, (str, DATATYPE)):  # type: ignore
      raise ValidationError("datatype", str, type(self.datatype), None)
    attrs["datatype"] = (
      self.datatype if isinstance(self.datatype, str) else self.datatype.value
    )
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.creationdate is not None:
      if not isinstance(self.creationdate, datetime):  # type: ignore
        raise ValidationError("creationdate", datetime, type(self.creationdate), None)
      attrs["creationdate"] = self.creationdate.strftime("%Y%m%dT%H%M%SZ")
    if self.creationid is not None:
      if not isinstance(self.creationid, str):  # type: ignore
        raise ValidationError("creationid", str, type(self.creationid), None)
      attrs["creationid"] = self.creationid
    if self.changedate is not None:
      if not isinstance(self.changedate, datetime):  # type: ignore
        raise ValidationError("changedate", datetime, type(self.changedate), None)
      attrs["changedate"] = self.changedate.strftime("%Y%m%dT%H%M%SZ")
    if self.changeid is not None:
      if not isinstance(self.changeid, str):  # type: ignore
        raise ValidationError("changeid", str, type(self.changeid), None)
      attrs["changeid"] = self.changeid
    return attrs
