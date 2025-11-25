from collections.abc import Iterable
from datetime import datetime
from itertools import chain
from typing import Callable, Final, Generic
from python_tmx.base.types import (
  Assoc,
  BaseElement,
  BaseInlineElement,
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
from python_tmx.xml import XmlElement
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.serialization.base import BaseElementSerializer
from python_tmx.xml.serialization.logger import SerializationLogger
from python_tmx.xml.serialization.policy import SerializationPolicy
from python_tmx.xml.utils import normalize_tag

__all__ = [
  "HeaderSerializer",
  "NoteSerializer",
  "PropSerializer",
  "TmxSerializer",
  "TuSerializer",
  "TuvSerializer",
  "BptSerializer",
  "EptSerializer",
  "ItSerializer",
  "PhSerializer",
  "SubSerializer",
  "HiSerializer",
  "InlineComposer",
]

XML_NS = "{http://www.w3.org/XML/1998/namespace}"


class NoteSerializer(BaseElementSerializer[XmlElement]):
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


class PropSerializer(BaseElementSerializer[XmlElement]):
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


class HeaderSerializer(BaseElementSerializer[XmlElement]):
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
        self.backend.append(elem, child_elem)
    return elem


class BptSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, Bpt):
      self.logger.log_invalid_element(repr(Bpt), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Bpt, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("bpt")
    self._set_attribute(elem, "i", element.i, int, False)
    self._set_attribute(elem, "x", element.x, int, True)
    self._set_attribute(elem, "type", element.type, str, True)
    return elem


class EptSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, Ept):
      self.logger.log_invalid_element(repr(Ept), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Ept, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("ept")
    self._set_attribute(elem, "i", element.i, int, False)
    return elem


class ItSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, It):
      self.logger.log_invalid_element(repr(It), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected It, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("it")
    self._set_attribute(elem, "pos", element.pos, Pos, False)
    self._set_attribute(elem, "x", element.x, int, True)
    self._set_attribute(elem, "type", element.type, str, True)
    return elem


class PhSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, Ph):
      self.logger.log_invalid_element(repr(Ph), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Ph, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("ph")
    self._set_attribute(elem, "x", element.x, int, True)
    self._set_attribute(elem, "assoc", element.assoc, Assoc, True)
    self._set_attribute(elem, "type", element.type, str, True)
    return elem


class SubSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, Sub):
      self.logger.log_invalid_element(repr(Sub), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Sub, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("sub")
    self._set_attribute(elem, "datatype", element.datatype, str, True)
    self._set_attribute(elem, "type", element.type, str, True)
    return elem


class HiSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, element: BaseElement) -> XmlElement | None:
    if not isinstance(element, Hi):
      self.logger.log_invalid_element(repr(Hi), repr(type(element)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Hi, got {type(element).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", element)
    elem = self.backend.make_elem("hi")
    self._set_attribute(elem, "x", element.x, int, True)
    self._set_attribute(elem, "type", element.type, str, True)
    return elem


class InlineComposer(Generic[XmlElement]):
  __slots__ = ("backend", "policy", "logger", "emit")
  ALLOWED: Final[dict[str, tuple[type, ...]]] = {
    "seg": (Bpt, Ept, Ph, It, Hi),
    "bpt": (Sub,),
    "ept": (Sub,),
    "it": (Sub,),
    "ph": (Sub,),
    "sub": (Bpt, Ept, Ph, It, Hi),
    "hi": (Bpt, Ept, Ph, It, Hi),
  }

  def __init__(
    self,
    backend: XMLBackend[XmlElement],
    policy: SerializationPolicy,
    logger: SerializationLogger,
    emit: Callable[[BaseInlineElement], XmlElement | None],
  ) -> None:
    self.backend: XMLBackend[XmlElement] = backend
    self.policy = policy
    self.logger = logger
    self.emit: Callable[[BaseInlineElement], XmlElement | None] = emit

  def compose_into(self, parent: XmlElement, runs: Iterable[BaseInlineElement | str]) -> None:
    tag = normalize_tag(getattr(parent, "tag", ""))
    allowed = InlineComposer.ALLOWED.get(tag)
    if allowed is None:
      self.logger.log_invalid_element(", ".join(InlineComposer.ALLOWED.keys()), "unknown")
      if self.policy.incorrect_child_element == "raise":
        raise TypeError(f"Unknown inline parent <{tag}> in composer")
      return

    for item in runs:
      if isinstance(item, str):
        self._add_text(parent, item)
        continue
      if isinstance(item, (Bpt, Ept, Ph, It, Hi, Sub)):
        if not isinstance(item, allowed):
          self.logger.log_invalid_child_element(repr(allowed), repr(type(item)))
          if self.policy.incorrect_child_element == "raise":
            raise TypeError(f"Incorrect content element: expected {allowed}, got {type(item).__name__!r}")
          continue
        child = self.emit(item)  # type: ignore[arg-type]
        if child is not None:
          self.backend.append(parent, child)
          self.compose_into(child, item.content)  # type: ignore[union-attr]
        continue
      self.logger.log_invalid_child_element(repr(BaseInlineElement), repr(type(item)))
      if self.policy.incorrect_child_element == "raise":
        raise TypeError(f"Incorrect content element: expected {BaseInlineElement}, got {type(item).__name__!r}")

  def _add_text(self, parent: XmlElement, text: str) -> None:
    if not isinstance(text, str):
      self.logger.log_invalid_attribute_type("text", "str", text)
      match self.policy.invalid_text_content:
        case "raise":
          raise TypeError(f"text must be str, got {type(text).__name__!r}")
        case "coerce":
          text = str(text)
        case "empty":
          text = ""
        case "ignore" | "warn":
          return
        case _:
          raise AssertionError("unreachable: unexpected invalid_text_content policy")

    if len(parent) == 0:
      parent.text = (parent.text or "") + text
    else:
      last = parent[-1]
      last.tail = (last.tail or "") + text


class TuvSerializer(BaseElementSerializer[XmlElement]):
  def __init__(
    self,
    composer: InlineComposer[XmlElement],
    backend: XMLBackend[XmlElement],
    policy: SerializationPolicy,
    logger: SerializationLogger,
  ):
    self.composer: InlineComposer[XmlElement] = composer
    super().__init__(backend, policy, logger)  # type: ignore[arg-type]

  def serialize(self, tuv: BaseElement) -> XmlElement | None:
    if not isinstance(tuv, Tuv):
      self.logger.log_invalid_element(repr(Tuv), repr(type(tuv)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Tuv, got {type(tuv).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", tuv)
    elem = self.backend.make_elem("tuv")
    self._set_attribute(elem, f"{XML_NS}lang", tuv.lang, str, False)
    self._set_attribute(elem, "o-encoding", tuv.o_encoding, str, True)
    self._set_attribute(elem, "datatype", tuv.datatype, str, True)
    self._set_attribute(elem, "usagecount", tuv.usagecount, int, True)
    self._set_attribute(elem, "lastusagedate", tuv.lastusagedate, datetime, True)
    self._set_attribute(elem, "creationtool", tuv.creationtool, str, True)
    self._set_attribute(elem, "creationtoolversion", tuv.creationtoolversion, str, True)
    self._set_attribute(elem, "creationdate", tuv.creationdate, datetime, True)
    self._set_attribute(elem, "creationid", tuv.creationid, str, True)
    self._set_attribute(elem, "changedate", tuv.changedate, datetime, True)
    self._set_attribute(elem, "changeid", tuv.changeid, str, True)
    self._set_attribute(elem, "o-tmf", tuv.o_tmf, str, True)
    seg = self.backend.make_elem("seg")
    self.composer.compose_into(seg, tuv.content)
    self.backend.append(elem, seg)
    for child in chain[Note | Prop](tuv.notes, tuv.props):
      child_elem = self.emit(child)
      if child_elem is not None:
        self.backend.append(elem, child_elem)
    return elem


class TuSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, obj: BaseElement):
    if not isinstance(obj, Tu):
      self.logger.log_invalid_element(repr(Tu), repr(type(obj)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Tu, got {type(obj).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", obj)
    elem = self.backend.make_elem("tu")
    self._set_attribute(elem, "tuid", obj.tuid, str, True)
    self._set_attribute(elem, "o-encoding", obj.o_encoding, str, True)
    self._set_attribute(elem, "datatype", obj.datatype, str, True)
    self._set_attribute(elem, "usagecount", obj.usagecount, int, True)
    self._set_attribute(elem, "lastusagedate", obj.lastusagedate, datetime, True)
    self._set_attribute(elem, "creationtool", obj.creationtool, str, True)
    self._set_attribute(elem, "creationtoolversion", obj.creationtoolversion, str, True)
    self._set_attribute(elem, "creationdate", obj.creationdate, datetime, True)
    self._set_attribute(elem, "creationid", obj.creationid, str, True)
    self._set_attribute(elem, "changedate", obj.changedate, datetime, True)
    self._set_attribute(elem, "segtype", obj.segtype, Segtype, True)
    self._set_attribute(elem, "changeid", obj.changeid, str, True)
    self._set_attribute(elem, "o-tmf", obj.o_tmf, str, True)
    self._set_attribute(elem, "srclang", obj.srclang, str, True)
    for child in chain[Tuv | Prop | Note](obj.variants, obj.props, obj.notes):
      child_elem = self.emit(child)
      if child_elem is not None:
        self.backend.append(elem, child_elem)
    return elem


class TmxSerializer(BaseElementSerializer[XmlElement]):
  def serialize(self, obj: BaseElement) -> XmlElement | None:
    if not isinstance(obj, Tmx):
      self.logger.log_invalid_element(repr(Tmx), repr(type(obj)))
      if self.policy.invalid_element == "raise":
        raise TypeError(f"Expected Tmx, got {type(obj).__name__!r}")
      return None
    self.logger.debug_action("Serializing %s", obj)
    elem = self.backend.make_elem("tmx")
    self._set_attribute(elem, "version", obj.version, str, True)
    header = self.emit(obj.header)
    if header is not None:
      self.backend.append(elem, header)
    body = self.backend.make_elem("body")
    for child in chain[Tu](obj.body):
      child_elem = self.emit(child)
      if child_elem is not None:
        self.backend.append(body, child_elem)
    self.backend.append(elem, body)
    return elem
