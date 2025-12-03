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
  """
  Deserializer for the `<note>` element.

  Structure:
      <note xml:lang="..." o-encoding="...">Content</note>

  Policies Enforced:
      - `empty_content`: Checks if the note has text. Default behavior is `raise`.
      - `invalid_child_element`: Checks if the note contains nested tags (it should be text-only).
  """

  def _deserialize(self, element: T_XmlElement) -> Note:
    """
    Parses a <note> element.

    Args:
        element (T_XmlElement): The element to parse.
    """
    self._check_tag(element, "note")
    lang = self._parse_attribute(element, f"{XML_NS}lang", False)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    text = self.backend.get_text(element)

    if text is None:
      self.logger.log(
        self.policy.empty_content.log_level, "Element <note> does not have any text content"
      )
      if self.policy.empty_content.behavior == "raise":
        raise XmlDeserializationError("Element <note> does not have any text content")
      if self.policy.empty_content.behavior == "empty":
        self.logger.log(self.policy.empty_content.log_level, "Falling back to an empty string")
        text = ""

    for child in self.backend.iter_children(element):
      self.logger.log(
        self.policy.invalid_child_element.log_level,
        "Invalid child element <%s> in <note>",
        self.backend.get_tag(child),
      )
      if self.policy.invalid_child_element.behavior == "raise":
        raise XmlDeserializationError(
          f"Invalid child element <{self.backend.get_tag(child)}> in <note>"
        )
    return Note(text=text, lang=lang, o_encoding=o_encoding)  # type: ignore[arg-type]


class PropDeserializer(BaseElementDeserializer[T_XmlElement]):
  """
  Deserializer for the `<prop>` element.

  Structure:
      <prop type="..." xml:lang="..." o-encoding="...">Value</prop>

  Policies Enforced:
      - `required_attribute_missing`: Checks for 'type'.
      - `empty_content`: Checks if the property has a value.
      - `invalid_child_element`: Ensures no nested tags.
  """

  def _deserialize(self, element: T_XmlElement) -> Prop:
    self._check_tag(element, "prop")
    _type = self._parse_attribute(element, "type", True)
    lang = self._parse_attribute(element, f"{XML_NS}lang", False)
    o_encoding = self._parse_attribute(element, "o-encoding", False)
    text = self.backend.get_text(element)

    if text is None:
      self.logger.log(
        self.policy.empty_content.log_level, "Element <prop> does not have any text content"
      )
      if self.policy.empty_content.behavior == "raise":
        raise XmlDeserializationError("Element <prop> does not have any text content")
      if self.policy.empty_content.behavior == "empty":
        self.logger.log(self.policy.empty_content.log_level, "Falling back to an empty string")
        text = ""

    for child in self.backend.iter_children(element):
      self.logger.log(
        self.policy.invalid_child_element.log_level,
        "Invalid child element <%s> in <prop>",
        self.backend.get_tag(child),
      )
      if self.policy.invalid_child_element.behavior == "raise":
        raise XmlDeserializationError(
          f"Invalid child element <{self.backend.get_tag(child)}> in <prop>"
        )
    return Prop(text=text, type=_type, lang=lang, o_encoding=o_encoding)  # type: ignore[arg-type]


class HeaderDeserializer(BaseElementDeserializer[T_XmlElement]):
  """
  Deserializer for the `<header>` element.

  Structure:
      <header creationtool="..." ...>
          <prop>...</prop>
          <note>...</note>
      </header>

  Policies Enforced:
      - `extra_text`: Detects non-whitespace text inside the header (which should only contain tags).
      - `invalid_child_element`: Detects tags other than <prop> or <note>.
  """

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
      tag = self.backend.get_tag(child)
      if tag == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif tag == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <header>",
          tag,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(f"Invalid child element <{tag}> in <header>")

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
  """
  Deserializer for the `<bpt>` (Begin Paired Tag) element.

  Uses `InlineContentDeserializerMixin` to process its `<sub>` children.
  """

  def _deserialize(self, element: T_XmlElement) -> Bpt:
    self._check_tag(element, "bpt")
    i = self._parse_attribute_as_int(element, "i", True)
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element, ("sub",))
    return Bpt(i=i, x=x, type=type, content=content)  # type: ignore[arg-type]


class EptDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<ept>` (End Paired Tag) element.
  """

  def _deserialize(self, element: T_XmlElement) -> Ept:
    self._check_tag(element, "ept")
    i = self._parse_attribute_as_int(element, "i", True)
    content = self.deserialize_content(element, ("sub",))
    return Ept(i=i, content=content)  # type: ignore[arg-type]


class ItDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<it>` (Isolated Tag) element.
  """

  def _deserialize(self, element: T_XmlElement) -> It:
    self._check_tag(element, "it")
    pos = self._parse_attribute_as_enum(element, "pos", Pos, True)
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element, ("sub",))
    return It(pos=pos, x=x, type=type, content=content)  # type: ignore[arg-type]


class PhDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<ph>` (Placeholder) element.
  """

  def _deserialize(self, element: T_XmlElement) -> Ph:
    self._check_tag(element, "ph")
    x = self._parse_attribute_as_int(element, "x", False)
    assoc = self._parse_attribute_as_enum(element, "assoc", Assoc, False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element, ("sub",))
    return Ph(x=x, assoc=assoc, type=type, content=content)  # type: ignore[arg-type]


class SubDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<sub>` (Sub-flow) element.

  Contains recursive inline markup.
  """

  def _deserialize(self, element: T_XmlElement) -> Sub:
    self._check_tag(element, "sub")
    datatype = self._parse_attribute(element, "datatype", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element, ("bpt", "ept", "ph", "it", "hi"))
    return Sub(datatype=datatype, type=type, content=content)  # type: ignore[arg-type]


class HiDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<hi>` (Highlight) element.
  """

  def _deserialize(self, element: T_XmlElement) -> Hi:
    self._check_tag(element, "hi")
    x = self._parse_attribute_as_int(element, "x", False)
    type = self._parse_attribute(element, "type", False)
    content = self.deserialize_content(element, ("bpt", "ept", "ph", "it", "hi"))
    return Hi(x=x, type=type, content=content)  # type: ignore[arg-type]


class TuvDeserializer(
  BaseElementDeserializer[T_XmlElement], InlineContentDeserializerMixin[T_XmlElement]
):
  """
  Deserializer for the `<tuv>` (Translation Unit Variant) element.

  Structure:
      <tuv xml:lang="...">
          <prop>...</prop>
          <seg>Mixed Content</seg>
          <note>...</note>
      </tuv>

  This handler bridges the structural world (Props/Notes) and the inline world (<seg>).

  Policies Enforced:
      - `missing_seg`: Controls behavior if no <seg> child is found.
      - `multiple_seg`: Controls behavior if multiple <seg> children are found.
      - `extra_text`: Ensures no text exists directly in <tuv> (text must be in <seg>).
  """

  def _deserialize(self, element: T_XmlElement) -> Tuv:
    self._check_tag(element, "tuv")

    if (text := self.backend.get_text(element)) is not None:
      if text.strip():
        self.logger.log(
          self.policy.extra_text.log_level, "Element <tuv> has extra text content '%s'", text
        )
        if self.policy.extra_text.behavior == "raise":
          raise XmlDeserializationError(f"Element <tuv> has extra text content '{text}'")

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
      tag = self.backend.get_tag(child)
      if tag == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif tag == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      elif tag == "seg":
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
        content = self.deserialize_content(child, ("bpt", "ept", "ph", "it", "hi"))
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tuv>",
          tag,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(f"Invalid child element <{tag}> in <tuv>")

    if not seg_found:
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
  """
  Deserializer for the `<tu>` (Translation Unit) element.

  Container for `<tuv>`, `<prop>`, and `<note>` elements.
  """

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
      tag = self.backend.get_tag(child)
      if tag == "prop":
        prop = self.emit(child)
        if isinstance(prop, Prop):
          props.append(prop)
      elif tag == "note":
        note = self.emit(child)
        if isinstance(note, Note):
          notes.append(note)
      elif tag == "tuv":
        tuv = self.emit(child)
        if isinstance(tuv, Tuv):
          variants.append(tuv)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tu>",
          tag,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(f"Invalid child element <{tag}> in <tu>")

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
  """
  Deserializer for the root `<tmx>` element.

  Structure:
      <tmx version="...">
          <header>...</header>
          <body>
              <tu>...</tu>
              ...
          </body>
      </tmx>

  Policies Enforced:
      - `missing_header`: Valid TMX must have a header.
      - `multiple_headers`: Valid TMX must have exactly one header.
  """

  def _deserialize(self, element: T_XmlElement) -> Tmx:
    self._check_tag(element, "tmx")
    version = self._parse_attribute(element, "version", True)
    header_found: bool = False
    header: Header | None = None
    body: list[Tu] = []

    if (text := self.backend.get_text(element)) is not None:
      if text.strip():
        self.logger.log(
          self.policy.extra_text.log_level, "Element <tmx> has extra text content '%s'", text
        )
        if self.policy.extra_text.behavior == "raise":
          raise XmlDeserializationError(f"Element <tmx> has extra text content '{text}'")

    for child in self.backend.iter_children(element):
      tag = self.backend.get_tag(child)
      if tag == "header":
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
      elif tag == "body":
        for grandchild in self.backend.iter_children(child):
          if self.backend.get_tag(grandchild) == "tu":
            tu_obj = self.emit(grandchild)
            if isinstance(tu_obj, Tu):
              body.append(tu_obj)
      else:
        self.logger.log(
          self.policy.invalid_child_element.log_level,
          "Invalid child element <%s> in <tmx>",
          tag,
        )
        if self.policy.invalid_child_element.behavior == "raise":
          raise XmlDeserializationError(f"Invalid child element <{tag}> in <tmx>")

    if not header_found:
      self.logger.log(
        self.policy.missing_header.log_level, "Element <tmx> is missing a <header> child element"
      )
      if self.policy.missing_header.behavior == "raise":
        raise XmlDeserializationError("Element <tmx> is missing a <header> child element")

    return Tmx(
      version=version,  # type: ignore[arg-type]
      header=header,  # type: ignore[arg-type]
      body=body,
    )
