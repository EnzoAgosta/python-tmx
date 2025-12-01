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
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Prop):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("prop")
      self._set_attribute(obj, element, "type", True)
      self._set_attribute(obj, element, f"{XML_NS}lang", False)
      self._set_attribute(obj, element, "o-encoding", False)
      self.backend.set_text(element, obj.text)
      return element


class NoteSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Note):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("prop")
      self._set_attribute(obj, element, "type", True)
      self._set_attribute(obj, element, f"{XML_NS}lang", False)
      self._set_attribute(obj, element, "o-encoding", False)
      self.backend.set_text(element, obj.text)
      return element


class HeaderSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Header):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("header")
      self._set_attribute(obj, element, "creationtool", True)
      self._set_attribute(obj, element, "creationtoolversion", True)
      self._set_enum_attribute(obj, element, "segtype", Segtype, True)
      self._set_attribute(obj, element, "o-tmf", False)
      self._set_attribute(obj, element, "adminlang", True)
      self._set_attribute(obj, element, "srclang", True)
      self._set_attribute(obj, element, "datatype", True)
      self._set_attribute(obj, element, "o-encoding", False)
      self._set_dt_attribute(obj, element, "creationdate", False)
      self._set_attribute(obj, element, "creationid", False)
      self._set_dt_attribute(obj, element, "changedate", False)
      self._set_attribute(obj, element, "changeid", False)
      for child in chain[Prop | Note](obj.props, obj.notes):
        child_element = self.emit(child)
        if child_element is not None:
          self.backend.append(element, child_element)
      return element


class TuvSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tuv):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("tuv")
      self._set_attribute(obj, element, f"{XML_NS}lang", True)
      self._set_attribute(obj, element, "o-encoding", False)
      self._set_attribute(obj, element, "datatype", False)
      self._set_int_attribute(obj, element, "usagecount", False)
      self._set_dt_attribute(obj, element, "lastusagedate", False)
      self._set_attribute(obj, element, "creationtool", False)
      self._set_attribute(obj, element, "creationtoolversion", False)
      self._set_dt_attribute(obj, element, "creationdate", False)
      self._set_attribute(obj, element, "creationid", False)
      self._set_dt_attribute(obj, element, "changedate", False)
      self._set_attribute(obj, element, "changeid", False)
      self._set_attribute(obj, element, "o-tmf", False)
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
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("tu")
      self._set_attribute(obj, element, "tuid", False)
      self._set_attribute(obj, element, "o-encoding", False)
      self._set_attribute(obj, element, "datatype", False)
      self._set_int_attribute(obj, element, "usagecount", False)
      self._set_dt_attribute(obj, element, "lastusagedate", False)
      self._set_attribute(obj, element, "creationtool", False)
      self._set_attribute(obj, element, "creationtoolversion", False)
      self._set_dt_attribute(obj, element, "creationdate", False)
      self._set_attribute(obj, element, "creationid", False)
      self._set_dt_attribute(obj, element, "changedate", False)
      self._set_enum_attribute(obj, element, "segtype", Segtype, False)
      self._set_attribute(obj, element, "changeid", False)
      self._set_attribute(obj, element, "o-tmf", False)
      self._set_attribute(obj, element, "srclang", False)
      for child in chain[Prop | Note | Tuv](obj.props, obj.notes, obj.variants):
        child_element = self.emit(child)
        if child_element is not None:
          self.backend.append(element, child_element)
      return element


class TmxSerializer(BaseElementSerializer[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tmx):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("tmx")
      self._set_attribute(obj, element, "version", True)
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
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("bpt")
      self._set_int_attribute(obj, element, "i", True)
      self._set_int_attribute(obj, element, "x", False)
      self._set_attribute(obj, element, "type", False)
      self.serialize_content(obj, element, (Sub,))
      return element


class EptSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Ept):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("ept")
      self._set_int_attribute(obj, element, "i", True)
      self.serialize_content(obj, element, (Sub,))
      return element


class HiSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Hi):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("hi")
      self._set_int_attribute(obj, element, "x", False)
      self._set_attribute(obj, element, "type", False)
      self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
      return element


class ItSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, It):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("it")
      self._set_enum_attribute(obj, element, "pos", Pos, True)
      self._set_int_attribute(obj, element, "x", False)
      self._set_attribute(obj, element, "type", False)
      self.serialize_content(obj, element, (Sub,))
      return element


class PhSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Ph):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("ph")
      self._set_int_attribute(obj, element, "x", False)
      self._set_enum_attribute(obj, element, "assoc", Assoc, False)
      self._set_attribute(obj, element, "type", False)
      self.serialize_content(obj, element, (Sub,))
      return element


class SubSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Sub):
      if self.policy.invalid_object_type.behavior == "ignore":
        return None
    else:
      element = self.backend.make_elem("sub")
      self._set_attribute(obj, element, "datatype", False)
      self._set_attribute(obj, element, "type", False)
      self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
      return element
