from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import (
  Assoc,
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
from python_tmx.xml import XML_NS, T_XmlElement
from python_tmx.xml.deserialization.base import (
  BaseElementDeserializer,
  InlineContentDeserializerMixin,
)


__all__ = [
  "NoteDeserializer",
  "PropDeserializer",
  "HeaderDeserializer",
  "BptDeserializer",
  "EptDeserializer",
  "ItDeserializer",
  "PhDeserializer",
  "SubDeserializer",
  "HiDeserializer",
  "TuvDeserializer",
  "TuDeserializer",
  "TmxDeserializer",
]


class NoteDeserializer(BaseElementDeserializer[T_XmlElement]):
  def _deserialize(self, element: T_XmlElement) -> Note:
    self._check_tag(element, "note")
    lang = self._parse_attribute(element, f"{XML_NS}lang", False)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    text = self.backend.get_text(element)
    if text is None:
      self.logger.log(
        self.policy.missing_text.log_level, "Element <note> does not have any text content"
      )
      if self.policy.missing_text.behavior == "raise":
        raise XmlDeserializationError("Element <note> does not have any text content")
      if self.policy.missing_text.behavior == "empty":
        self.logger.log(self.policy.missing_text.log_level, "Falling back to an empty string")
        text = ""
    return Note(text=text, lang=lang, o_encoding=o_encoding)  # type: ignore[arg-type]


class PropDeserializer(BaseElementDeserializer[T_XmlElement]):
  def _deserialize(self, element: T_XmlElement) -> Prop:
    self._check_tag(element, "prop")
    _type = self._parse_attribute(element, "type", True)
    lang = self._parse_attribute(element, f"{XML_NS}lang", False)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    text = self.backend.get_text(element)
    if text is None:
      self.logger.log(
        self.policy.missing_text.log_level, "Element <prop> does not have any text content"
      )
      if self.policy.missing_text.behavior == "raise":
        raise XmlDeserializationError("Element <prop> does not have any text content")
      if self.policy.missing_text.behavior == "empty":
        self.logger.log(self.policy.missing_text.log_level, "Falling back to an empty string")
        text = ""
    return Prop(text=text, type=_type, lang=lang, o_encoding=o_encoding)  # type: ignore[arg-type]


class HeaderDeserializer(BaseElementDeserializer[T_XmlElement]):
  def _deserialize(self, element: T_XmlElement) -> Header:
    self._check_tag(element, "header")
    if (text := self.backend.get_text(element)) is not None:
      if text.strip():
        self.logger.log(
          self.policy.extra_text.log_level, "Element <header> has extra text content '%s'", text
        )
        if self.policy.extra_text.behavior == "raise":
          raise XmlDeserializationError(f"Element <header> has extra text content '{text}'")
    creationtool = self._parse_attribute(element, "creationtool", True)
    creationtoolversion = self._parse_attribute(element, "creationtoolversion", True)
    segtype = self._parse_attribute_as_enum(element, "segtype", Segtype, True)
    o_tmf = self._parse_attribute(element, "o-tmf", True)
    adminlang = self._parse_attribute(element, "adminlang", True)
    srclang = self._parse_attribute(element, "srclang", True)
    datatype = self._parse_attribute(element, "datatype", True)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    creationdate = self._parse_attribute_as_dt(element, "creationdate", False)
    creationid = self._parse_attribute(element, "creationid", False)
    changedate = self._parse_attribute_as_dt(element, "changedate", False)
    changeid = self._parse_attribute(element, "changeid", False)
    notes: list[Note] = []
    props: list[Prop] = []
    for child in self.backend.iter_children(element):
      if self.backend.get_tag(child) == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif self.backend.get_tag(child) == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <header>",
          self.backend.get_tag(child),
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(
            f"Invalid child element <{self.backend.get_tag(child)}> in <header>"
          )
    return Header(
      creationtool=creationtool,  # type: ignore[arg-type]
      creationtoolversion=creationtoolversion,  # type: ignore[arg-type]
      segtype=segtype,  # type: ignore[arg-type]
      o_tmf=o_tmf,  # type: ignore[arg-type]
      adminlang=adminlang,  # type: ignore[arg-type]
      srclang=srclang,  # type: ignore[arg-type]
      datatype=datatype,  # type: ignore[arg-type]
      o_encoding=o_encoding,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      changeid=changeid,
      props=props,
      notes=notes,
    )


class BptDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Bpt:
    self._check_tag(element, "bpt")
    i = self._parse_attribute_as_int(element, "i", True)
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = [x for x in self.deserialize_content(element) if isinstance(x, (str, Sub))]
    return Bpt(i=i, x=x, type=type, content=content)  # type: ignore[arg-type]


class EptDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Ept:
    self._check_tag(element, "ept")
    i = self._parse_attribute_as_int(element, "i", True)
    content = self.deserialize_content(element)
    return Ept(i=i, content=content)  # type: ignore[arg-type]


class ItDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> It:
    self._check_tag(element, "it")
    pos = self._parse_attribute_as_enum(element, "pos", Pos, True)
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element)
    return It(pos=pos, x=x, type=type, content=content)  # type: ignore[arg-type]


class PhDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Ph:
    self._check_tag(element, "ph")
    x = self._parse_attribute_as_int(element, "x", False)
    assoc = self._parse_attribute_as_enum(element, "assoc", Assoc, False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element)
    return Ph(x=x, assoc=assoc, type=type, content=content)  # type: ignore[arg-type]


class SubDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Sub:
    self._check_tag(element, "sub")
    datatype = self._parse_attribute(element, "datatype", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element)
    return Sub(datatype=datatype, type=type, content=content)  # type: ignore[arg-type]


class HiDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Hi:
    self._check_tag(element, "hi")
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element)
    return Hi(x=x, type=type, content=content)  # type: ignore[arg-type]


class TuvDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  def _deserialize(self, element: T_XmlElement) -> Tuv:
    self._check_tag(element, "tuv")
    if (text := self.backend.get_text(element)) is not None:
      if text.strip():
        self.logger.log(
          self.policy.extra_text.log_level, "Element <tuv> has extra text content '%s'", text
        )
        if self.policy.extra_text.behavior == "raise":
          raise XmlDeserializationError("Element <tuv> has extra text content")
    lang = self._parse_attribute(element, f"{XML_NS}lang", True)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    datatype = self._parse_attribute(element, "datatype", False)
    usagecount = self._parse_attribute_as_int(element, "usagecount", False)
    lastusagedate = self._parse_attribute_as_dt(element, "lastusagedate", False)
    creationtool = self._parse_attribute(element, "creationtool", False)
    creationtoolversion = self._parse_attribute(element, "creationtoolversion", False)
    creationdate = self._parse_attribute_as_dt(element, "creationdate", False)
    creationid = self._parse_attribute(element, "creationid", False)
    changedate = self._parse_attribute_as_dt(element, "changedate", False)
    changeid = self._parse_attribute(element, "changeid", False)
    o_tmf = self._parse_attribute(element, "o-tmf", False)
    props: list[Prop] = []
    notes: list[Note] = []
    content: list[str | BaseInlineElement] | None = None
    seg_found = False
    for child in self.backend.iter_children(element):
      if self.backend.get_tag(child) == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif self.backend.get_tag(child) == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      elif self.backend.get_tag(child) == "seg":
        if seg_found:
          self.logger.log(
            self.policy.multiple_seg.log_level,
            "Multiple <seg> elements in <tuv>",
          )
          if self.policy.multiple_seg.behavior == "raise":
            raise XmlDeserializationError("Multiple <seg> elements in <tuv>")
          if self.policy.multiple_seg.behavior == "keep_first":
            continue
        seg_found = True
        content = self.deserialize_content(child)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tuv>",
          self.backend.get_tag(child),
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(
            f"Invalid child element <{self.backend.get_tag(child)}> in <tuv>"
          )
    if seg_found:
      if content == []:
        self.logger.log(
          self.policy.empty_seg.log_level, "Element <tuv> has an empty <seg> child element"
        )
        if self.policy.empty_seg.behavior == "raise":
          raise XmlDeserializationError("Element <tuv> has an empty <seg> child element")
    else:
      self.logger.log(
        self.policy.missing_seg.log_level, "Element <tuv> is missing a <seg> child element"
      )
      if self.policy.missing_seg.behavior == "raise":
        raise XmlDeserializationError("Element <tuv> is missing a <seg> child element")
      if self.policy.missing_seg.behavior == "ignore":
        content = []
    return Tuv(
      lang=lang,  # type: ignore[arg-type]
      o_encoding=o_encoding,
      datatype=datatype,
      usagecount=usagecount,
      lastusagedate=lastusagedate,
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      changeid=changeid,
      o_tmf=o_tmf,
      props=props,
      notes=notes,
      content=content,  # type: ignore[arg-type]
    )


