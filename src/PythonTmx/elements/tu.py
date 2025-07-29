from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from PythonTmx.core import (
  AnyElementFactory,
  AnyXmlElement,
  BaseTmxElement,
  ConvertibleToInt,
  R,
  WithChildren,
)
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.elements.tuv import Tuv
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


class Tu(BaseTmxElement, WithChildren[Prop | Note | Tuv]):
  __slots__ = (
    "tuid",
    "encoding",
    "datatype",
    "usagecount",
    "lastusagedate",
    "creationtool",
    "creationtoolversion",
    "creationdate",
    "creationid",
    "changedate",
    "segtype",
    "changeid",
    "tmf",
    "srclang",
    "_children",
  )
  tuid: str | None
  encoding: str | None
  datatype: str | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  segtype: str | None
  changeid: str | None
  tmf: str | None
  srclang: str | None
  _children: list[Prop | Note | Tuv]

  def __init__(
    self,
    tuid: str | None = None,
    encoding: str | None = None,
    datatype: str | None = None,
    usagecount: ConvertibleToInt | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    segtype: str | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    srclang: str | None = None,
    children: Sequence[Note | Prop | Tuv] | None = None,
  ) -> None:
    self.tuid = tuid
    self.encoding = encoding
    self.datatype = datatype
    self.usagecount = int(usagecount) if usagecount is not None else usagecount
    self.lastusagedate = try_parse_datetime(lastusagedate, False)
    self.creationtool = creationtool
    self.creationtoolversion = creationtoolversion
    self.creationdate = try_parse_datetime(creationdate, False)
    self.creationid = creationid
    self.changedate = try_parse_datetime(changedate, False)
    self.segtype = segtype
    self.changeid = changeid
    self.tmf = tmf
    self.srclang = srclang
    self._children = [child for child in children] if children is not None else []

  @property
  def props(self) -> list[Prop]:
    return [child for child in self if isinstance(child, Prop)]

  @property
  def notes(self) -> list[Note]:
    return [child for child in self if isinstance(child, Note)]

  @property
  def tuvs(self) -> list[Tuv]:
    return [child for child in self if isinstance(child, Tuv)]

  @classmethod
  def from_xml(cls: type[Tu], element: AnyXmlElement) -> Tu:
    try:
      check_element_is_usable(element)
      if element.tag != "tu":
        raise WrongTagError(element.tag, "tu")

      children: list[Prop | Note | Tuv] = []
      for child in element:
        if child.tag == "prop":
          children.append(Prop.from_xml(child))
        elif child.tag == "note":
          children.append(Note.from_xml(child))
        elif child.tag == "tuv":
          children.append(Tuv.from_xml(child))
        else:
          raise WrongTagError(child.tag, "prop, note or tuv")

      return cls(
        tuid=element.attrib.get("tuid"),
        encoding=element.attrib.get("o-encoding"),
        datatype=element.attrib.get("datatype"),
        usagecount=element.attrib.get("usagecount"),
        lastusagedate=element.attrib.get("lastusagedate"),
        creationtool=element.attrib.get("creationtool"),
        creationtoolversion=element.attrib.get("creationtoolversion"),
        creationdate=element.attrib.get("creationdate"),
        creationid=element.attrib.get("creationid"),
        changedate=element.attrib.get("changedate"),
        segtype=element.attrib.get("segtype"),
        changeid=element.attrib.get("changeid"),
        tmf=element.attrib.get("o-tmf"),
        srclang=element.attrib.get("srclang"),
        children=children,
      )
    except (
      WrongTagError,
      NotMappingLikeError,
      RequiredAttributeMissingError,
      AttributeError,
      KeyError,
    ) as e:
      raise SerializationError(cls, e) from e

  def to_xml(self, factory: AnyElementFactory[..., R] | None = None) -> R:
    _factory = get_factory(self, factory)
    try:
      element = _factory("tu", self._make_attrib_dict())
      for child in self:
        element.append(child.to_xml(_factory))
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    attrs: dict[str, str] = {}
    if self.tuid is not None:
      if not isinstance(self.tuid, str):  # type: ignore
        raise ValidationError("tuid", str, type(self.tuid), None)
      attrs["tuid"] = self.tuid
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.datatype is not None:
      if not isinstance(self.datatype, str):  # type: ignore
        raise ValidationError("datatype", str, type(self.datatype), None)
      attrs["datatype"] = self.datatype
    if self.usagecount is not None:
      if not isinstance(self.usagecount, int):  # type: ignore
        raise ValidationError("usagecount", int, type(self.usagecount), None)
      attrs["usagecount"] = str(self.usagecount)
    if self.lastusagedate is not None:
      if not isinstance(self.lastusagedate, datetime):  # type: ignore
        raise ValidationError("lastusagedate", datetime, type(self.lastusagedate), None)
      attrs["lastusagedate"] = self.lastusagedate.strftime("%Y%m%dT%H%M%S%Z")
    if self.creationtool is not None:
      if not isinstance(self.creationtool, str):  # type: ignore
        raise ValidationError("creationtool", str, type(self.creationtool), None)
      attrs["creationtool"] = self.creationtool
    if self.creationtoolversion is not None:
      if not isinstance(self.creationtoolversion, str):  # type: ignore
        raise ValidationError(
          "creationtoolversion", str, type(self.creationtoolversion), None
        )
      attrs["creationtoolversion"] = self.creationtoolversion
    if self.creationdate is not None:
      if not isinstance(self.creationdate, datetime):  # type: ignore
        raise ValidationError("creationdate", datetime, type(self.creationdate), None)
      attrs["creationdate"] = self.creationdate.strftime("%Y%m%dT%H%M%S%Z")
    if self.creationid is not None:
      if not isinstance(self.creationid, str):  # type: ignore
        raise ValidationError("creationid", str, type(self.creationid), None)
      attrs["creationid"] = self.creationid
    if self.changedate is not None:
      if not isinstance(self.changedate, datetime):  # type: ignore
        raise ValidationError("changedate", datetime, type(self.changedate), None)
      attrs["changedate"] = self.changedate.strftime("%Y%m%dT%H%M%S%Z")
    if self.segtype is not None:
      if not isinstance(self.segtype, str):  # type: ignore
        raise ValidationError("segtype", str, type(self.segtype), None)
      attrs["segtype"] = self.segtype
    if self.changeid is not None:
      if not isinstance(self.changeid, str):  # type: ignore
        raise ValidationError("changeid", str, type(self.changeid), None)
      attrs["changeid"] = self.changeid
    if self.tmf is not None:
      if not isinstance(self.tmf, str):  # type: ignore
        raise ValidationError("tmf", str, type(self.tmf), None)
      attrs["o-tmf"] = self.tmf
    if self.srclang is not None:
      if not isinstance(self.srclang, str):  # type: ignore
        raise ValidationError("srclang", str, type(self.srclang), None)
      attrs["srclang"] = self.srclang
    return attrs
