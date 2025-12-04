from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Self

__all__ = [
  "BaseElement",
  "BaseInlineElement",
  "BaseStructuralElement",
  "Bpt",
  "Ept",
  "Hi",
  "It",
  "Ph",
  "Sub",
  "Pos",
  "Segtype",
  "Assoc",
  "Header",
  "Note",
  "Prop",
  "Tu",
  "Tuv",
  "Tmx",
]

type BaseStructuralElement = Prop | Note | Header | Tu | Tuv | Tmx
"""Union of all structural TMX elements as defined in TMX 1.4b."""

type BaseInlineElement = Bpt | Ept | It | Hi | Ph | Sub
"""Union of all inline TMX elements permitted inside segment content."""

type BaseElement = BaseInlineElement | BaseStructuralElement
"""Union of all element classes in a TMX document."""


class Pos(StrEnum):
  """Enumerates valid values of the `pos` attribute for the `<it>` element."""

  BEGIN = "begin"
  """Marks the beginning position of an isolated tag."""
  END = "end"
  """Marks the ending position of an isolated tag."""


class Assoc(StrEnum):
  """Enumerates valid values of the `assoc` attribute for `<ph>` elements."""

  P = "p"
  """Indicates the placeholder is paired with a previous tag."""
  F = "f"
  """Indicates the placeholder is paired with a following tag."""
  B = "b"
  """Indicates the placeholder stands by itself (both)."""


class Segtype(StrEnum):
  """Enumerates the allowed values of the `segtype` attribute."""

  BLOCK = "block"
  PARAGRAPH = "paragraph"
  SENTENCE = "sentence"
  PHRASE = "phrase"


@dataclass(slots=True)
class Prop:
  """Represents the `<prop>` element as defined in TMX 1.4b §3.6.1.

  The `<prop>` element provides a flexible mechanism for associating
  user-defined properties or metadata with a parent element.
  """

  text: str
  """Element content. Specifies the value of the property."""
  type: str
  """`type` attribute (required). Identifies the name or category of this property."""
  lang: str | None = None
  """`xml:lang` attribute (optional). Specifies the language of the property text."""
  o_encoding: str | None = None
  """`o-encoding` attribute (optional). Specifies the original encoding of the text value."""


@dataclass(slots=True)
class Note:
  """Represents the `<note>` element as defined in TMX 1.4b §3.6.2.

  The `<note>` element contains human-readable comments or annotations.
  """

  text: str
  """Element content. Provides the text of the annotation."""
  lang: str | None = None
  """`xml:lang` attribute (optional). Specifies the language of the note."""
  o_encoding: str | None = None
  """`o-encoding` attribute (optional). Specifies the original character encoding."""


@dataclass(slots=True)
class Header:
  """Represents the `<header>` element as defined in TMX 1.4b §3.2.

  The header element provides administrative and structural information
  for the TMX document and applies to all translation units contained
  in the file.
  """

  creationtool: str
  """`creationtool` attribute (required). Identifies the tool that created the TMX file."""
  creationtoolversion: str
  """`creationtoolversion` attribute (required). Specifies the version number of the creation tool."""
  segtype: Segtype
  """`segtype` attribute (required). Specifies the segmentation type used in the file."""
  o_tmf: str
  """`o-tmf` attribute (required). Identifies the original TMF (Translation Memory Format) type."""
  adminlang: str
  """`adminlang` attribute (required). Specifies the language used for administrative data."""
  srclang: str
  """`srclang` attribute (required). Specifies the source-language code for all TUs in the file."""
  datatype: str
  """`datatype` attribute (required). Specifies the general content type (e.g. “plaintext”, “html”)."""
  o_encoding: str | None = None
  """`o-encoding` attribute (optional). Specifies the original character encoding."""
  creationdate: datetime | None = None
  """`creationdate` attribute (optional). Indicates the date/time when the TMX file was created."""
  creationid: str | None = None
  """`creationid` attribute (optional). Identifies the individual or process that created the TMX file."""
  changedate: datetime | None = None
  """`changedate` attribute (optional). Indicates the date/time of the most recent modification."""
  changeid: str | None = None
  """`changeid` attribute (optional). Identifies the individual or process that last modified the file."""
  props: list[Prop] = field(default_factory=list)
  """Zero or more `<prop>` child elements providing additional metadata."""
  notes: list[Note] = field(default_factory=list)
  """Zero or more `<note>` child elements providing administrative comments."""


