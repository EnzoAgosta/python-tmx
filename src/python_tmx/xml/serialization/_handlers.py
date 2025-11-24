from datetime import datetime
from itertools import chain
from python_tmx.base.types import BaseElement, Header, Note, Prop, Segtype
from python_tmx.xml import XmlElement
from python_tmx.xml.serialization.base import BaseSerializer

__all__ = ["HeaderSerializer", "NoteSerializer", "PropSerializer"]

XML_NS = "{http://www.w3.org/XML/1998/namespace}"


class NoteSerializer(BaseSerializer[XmlElement]):
  def serialize(self, note: BaseElement) -> XmlElement | None:
    if not isinstance(note, Note):
      self.logger.log_invalid_element(repr(Note), repr(type(note)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Note, got {type(note).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", note)
    elem = self.backend.make_elem("note")
    self._set_text(elem, note.text)
    self._set_attribute(elem, f"{XML_NS}lang", note.lang, str, False)
    self._set_attribute(elem, "o-encoding", note.o_encoding, str, True)
    return elem


class PropSerializer(BaseSerializer[XmlElement]):
  def serialize(self, prop: BaseElement) -> XmlElement | None:
    if not isinstance(prop, Prop):
      self.logger.log_invalid_element(repr(Prop), repr(type(prop)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Prop, got {type(prop).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", prop)
    elem = self.backend.make_elem("prop")
    self._set_text(elem, prop.text)
    self._set_attribute(elem, "type", prop.type, str, False)
    self._set_attribute(elem, f"{XML_NS}lang", prop.lang, str, False)
    self._set_attribute(elem, "o-encoding", prop.o_encoding, str, True)
    return elem


class HeaderSerializer(BaseSerializer[XmlElement]):
  def serialize(self, header: BaseElement) -> XmlElement | None:
    if not isinstance(header, Header):
      self.logger.log_invalid_element(repr(Header), repr(type(header)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Header, got {type(header).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", header)
    elem = self.backend.make_elem("header")
    self._set_attribute(elem, "creationtool", header.creationtool, str, False)
    self._set_attribute(elem, "creationtoolversion", header.creationtoolversion, str, False)
    self._set_attribute(elem, "segtype", header.segtype, Segtype, False)
    self._set_attribute(elem, "o-tmf", header.o_tmf, str, False)
    self._set_attribute(elem, "adminlang", header.adminlang, str, False)
    self._set_attribute(elem, "srclang", header.srclang, str, False)
    self._set_attribute(elem, "datatype", header.datatype, str, False)
    self._set_attribute(elem, "o-encoding", header.o_encoding, str, True)
    self._set_attribute(elem, "creationdate", header.creationdate, datetime, True)
    self._set_attribute(elem, "creationid", header.creationid, str, True)
    self._set_attribute(elem, "changedate", header.changedate, datetime, True)
    self._set_attribute(elem, "changeid", header.changeid, str, True)
    for child in chain[Note | Prop](header.notes, header.props):
      child_elem = self.emit(child)
      if child_elem is not None:
        elem.append(child_elem)
    return elem
