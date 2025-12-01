from itertools import chain
from python_tmx.base.errors import XmlSerializationError
from python_tmx.base.types import (
  Assoc,
  BaseElement,
  Bpt,
  Ept,
  Header,
  Hi,
  It,
  Note,
  Ph,
  Pos,
  Prop,
  Segtype,
  Sub,
  Tmx,
  Tu,
  Tuv,
)
from python_tmx.xml import XML_NS, T_XmlElement
from python_tmx.xml.serialization.base import (
  BaseElementSerializer,
  InlineContentSerializerMixin,
)

__all__ = [
  "PropSerializer",
  "NoteSerializer",
  "HeaderSerializer",
  "BptSerializer",
  "EptSerializer",
  "ItSerializer",
  "PhSerializer",
  "SubSerializer",
  "HiSerializer",
  "TuvSerializer",
  "TuSerializer",
  "TmxSerializer",
]


class PropSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Prop):
      return None
    element = self.backend.make_elem("prop")
    self._set_attribute(element, obj.type, "type", True)
    self._set_attribute(element, obj.lang, f"{XML_NS}lang", False)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self.backend.set_text(element, obj.text)
    return element


class NoteSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Note):
      return None
    element = self.backend.make_elem("note")
    self._set_attribute(element, obj.lang, f"{XML_NS}lang", True)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self.backend.set_text(element, obj.text)
    return element


class HeaderSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Header):
      return None
    element = self.backend.make_elem("header")
    self._set_attribute(element, obj.creationtool, "creationtool", True)
    self._set_attribute(element, obj.creationtoolversion, "creationtoolversion", True)
    self._set_enum_attribute(element, obj.segtype, "segtype", Segtype, True)
    self._set_attribute(element, obj.o_tmf, "o-tmf", False)
    self._set_attribute(element, obj.adminlang, "adminlang", True)
    self._set_attribute(element, obj.srclang, "srclang", True)
    self._set_attribute(element, obj.datatype, "datatype", True)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self._set_dt_attribute(element, obj.creationdate, "creationdate", False)
    self._set_attribute(element, obj.creationid, "creationid", False)
    self._set_dt_attribute(element, obj.changedate, "changedate", False)
    self._set_attribute(element, obj.changeid, "changeid", False)
    for child in chain[Prop | Note](obj.props, obj.notes):
      if isinstance(child, (Prop, Note)):
        child_element = self.emit(child)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Header",
          type(child).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(
            f"Invalid child element {type(child).__name__!r} in Header"
          )
    return element


class TuvSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tuv):
      return None
    element = self.backend.make_elem("tuv")
    self._set_attribute(element, obj.lang, f"{XML_NS}lang", True)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self._set_attribute(element, obj.datatype, "datatype", False)
    self._set_int_attribute(element, obj.usagecount, "usagecount", False)
    self._set_dt_attribute(element, obj.lastusagedate, "lastusagedate", False)
    self._set_attribute(element, obj.creationtool, "creationtool", False)
    self._set_attribute(element, obj.creationtoolversion, "creationtoolversion", False)
    self._set_dt_attribute(element, obj.creationdate, "creationdate", False)
    self._set_attribute(element, obj.creationid, "creationid", False)
    self._set_dt_attribute(element, obj.changedate, "changedate", False)
    self._set_attribute(element, obj.changeid, "changeid", False)
    self._set_attribute(element, obj.o_tmf, "o-tmf", False)
    for child in chain[Prop | Note](obj.props, obj.notes):
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(element, child_element)
    seg_element = self.backend.make_elem("seg")
    self.serialize_content(obj, seg_element, (Bpt, Ept, Ph, It, Hi))
    self.backend.append(element, seg_element)
    return element


class TuSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tu):
      return None
    element = self.backend.make_elem("tu")
    self._set_attribute(element, obj.tuid, "tuid", False)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self._set_attribute(element, obj.datatype, "datatype", False)
    self._set_int_attribute(element, obj.usagecount, "usagecount", False)
    self._set_dt_attribute(element, obj.lastusagedate, "lastusagedate", False)
    self._set_attribute(element, obj.creationtool, "creationtool", False)
    self._set_attribute(element, obj.creationtoolversion, "creationtoolversion", False)
    self._set_dt_attribute(element, obj.creationdate, "creationdate", False)
    self._set_attribute(element, obj.creationid, "creationid", False)
    self._set_dt_attribute(element, obj.changedate, "changedate", False)
    self._set_enum_attribute(element, obj.segtype, "segtype", Segtype, False)
    self._set_attribute(element, obj.changeid, "changeid", False)
    self._set_attribute(element, obj.o_tmf, "o-tmf", False)
    self._set_attribute(element, obj.srclang, "srclang", False)
    for child in chain[Prop | Note | Tuv](obj.props, obj.notes, obj.variants):
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(element, child_element)
    return element


class TmxSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tmx):
      return None
    element = self.backend.make_elem("tmx")
    self._set_attribute(element, obj.version, "version", True)
    header_element = self.emit(obj.header)
    if header_element is not None:
      self.backend.append(element, header_element)
    body_element = self.backend.make_elem("body")
    for child in obj.body:
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(body_element, child_element)
    self.backend.append(element, body_element)
    return element


class BptSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Bpt):
      return None
    element = self.backend.make_elem("bpt")
    self._set_int_attribute(element, obj.i, "i", True)
    self._set_int_attribute(element, obj.x, "x", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Sub,))
    return element


class EptSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Ept):
      return None
    element = self.backend.make_elem("ept")
    self._set_int_attribute(element, obj.i, "i", True)
    self.serialize_content(obj, element, (Sub,))
    return element


class HiSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Hi):
      return None
    element = self.backend.make_elem("hi")
    self._set_int_attribute(element, obj.x, "x", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
    return element


class ItSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, It):
      return None
    element = self.backend.make_elem("it")
    self._set_enum_attribute(element, obj.pos, "pos", Pos, True)
    self._set_int_attribute(element, obj.x, "x", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Sub,))
    return element


class PhSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Ph):
      return None
    element = self.backend.make_elem("ph")
    self._set_int_attribute(element, obj.x, "x", False)
    self._set_enum_attribute(element, obj.assoc, "assoc", Assoc, False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Sub,))
    return element


class SubSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Sub):
      return None
    element = self.backend.make_elem("sub")
    self._set_attribute(element, obj.datatype, "datatype", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
    return element
