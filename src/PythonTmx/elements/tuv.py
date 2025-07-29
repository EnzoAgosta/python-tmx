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
from PythonTmx.elements.inline import Bpt, Ept, Hi, It, Ph, Ut
from PythonTmx.elements.note import Note
from PythonTmx.elements.prop import Prop
from PythonTmx.enums import DATATYPE
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

__all__ = ["Tuv"]


class Tuv(BaseTmxElement, WithChildren[Prop | Note]):
  __slots__ = (
    "lang",
    "encoding",
    "datatype",
    "usagecount",
    "lastusagedate",
    "creationtool",
    "creationtoolversion",
    "creationdate",
    "creationid",
    "changedate",
    "changeid",
    "tmf",
    "_children",
    "segment",
  )
  lang: str
  encoding: str | None
  datatype: str | DATATYPE | None
  usagecount: int | None
  lastusagedate: datetime | None
  creationtool: str | None
  creationtoolversion: str | None
  creationdate: datetime | None
  creationid: str | None
  changedate: datetime | None
  changeid: str | None
  tmf: str | None
  _children: list[Prop | Note]
  segment: list[Bpt | Ept | It | Ph | Hi | Ut | str]

  def __init__(
    self,
    lang: str,
    encoding: str | None = None,
    datatype: str | DATATYPE | None = None,
    usagecount: ConvertibleToInt | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    children: Sequence[Note | Prop] | None = None,
    segment: Sequence[Bpt | Ept | It | Ph | Hi | Ut | str] | None = None,
  ) -> None:
    self.lang = lang
    self.encoding = encoding
    self.usagecount = int(usagecount) if usagecount is not None else usagecount
    self.lastusagedate = try_parse_datetime(lastusagedate, False)
    self.creationtool = creationtool
    self.creationtoolversion = creationtoolversion
    self.creationdate = try_parse_datetime(creationdate, False)
    self.creationid = creationid
    self.changedate = try_parse_datetime(changedate, False)
    self.changeid = changeid
    self.tmf = tmf
    if datatype is not None:
      try:
        self.datatype = DATATYPE(datatype)
      except ValueError:
        self.datatype = datatype
    else:
      self.datatype = DATATYPE.UNKNOWN
    self._children = [child for child in children] if children is not None else []
    self.segment = [child for child in segment] if segment is not None else []

  @property
  def props(self) -> list[Prop]:
    return [child for child in self if isinstance(child, Prop)]

  @property
  def notes(self) -> list[Note]:
    return [child for child in self if isinstance(child, Note)]

  @classmethod
  def from_xml(cls: type[Tuv], element: AnyXmlElement) -> Tuv:
    def parse_seg(
      seg: AnyXmlElement,
    ) -> list[Bpt | Ept | It | Ph | Hi | Ut | str]:
      result: list[Bpt | Ept | It | Ph | Hi | Ut | str] = []
      if seg.text is not None:
        result.append(seg.text)
      for child in seg:
        match child.tag:
          case "bpt":
            result.append(Bpt.from_xml(child))
          case "ept":
            result.append(Ept.from_xml(child))
          case "it":
            result.append(It.from_xml(child))
          case "ph":
            result.append(Ph.from_xml(child))
          case "hi":
            result.append(Hi.from_xml(child))
          case "ut":
            result.append(Ut.from_xml(child))
          case _:
            raise WrongTagError(child.tag, "bpt|ept|it|ph|hi|ut")
        if child.tail is not None:
          result.append(child.tail)
      return result

    try:
      check_element_is_usable(element)
      if element.tag != "tuv":
        raise WrongTagError(element.tag, "tuv")
      if element.text is not None:
        raise ValueError("tuv element cannot have text")
      segment: list[Bpt | Ept | It | Ph | Hi | Ut | str] = []
      children: list[Prop | Note] = []
      for child in element:
        match child.tag:
          case "prop":
            children.append(Prop.from_xml(child))
          case "note":
            children.append(Note.from_xml(child))
          case "seg":
            segment.extend(parse_seg(child))
          case _:
            raise WrongTagError(child.tag, "prop, note or seg")

      return cls(
        lang=element.attrib["{http://www.w3.org/XML/1998/namespace}lang"],
        encoding=element.attrib.get("o-encoding"),
        datatype=element.attrib.get("datatype"),
        usagecount=element.attrib.get("usagecount"),
        lastusagedate=element.attrib.get("lastusagedate"),
        creationtool=element.attrib.get("creationtool"),
        creationtoolversion=element.attrib.get("creationtoolversion"),
        creationdate=element.attrib.get("creationdate"),
        creationid=element.attrib.get("creationid"),
        changedate=element.attrib.get("changedate"),
        changeid=element.attrib.get("changeid"),
        tmf=element.attrib.get("o-tmf"),
        children=children,
        segment=segment,
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
    try:
      _factory = get_factory(self, factory)
      element = _factory("tuv", self._make_attrib_dict())
      for child in self:
        if not isinstance(child, (Note, Prop)):  # type: ignore
          raise TypeError(
            f"Unexpected child element in tuv element - Expected Note or Prop, got {type(child):r}",
          )
        element.append(child.to_xml(factory=factory))
      seg = _factory("seg", {})
      current = seg
      for elem in self.segment:
        if isinstance(elem, str):
          if seg.text is None:
            seg.text = elem
          elif current is seg:
            seg.text += elem
          else:
            current.tail = elem
        elif isinstance(elem, (Bpt, Ept, It, Ph, Hi, Ut)):  # type: ignore
          current = elem.to_xml(factory=_factory)
          seg.append(current)
        else:
          raise TypeError(
            f"Unexpected child element in segment - Expected str, Bpt, Ept, It, Ph, Hi or Ut, got {type(elem)!r}"
          )
      element.append(seg)
      return element
    except ValidationError as e:
      raise DeserializationError(self, e) from e

  def _make_attrib_dict(self) -> dict[str, str]:
    if not isinstance(self.lang, str):  # type: ignore
      raise ValidationError("lang", str, type(self.lang), None)
    attrs: dict[str, str] = {"{http://www.w3.org/XML/1998/namespace}lang": self.lang}
    if self.encoding is not None:
      if not isinstance(self.encoding, str):  # type: ignore
        raise ValidationError("encoding", str, type(self.encoding), None)
      attrs["o-encoding"] = self.encoding
    if self.datatype is not None:
      if not isinstance(self.datatype, (str, DATATYPE)):  # type: ignore
        raise ValidationError("datatype", (str, DATATYPE), type(self.datatype), None)
      attrs["datatype"] = (
        self.datatype.value if isinstance(self.datatype, DATATYPE) else self.datatype
      )
    if self.usagecount is not None:
      if not isinstance(self.usagecount, int):  # type: ignore
        raise ValidationError("usagecount", int, type(self.usagecount), None)
      attrs["usagecount"] = str(self.usagecount)
    if self.lastusagedate is not None:
      if not isinstance(self.lastusagedate, datetime):  # type: ignore
        raise ValidationError("lastusagedate", datetime, type(self.lastusagedate), None)
      attrs["lastusagedate"] = self.lastusagedate.strftime("%Y%m%dT%H%M%SZ")
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
    if self.tmf is not None:
      if not isinstance(self.tmf, str):  # type: ignore
        raise ValidationError("tmf", str, type(self.tmf), None)
      attrs["o-tmf"] = self.tmf
    return attrs