@dataclass(slots=True)
class Bpt:
  """Represents the `<bpt>` (begin paired tag) inline element (TMX 1.4b §3.7.3)."""

  i: int
  """`i` attribute (required). Identifies a paired sequence shared with a corresponding `<ept>`."""
  content: list[Sub | str] = field(default_factory=list)
  """Element content. May include text or nested `<sub>` elements."""
  x: int | None = None
  """`x` attribute (optional). Specifies an external identifier for tag mapping."""
  type: str | None = None
  """`type` attribute (optional). Describes the functional type of the inline tag."""


@dataclass(slots=True)
class Ept:
  """Represents the `<ept>` (end paired tag) inline element (TMX 1.4b §3.7.4)."""

  i: int
  """`i` attribute (required). Associates this `<ept>` with its corresponding `<bpt>`."""
  content: list[Sub | str] = field(default_factory=list)
  """Element content. May include text or nested `<sub>` elements."""


@dataclass(slots=True)
class Hi:
  """Represents the `<hi>` (highlight) inline element (TMX 1.4b §3.7.7)."""

  content: list[str | Bpt | Ept | It | Ph | Self]
  """Element content. Contains text and other inline elements; `<hi>` elements may nest."""
  x: int | None = None
  """`x` attribute (optional). User-defined numeric identifier."""
  type: str | None = None
  """`type` attribute (optional). Describes the formatting or emphasis category."""


@dataclass(slots=True)
class It:
  """Represents the `<it>` (isolated tag) inline element (TMX 1.4b §3.7.5)."""

  content: list[str | Sub]
  """Element content. Contains text or nested `<sub>` elements."""
  pos: Pos
  """`pos` attribute (required). Specifies whether the tag is a BEGIN or END isolated tag."""
  x: int | None = None
  """`x` attribute (optional). Provides an external reference number for tag alignment."""
  type: str | None = None
  """`type` attribute (optional). Describes the function of the isolated tag."""


@dataclass(slots=True)
class Ph:
  """Represents the `<ph>` (placeholder) inline element (TMX 1.4b §3.7.6)."""

  x: int | None = None
  """`x` attribute (optional). User-defined external identifier."""
  content: list[Sub | str] = field(default_factory=list)
  """Element content. Contains placeholder text or nested `<sub>` elements."""
  type: str | None = None
  """`type` attribute (optional). Describes the nature of the placeholder."""
  assoc: Assoc | None = None
  """`assoc` attribute (optional). Specifies association with preceding or following tags."""


@dataclass(slots=True)
class Sub:
  """Represents the `<sub>` (sub-segment) inline element (TMX 1.4b §3.7.8)."""

  datatype: str | None = None
  """`datatype` attribute (optional). Specifies the data type of the sub-segment."""
  content: list[Bpt | Ept | It | Ph | Hi | str] = field(default_factory=list)
  """Element content. May include text and inline elements representing sub-segments."""
  type: str | None = None
  """`type` attribute (optional). Indicates the function or classification of the sub-segment."""