class TuDeserializer(BaseElementDeserializer[T_XmlElement]):
  def _deserialize(self, element: T_XmlElement) -> Tu:
    self._check_tag(element, "tu")
    if (text := self.backend.get_text(element)) is not None:
      if text.strip():
        self.logger.log(
          self.policy.extra_text.log_level, "Element <tu> has extra text content '%s'", text
        )
        if self.policy.extra_text.behavior == "raise":
          raise XmlDeserializationError(f"Element <tu> has extra text content '{text}'")
    tuid = self._parse_attribute(element, "tuid", False)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    datatype = self._parse_attribute(element, "datatype", False)
    usagecount = self._parse_attribute_as_int(element, "usagecount", False)
    lastusagedate = self._parse_attribute_as_dt(element, "lastusagedate", False)
    creationtool = self._parse_attribute(element, "creationtool", False)
    creationtoolversion = self._parse_attribute(element, "creationtoolversion", False)
    creationdate = self._parse_attribute_as_dt(element, "creationdate", False)
    creationid = self._parse_attribute(element, "creationid", False)
    changedate = self._parse_attribute_as_dt(element, "changedate", False)
    segtype = self._parse_attribute_as_enum(element, "segtype", Segtype, False)
    changeid = self._parse_attribute(element, "changeid", False)
    o_tmf = self._parse_attribute(element, "o-tmf", False)
    srclang = self._parse_attribute(element, "srclang", False)
    props: list[Prop] = []
    notes: list[Note] = []
    variants: list[Tuv] = []
    for child in self.backend.iter_children(element):
      if self.backend.get_tag(child) == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif self.backend.get_tag(child) == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      elif self.backend.get_tag(child) == "tuv":
        tuv = self.emit(child)
        if isinstance(tuv, Tuv):
          variants.append(tuv)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tu>",
          self.backend.get_tag(child),
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(
            f"Invalid child element <{self.backend.get_tag(child)}> in <tu>"
          )
    return Tu(
      tuid=tuid,
      o_encoding=o_encoding,
      datatype=datatype,
      usagecount=usagecount,
      lastusagedate=lastusagedate,
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      segtype=segtype,
      changeid=changeid,
      o_tmf=o_tmf,
      srclang=srclang,
      props=props,
      notes=notes,
      variants=variants,
    )


class TmxDeserializer(BaseElementDeserializer[T_XmlElement]):
  def _deserialize(self, element: T_XmlElement) -> Tmx:
    self._check_tag(element, "tmx")
    version = self._parse_attribute(element, "version", True)
    header_found: bool = False
    header: Header | None = None
    body: list[Tu] = []
    for child in self.backend.iter_children(element):
      if self.backend.get_tag(child) == "header":
        if header_found:
          self.logger.log(
            self.policy.multiple_headers.log_level,
            "Multiple <header> elements in <tmx>",
          )
          if self.policy.multiple_headers.behavior == "raise":
            raise XmlDeserializationError("Multiple <header> elements in <tmx>")
          if self.policy.multiple_headers.behavior == "keep_first":
            continue
        header_found = True
        header_obj = self.emit(child)
        if isinstance(header_obj, Header):
          header = header_obj
      elif self.backend.get_tag(child) == "body":
        for grandchild in self.backend.iter_children(child):
          if self.backend.get_tag(grandchild) == "tu":
            tu_obj = self.emit(grandchild)
            if isinstance(tu_obj, Tu):
              body.append(tu_obj)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tmx>",
          self.backend.get_tag(child),
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(
            f"Invalid child element <{self.backend.get_tag(child)}> in <tmx>"
          )
    if not header_found:
      self.logger.log(
        self.policy.missing_header.log_level, "Element <tmx> is missing a <header> child element."
      )
      if self.policy.missing_header.behavior == "raise":  # type: ignore[unreachable]
        raise XmlDeserializationError("Element <tmx> is missing a <header> child element.")
    return Tmx(
      version=version,  # type: ignore[arg-type]
      header=header,  # type: ignore[arg-type]
      body=body,
    )
