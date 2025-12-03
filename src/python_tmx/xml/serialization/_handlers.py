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
  """
  Serializer for the `<prop>` element.

  Type Checks:
      - Ensures input is `Prop`. Returns None (if ignored) or raises error otherwise.
  """

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
  """
  Serializer for the `<note>` element.
  """

  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Note):
      return None
    element = self.backend.make_elem("note")
    self._set_attribute(element, obj.lang, f"{XML_NS}lang", False)
    self._set_attribute(element, obj.o_encoding, "o-encoding", False)
    self.backend.set_text(element, obj.text)
    return element


class HeaderSerializer(BaseElementSerializer[T_XmlElement]):
  """
  Serializer for the `<header>` element.

  Serializes simple attributes and recursively processes `props` and `notes` lists.

  Policies Enforced:
      - `invalid_child_element`: Checks that `obj.notes` and `obj.props` contain
        valid `Note` and `Prop` objects respectively.
  """

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
    for note in obj.notes:
      if isinstance(note, Note):
        child_element = self.emit(note)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Header.notes",
          type(note).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(
            f"Invalid child element {type(note).__name__!r} in Header.notes"
          )
    for prop in obj.props:
      if isinstance(prop, Prop):
        child_element = self.emit(prop)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Header.props",
          type(prop).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(
            f"Invalid child element {type(prop).__name__!r} in Header.props"
          )
    return element


class TuvSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  """
  Serializer for the `<tuv>` element.

  Constructs the structural `<tuv>` container and delegates the creation of the
  inner `<seg>` element to the `InlineContentSerializerMixin`.
  """

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
    for note in obj.notes:
      if isinstance(note, Note):
        child_element = self.emit(note)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tuv.notes",
          type(note).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(f"Invalid child element {type(note).__name__!r} in Tuv.notes")
    for prop in obj.props:
      if isinstance(prop, Prop):
        child_element = self.emit(prop)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tuv.props",
          type(prop).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(f"Invalid child element {type(prop).__name__!r} in Tuv.props")
    seg_element = self.backend.make_elem("seg")
    self.serialize_content(obj, seg_element, (Bpt, Ept, Ph, It, Hi))
    self.backend.append(element, seg_element)
    return element


class TuSerializer(BaseElementSerializer[T_XmlElement]):
  """
  Serializer for the `<tu>` element.

  Iterates over `variants` (Tuv), `props`, and `notes`.
  """

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
    for note in obj.notes:
      if isinstance(note, Note):
        child_element = self.emit(note)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tu.notes",
          type(note).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(f"Invalid child element {type(note).__name__!r} in Tu.notes")
    for prop in obj.props:
      if isinstance(prop, Prop):
        child_element = self.emit(prop)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tu.props",
          type(prop).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(f"Invalid child element {type(prop).__name__!r} in Tu.props")
    for tuv in obj.variants:
      if isinstance(tuv, Tuv):
        child_element = self.emit(tuv)
        if child_element is not None:
          self.backend.append(element, child_element)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tu.variants",
          type(tuv).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(
            f"Invalid child element {type(tuv).__name__!r} in Tu.variants"
          )
    return element


class TmxSerializer(BaseElementSerializer[T_XmlElement]):
  """
  Serializer for the root `<tmx>` element.

  Constructs the Header and the Body (containing TUs).
  """

  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Tmx):
      return None
    element = self.backend.make_elem("tmx")
    self._set_attribute(element, obj.version, "version", True)
    if not isinstance(obj.header, Header):
      self.logger.log(
        self.policy.invalid_child_element.log_level,
        "Tmx.header is not a Header object. Expected %s, got %r",
        "Header",
        type(obj.header).__name__,
      )
      if self.policy.invalid_child_element.behavior == "raise":
        raise XmlSerializationError(
          f"Tmx.header is not a Header object. Expected Header, got {type(obj.header).__name__!r}"
        )
    header_element = self.emit(obj.header)
    if header_element is not None:
      self.backend.append(element, header_element)
    body = self.backend.make_elem("body")
    for child in obj.body:
      if not isinstance(child, Tu):
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element %r in Tmx.body",
          type(child).__name__,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlSerializationError(f"Invalid child element {type(child).__name__!r} in Tmx.body")
      child_element = self.emit(child)
      if child_element is not None:
        self.backend.append(body, child_element)
    self.backend.append(element, body)
    return element


class BptSerializer(
  BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]
):
  """Serializer for `<bpt>` (Begin Paired Tag)."""

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
  """Serializer for `<ept>` (End Paired Tag)."""

  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Ept):
      return None
    element = self.backend.make_elem("ept")
    self._set_int_attribute(element, obj.i, "i", True)
    self.serialize_content(obj, element, (Sub,))
    return element


class HiSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  """Serializer for `<hi>` (Highlight)."""

  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Hi):
      return None
    element = self.backend.make_elem("hi")
    self._set_int_attribute(element, obj.x, "x", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
    return element


class ItSerializer(BaseElementSerializer[T_XmlElement], InlineContentSerializerMixin[T_XmlElement]):
  """Serializer for `<it>` (Isolated Tag)."""

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
  """Serializer for `<ph>` (Placeholder)."""

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
  """Serializer for `<sub>` (Sub-flow)."""

  def _serialize(self, obj: BaseElement) -> T_XmlElement | None:
    if not self._check_obj_type(obj, Sub):
      return None
    element = self.backend.make_elem("sub")
    self._set_attribute(element, obj.datatype, "datatype", False)
    self._set_attribute(element, obj.type, "type", False)
    self.serialize_content(obj, element, (Bpt, Ept, Ph, It, Hi))
    return element