@dataclass(slots=True)
class Tuv:
  """Represents the `<tuv>` (Translation Unit Variant) element."""

  lang: str
  """`xml:lang` attribute (required). Specifies the language of this translation variant."""
  o_encoding: str | None = None
  """`o-encoding` attribute (optional). Indicates the original character encoding."""
  datatype: str | None = None
  """`datatype` attribute (optional). Describes the content type of the translation variant."""
  usagecount: int | None = None
  """`usagecount` attribute (optional). Records how many times this TUV has been used."""
  lastusagedate: datetime | None = None
  """`lastusagedate` attribute (optional). Indicates when the TUV was last used."""
  creationtool: str | None = None
  """`creationtool` attribute (optional). Identifies the tool that created this variant."""
  creationtoolversion: str | None = None
  """`creationtoolversion` attribute (optional). Specifies version of the creating tool."""
  creationdate: datetime | None = None
  """`creationdate` attribute (optional). Specifies when this TUV was created."""
  creationid: str | None = None
  """`creationid` attribute (optional). Identifies who created this variant."""
  changedate: datetime | None = None
  """`changedate` attribute (optional). Specifies when this TUV was last modified."""
  changeid: str | None = None
  """`changeid` attribute (optional). Identifies who last modified this variant."""
  o_tmf: str | None = None
  """`o-tmf` attribute (optional). Identifies the original TMF type for this variant."""
  props: list[Prop] = field(default_factory=list)
  """Zero or more `<prop>` child elements providing metadata."""
  notes: list[Note] = field(default_factory=list)
  """Zero or more `<note>` child elements providing annotations."""
  content: list[str | Bpt | Ept | Hi | It | Ph] = field(default_factory=list)
  """Element content of the `<seg>` element inside `<tuv>`. Represents the translation text and inline markup."""


@dataclass(slots=True)
class Tu:
  """Represents the `<tu>` (Translation Unit) element (TMX 1.4b §3.3)."""

  tuid: str | None = None
  """`tuid` attribute (optional). Provides a unique identifier for the translation unit."""
  o_encoding: str | None = None
  """`o-encoding` attribute (optional). Specifies the original encoding of this TU."""
  datatype: str | None = None
  """`datatype` attribute (optional). Indicates the content type of the unit."""
  usagecount: int | None = None
  """`usagecount` attribute (optional). Indicates the number of times the TU has been used."""
  lastusagedate: datetime | None = None
  """`lastusagedate` attribute (optional). Records the date/time the TU was last used."""
  creationtool: str | None = None
  """`creationtool` attribute (optional). Identifies the tool that created this TU."""
  creationtoolversion: str | None = None
  """`creationtoolversion` attribute (optional). Version of the tool used to create the TU."""
  creationdate: datetime | None = None
  """`creationdate` attribute (optional). Date/time the TU was created."""
  creationid: str | None = None
  """`creationid` attribute (optional). Identifies who created the TU."""
  changedate: datetime | None = None
  """`changedate` attribute (optional). Date/time the TU was last modified."""
  segtype: Segtype | None = None
  """`segtype` attribute (optional). Specifies the segmentation type if overriding the header value."""
  changeid: str | None = None
  """`changeid` attribute (optional). Identifies who last changed the TU."""
  o_tmf: str | None = None
  """`o-tmf` attribute (optional). Original TMF type of the TU."""
  srclang: str | None = None
  """`srclang` attribute (optional). Specifies the source language if overriding the header value."""
  props: list[Prop] = field(default_factory=list)
  """Zero or more `<prop>` elements attached to the translation unit."""
  notes: list[Note] = field(default_factory=list)
  """Zero or more `<note>` elements providing commentary or metadata."""
  variants: list[Tuv] = field(default_factory=list)
  """One or more `<tuv>` elements that represent the translation variants for this TU."""


@dataclass(slots=True)
class Tmx:
  """Represents the root `<tmx>` element (TMX 1.4b §3.1)."""

  version: str
  """`version` attribute (required). Specifies the TMX version of this document."""
  header: Header
  """The `<header>` child element providing administrative metadata."""
  body: list[Tu] = field(default_factory=list)
  """The `<body>` child element containing one or more `<tu>` translation units."""
