from itertools import chain
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
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Prop)
    element = self.backend.make_elem("prop")
    self._set_attribute(element, "type", obj.type, True)
    self._set_attribute(element, f"{XML_NS}lang", obj.lang, False)
    self._set_attribute(element, "o-encoding", obj.o_encoding, False)
    self.backend.set_text(element, obj.text)
    return element


class NoteSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Note)
    element = self.backend.make_elem("note")
    self._set_attribute(element, f"{XML_NS}lang", obj.lang, False)
    self._set_attribute(element, "o-encoding", obj.o_encoding, False)
    self.backend.set_text(element, obj.text)
    return element


class HeaderSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Header)
    element = self.backend.make_elem("header")
    self._set_attribute(element, "creationtool", obj.creationtool, True)
    self._set_attribute(element, "creationtoolversion", obj.creationtoolversion, True)
    self._set_enum_attribute(element, "segtype", obj.segtype, Segtype, True)
    self._set_attribute(element, "o-tmf", obj.o_tmf, False)
    self._set_attribute(element, "adminlang", obj.adminlang, True)
    self._set_attribute(element, "srclang", obj.srclang, True)
    self._set_attribute(element, "datatype", obj.datatype, True)
    self._set_attribute(element, "o-encoding", obj.o_encoding, False)
    self._set_dt_attribute(element, "creationdate", obj.creationdate, False)
    self._set_attribute(element, "creationid", obj.creationid, False)
    self._set_dt_attribute(element, "changedate", obj.changedate, False)
    self._set_attribute(element, "changeid", obj.changeid, False)
    for child in chain[Prop | Note](obj.props, obj.notes):
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(element, child_element)
    return element


class TuvSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Tuv)
    element = self.backend.make_elem("tuv")
    self._set_attribute(element, f"{XML_NS}lang", obj.lang, True)
    self._set_attribute(element, "o-encoding", obj.o_encoding, False)
    self._set_attribute(element, "datatype", obj.datatype, False)
    self._set_int_attribute(element, "usagecount", obj.usagecount, False)
    self._set_dt_attribute(element, "lastusagedate", obj.lastusagedate, False)
    self._set_attribute(element, "creationtool", obj.creationtool, False)
    self._set_attribute(element, "creationtoolversion", obj.creationtoolversion, False)
    self._set_dt_attribute(element, "creationdate", obj.creationdate, False)
    self._set_attribute(element, "creationid", obj.creationid, False)
    self._set_dt_attribute(element, "changedate", obj.changedate, False)
    self._set_attribute(element, "changeid", obj.changeid, False)
    self._set_attribute(element, "o-tmf", obj.o_tmf, False)
    for child in chain[Prop | Note](obj.props, obj.notes):
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(element, child_element)
    seg_element = self.backend.make_elem("seg")
    self.serialize_content_into(obj, seg_element)
    self.backend.append(element, seg_element)
    return element


class TuSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Tu)
    element = self.backend.make_elem("tu")
    self._set_attribute(element, "tuid", obj.tuid, False)
    self._set_attribute(element, "o-encoding", obj.o_encoding, False)
    self._set_attribute(element, "datatype", obj.datatype, False)
    self._set_int_attribute(element, "usagecount", obj.usagecount, False)
    self._set_dt_attribute(element, "lastusagedate", obj.lastusagedate, False)
    self._set_attribute(element, "creationtool", obj.creationtool, False)
    self._set_attribute(element, "creationtoolversion", obj.creationtoolversion, False)
    self._set_dt_attribute(element, "creationdate", obj.creationdate, False)
    self._set_attribute(element, "creationid", obj.creationid, False)
    self._set_dt_attribute(element, "changedate", obj.changedate, False)
    self._set_enum_attribute(element, "segtype", obj.segtype, Segtype, False)
    self._set_attribute(element, "changeid", obj.changeid, False)
    self._set_attribute(element, "o-tmf", obj.o_tmf, False)
    self._set_attribute(element, "srclang", obj.srclang, False)
    for child in chain[Prop | Note | Tuv](obj.props, obj.notes, obj.variants):
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(element, child_element)
    return element


class TmxSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Tmx)
    element = self.backend.make_elem("tmx")
    self._set_attribute(element, "version", obj.version, True)
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


class BptSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Bpt)
    element = self.backend.make_elem("bpt")
    self._set_int_attribute(element, "i", obj.i, True)
    self._set_int_attribute(element, "x", obj.x, False)
    self._set_attribute(element, "type", obj.type, False)
    self.serialize_content_into(obj, element)
    return element


class EptSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Ept)
    element = self.backend.make_elem("ept")
    self._set_int_attribute(element, "i", obj.i, True)
    self.serialize_content_into(obj, element)
    return element


class HiSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Hi)
    element = self.backend.make_elem("hi")
    self._set_int_attribute(element, "x", obj.x, False)
    self._set_attribute(element, "type", obj.type, False)
    self.serialize_content_into(obj, element)
    return element


class ItSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, It)
    element = self.backend.make_elem("it")
    self._set_enum_attribute(element, "pos", obj.pos, Pos, True)
    self._set_int_attribute(element, "x", obj.x, False)
    self._set_attribute(element, "type", obj.type, False)
    self.serialize_content_into(obj, element)
    return element


class PhSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Ph)
    element = self.backend.make_elem("ph")
    self._set_int_attribute(element, "x", obj.x, False)
    self._set_enum_attribute(element, "assoc", obj.assoc, Assoc, False)
    self._set_attribute(element, "type", obj.type, False)
    self.serialize_content_into(obj, element)
    return element


class SubSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement:
    obj = self._check_obj_type(obj, Sub)
    element = self.backend.make_elem("sub")
    self._set_attribute(element, "datatype", obj.datatype, False)
    self._set_attribute(element, "type", obj.type, False)
    self.serialize_content_into(obj, element)
    return element
