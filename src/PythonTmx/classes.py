from __future__ import annotations

from collections.abc import Generator, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

__all__ = [
  "TmxElement",
  "InlineElement",
  "StructuralElement",
  "Bpt",
  "Ept",
  "It",
  "Ph",
  "Hi",
  "Ut",
  "Sub",
  "Map",
  "Ude",
  "Note",
  "Prop",
  "Header",
  "Tuv",
  "Tu",
  "Tmx",
  "POS",
  "SEGTYPE",
  "ASSOC",
]


class POS(Enum):
  """
  Whether an isolated tag :class:`It` is a beginning or and ending tag.
  """

  BEGIN = "begin"
  """
  Beginning tag
  """
  END = "end"
  """
  Ending tag
  """


class SEGTYPE(Enum):
  """
  Specifies the kind of segmentation. If a :class:`Tu` doesn't specify its segtype,
  CAT tools will default to the one in the :class:`Header` tag.
  """

  BLOCK = "block"
  """
  Used when segmentation does not correspond to one of the other values.
  """
  PARAGRAPH = "paragraph"
  """
  Used when a :class:`Tu` contains multiple multiple sentences.
  """
  SENTENCE = "sentence"
  """
  Used when a :class:`Tu` contains a single sentence.
  """
  PHRASE = "phrase"
  """
  Used when a :class:`Tu` contains single words or short phrases, not necessarily
  full sentences.
  """


class ASSOC(Enum):
  """
  Specifies whether a :class:`Ph` is associated with the previous part of the text,
  the next part of the text, or both.
  """

  PRIOR = "p"
  """
  Associated with the previous part of the text.
  """
  FOLLOWING = "f"
  """
  Associated with the next part of the text.
  """
  BOTH = "b"
  """
  Associated with both the previous and next parts of the text.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class TmxElement:
  """
  Base class for all elements in a TMX file.
  """

  extra: dict[str, str] = field(default_factory=dict, metadata={"exclude": True})


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class InlineElement(TmxElement):
  """
  Base class for all inline elements in a TMX file.
  """

  content: Sequence


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class StructuralElement(TmxElement):
  """
  Base class for all structural elements in a TMX file.
  """

  pass


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Bpt(InlineElement):
  """
  *Begin Paired Tag* - Delimits the beginning of a paired sequence of native code. Each :class:`Bpt`
  inside of a :class:`Tuv` must have a corresponding :class:`Ept`.
  """

  content: Sequence[str | Sub] = field(default_factory=list, metadata={"exclude": True})
  """
  The content of the :class:`Bpt`.
  """
  i: int
  """
  *Internal matching* - Used to pair :class:`Bpt` elements with their corresponding
  :class:`Ept` elements. Must be unique within a :class:`Tuv`. Required.
  """
  x: int | None = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`Ept` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: str | None = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """

  def __iter__(self) -> Generator[str | Sub, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ept(InlineElement):
  """
  *End Paired Tag* - Delimits the end of a paired sequence of native code. Each :class:`Ept` inside of
  a :class:`Tuv` must have a corresponding :class:`Bpt`.
  """

  content: Sequence[str | Sub] = field(default_factory=list, metadata={"exclude": True})
  """
  The content of the :class:`Ept`.
  """
  i: int
  """
  *Internal matching* - Used to pair :class:`Ept` elements with their corresponding
  :class:`Bpt` elements. Must be unique within a :class:`Tuv`. Required.
  """

  def __iter__(self) -> Generator[str | Sub, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Sub(InlineElement):
  """
  *Sub Flow* - Delimits sub-flow text inside a sequence of native code, e.g. the alt-text of
  a <img /> tag.
  """

  content: Sequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Sub`.
  """
  datatype: str | None = field(default=None)
  """
  *Datatype* - Used to specify the type of data contained. Optional, by default None.
  """
  type: str | None = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """

  def __iter__(self) -> Generator[str | Bpt | Ept | It | Ph | Hi | Ut, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class It(InlineElement):
  """
  *Isolated Tag* - Delimits a beginning/ending sequence of native codes that does not have its
  corresponding ending/beginning within the segment.
  """

  content: Sequence[str | Sub] = field(default_factory=list, metadata={"exclude": True})
  """
  The content of the :class:`It`.
  """
  pos: POS = field(metadata={"export_func": lambda x: x.value})
  """
  *Position* - Indicates whether an isolated tag :class:`It` is a beginning or
  and ending tag. Required.
  """
  x: int | None = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`It` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: str | None = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """

  def __iter__(self) -> Generator[str | Sub, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ph(InlineElement):
  """
  *Placeholder* - Delimits a sequence of native standalone codes in the segment.
  """

  content: Sequence[str | Sub] = field(default_factory=list, metadata={"exclude": True})
  """
  The content of the :class:`Ph`.
  """
  x: int | None = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that a :class:`Ph` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  assoc: ASSOC | None = field(default=None, metadata={"export_func": lambda x: x.value})
  """
  *Association* - Specifies whether a :class:`Ph` is associated with the previous
  part of the text, the next part of the text, or both. Optional, by default None.
  """
  type: str | None = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.
  """

  def __iter__(self) -> Generator[str | Sub, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Hi(InlineElement):
  """
  *Highlight* - Delimits a section of text that has special meaning.
  """

  content: Sequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Hi`.
  """
  x: int | None = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that a :class:`Hi` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """
  type: str | None = field(default=None)
  """
  *Type* - Used to specify the type of element. Optional, by default None.  
  """

  def __iter__(self) -> Generator[str | Bpt | Ept | It | Ph | Hi | Ut, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ut(InlineElement):
  """
  *Unknown Tag* - Delimit a sequence of native unknown codes in the segment.

  .. warning::
    This element is deprecated. It is still supported for compatibility with older
    versions of TMX, but it is not recommended for new TMX files.
  """

  content: Sequence[str | Sub] = field(default_factory=list, metadata={"exclude": True})
  """
  The content of the :class:`Ut`.
  """
  x: int | None = field(default=None)
  """
  *External matching* - Used to match inline elements between each :class:`Tuv`
  inside a :class:`Tu`. Note that an :class:`Ut` element is matched based on the
  :attr:`x` attribute of its corresponding :class:`Bpt` element. Optional,
  by default None.
  """

  def __iter__(self) -> Generator[str | Sub, None, None]:
    yield from self.content


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Map(StructuralElement):
  """
  *Mapping* - Used to map character and some of their properties.
  """

  unicode: str
  """
  *Unicode* - The Unicode character the mapping is for. A valid Unicode value
  (including values in the Private Use areas) in hexadecimal format.
  For example: unicode="#xF8FF". Required.
  """
  code: str | None = field(default=None)
  """
  *Code* - The code-point value corresponding to the unicode character.
  A hexadecimal value prefixed with "#x". For example: code="#x9F".
  Optional, by default None.
  """
  ent: str | None = field(default=None)
  """
  *Entity* - The entity name corresponding to the unicode character.
  Text in ASCII. For example: ent="copy". Optional, by default None.
  """
  subst: str | None = field(default=None)
  """
  *Substitution* - What to substitute the unicode character with. Text in ASCII.
  For example: subst="copy". Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Ude(StructuralElement):
  """
  *User-Defined encoding* - Used to define a user-defined encoding.
  """

  name: str
  """
  *Name* - The name of the encoding. Required.
  """
  base: str | None = None
  """
  *Base* - The encoding upon which the re-mapping is based. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.

  .. note::
    If at least one :class:`Map` element has a :attr:`code` attribute, the
    :attr:`base` attribute is required.
  """
  maps: Sequence[Map] = field(default_factory=list, metadata={"exclude": True})
  """
  A Sequence of :class:`Map` elements. By default an empty list.
  """

  def __iter__(self) -> Generator[Map, None, None]:
    yield from self.maps

  def __len__(self) -> int:
    return len(self.maps)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Note(StructuralElement):
  """
  *Note* - Used to provide information about the parent element.
  """

  text: str = field(metadata={"exclude": True})
  """
  The text of the :class:`Note`.
  """
  lang: str | None = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  """
  *Language* - The language of the :class:`Note`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Optional, by default None. Optional,
  by default None.
  """
  encoding: str | None = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Note`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Prop(StructuralElement):
  """
  *Property* - Used to provide information about specific properties of the parent
  element.

  These properties are not defined by the standard. The "text" can be any
  anything as long as it is in string format. By convention, values for the
  "type" attribute that are not defined by the standard should be prefixed with
  "x-". For example, "x-my-custom-type".
  """

  text: str = field(metadata={"exclude": True})
  """
  The text of the :class:`Prop`.
  """
  type: str
  """
  *Type* - The type of the :class:`Prop`. Required.

  .. note::
    The "type" attribute is not defined by the standard. The "text" can be any
    anything as long as it is in string format. By convention, values for the
    "type" attribute that are not defined by the standard should be prefixed with
    "x-". For example, "x-my-custom-type".
  """
  lang: str | None = field(
    default=None, metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  """
  *Language* - The language of the :class:`Prop`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Optional, by default None.
  """
  encoding: str | None = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Prop`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Header(StructuralElement):
  """
  *Header* - Contains information about the Tmx file itself. Most of the
  attributes here can be overriden at an element level. if an element does not
  have a value for an attribute, the value from the header will be used if present.

  .. note::
    CAT Tools are responsible for using values from the headeer when parsing
    the TMX file. PythonTmx does not automatically fill in the blanks when
    exporting a Tmx object to an xml Element.
  """

  creationtool: str
  """
  *Creation Tool* - The name of the tool that created the TMX file. Required.
  """
  creationtoolversion: str
  """
  *Creation Tool Version* - The version of the tool that created the TMX file.
  Required.
  """
  segtype: SEGTYPE = field(metadata={"export_func": lambda x: x.value})
  """
  *Segment Type* - The type of segmentation used in the TMX file unless
  specified otherwise in the element itself. Required.
  """
  tmf: str = field(metadata={"export_name": "o-tmf"})
  """
  *Original Translation Memory Format* - The orginal format the tmx file was
  exported from. Required.
  """
  adminlang: str
  """
  *Administrative Language* - The default language of :class:`Prop` and
  :class:`Note` elements unless specified otherwise in the element itself.
  Required.
  """
  srclang: str
  """
  *Source Language* - The default language of :class:`Tu` elements unless
  specified otherwise in the element itself. Required.
  """
  datatype: str
  """
  *Data Type* - The type of data in the TMX file unless specified otherwise in
  the element itself. Required.
  """
  encoding: str | None = field(metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the tmx file. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """
  creationdate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Creation Date* - The date the tmx file was created. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  creationid: str | None = None
  """
  *Creation ID* - The ID of the user who created the tmx file. Optional, by default None.
  """
  changedate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Change Date* - The date the tmx file was last edited. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  changeid: str | None = None
  """
  *Change ID* - The ID of the user who last edited the tmx file. Optional, by default None.
  """
  notes: Sequence[Note] = field(default_factory=list, metadata={"exclude": True})
  """
  *Notes* - Used to provide information about the parent element.
  Optional, by default an empty list.
  """
  props: Sequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  """
  *Properties* - Used to provide information about specific properties of the parent
  element. Optional, by default an empty list.
  """
  udes: Sequence[Ude] = field(default_factory=list, metadata={"exclude": True})
  """
  *User-Defined encoding* - Used to define a user-defined encoding.
  Optional, by default an empty list.
  """


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tuv(StructuralElement):
  """
  *Translation Unit Variant* - Contains the actual segments of the translation unit.
  """

  content: Sequence[str | Bpt | Ept | Ph | It | Hi | Ut] = field(
    default_factory=list, metadata={"exclude": True}
  )
  """
  The content of the :class:`Tuv`.
  """
  lang: str = field(
    metadata={"export_name": "{http://www.w3.org/XML/1998/namespace}lang"}
  )
  """
  *Language* - The language of the :class:`Tuv`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Required.
  """
  encoding: str | None = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Tuv`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """
  datatype: str | None = field(default=None)
  """
  *Data Type* - The type of data in the :class:`Tuv`. Optional, by default None.
  """
  usagecount: int | None = field(default=None)
  """
  *Usage Count* - The number of times the :class:`Tuv` has been used in the
  original translation memory. Optional, by default None.
  """
  lastusagedate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Last Usage Date* - The date the :class:`Tuv` was last used in the original
  translation memory. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  creationtool: str | None = field(default=None)
  """
  *Creation Tool* - The name of the tool that created the :class:`Tuv`. Optional,
  by default None.
  """
  creationtoolversion: str | None = field(default=None)
  """
  *Creation Tool Version* - The version of the tool that created the :class:`Tuv`.
  Optional, by default None.
  """
  creationdate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Creation Date* - The date the :class:`Tuv` was created. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  creationid: str | None = field(default=None)
  """
  *Creation ID* - The ID of the user who created the :class:`Tuv`. Optional, by default None.
  """
  changedate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Change Date* - The date the :class:`Tuv` was last edited. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  tmf: str | None = field(default=None, metadata={"export_name": "o-tmf"})
  """
  *Original Translation Memory Format* - The orginal format the :class:`Tuv` was
  exported from. Optional, by default None.
  """
  changeid: str | None = field(default=None)
  """
  *Change ID* - The ID of the user who last edited the :class:`Tuv`. Optional, by default None.
  """
  props: Sequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  """
  *Properties* - Used to provide information about specific properties of the parent
  element. Optional, by default an empty list.
  """
  notes: Sequence[Note] = field(default_factory=list, metadata={"exclude": True})
  """
  *Notes* - Used to provide information about the parent element.
  Optional, by default an empty list.
  """

  def __iter__(self) -> Generator[str | Bpt | Ept | Ph | It | Hi | Ut, None, None]:
    yield from self.content

  def __len__(self) -> int:
    return len(self.content)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tu(StructuralElement):
  """
  *Translation Unit* - Contains the the :class:`Tuv` elements for the source and
  target languages.

  .. note::
    Logically, a :class:`Tu` should contain at least 2 :class:`Tuv` elements,
    one for the source language and one for the target language. However, it is
    possible to have more than 2 :class:`Tuv` elements.
  """

  tuid: str | None = field(default=None)
  """
  *Translation Unit ID* - The ID of the :class:`Tu`. Optional, by default None.
  """
  encoding: str | None = field(default=None, metadata={"export_name": "o-encoding"})
  """
  *Original Encoding* - The encoding of the :class:`Tu`. One of the [IANA]
  recommended "charset identifier", if possible. Optional, by default None.
  """
  datatype: str | None = field(default=None)
  """
  *Data Type* - The type of data in the :class:`Tu`. Optional, by default None.
  """
  usagecount: int | None = field(default=None)
  """
  *Usage Count* - The number of times the :class:`Tu` has been used in the
  original translation memory. Optional, by default None.
  """
  lastusagedate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Last Usage Date* - The date the :class:`Tu` was last used in the original
  translation memory. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  creationtool: str | None = field(default=None)
  """
  *Creation Tool* - The name of the tool that created the :class:`Tu`. Optional,
  by default None.
  """
  creationtoolversion: str | None = field(default=None)
  """
  *Creation Tool Version* - The version of the tool that created the :class:`Tu`.
  Optional, by default None.
  """
  creationdate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Creation Date* - The date the :class:`Tu` was created. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  creationid: str | None = field(default=None)
  """
  *Creation ID* - The ID of the user who created the :class:`Tu`. Optional, by default None.
  """
  changedate: datetime | None = field(
    default=None,
    metadata={"export_func": lambda x: x.strftime(format="%Y%m%dT%H%M%SZ")},
  )
  """
  *Change Date* - The date the :class:`Tu` was last edited. Optional, by default None.

  .. note::
    When exported to an Element, the datetime object is converted to a string in
    the format "YYYYMMDDThhmmssZ".
  """
  segtype: SEGTYPE | None = field(
    default=None, metadata={"export_func": lambda x: x.value}
  )
  """
  *Segmentation Type* - The type of segmentation used in the :class:`Tu`.
  Optional, by default None.
  """
  changeid: str | None = field(default=None)
  """
  *Change ID* - The ID of the user who last edited the :class:`Tu`. Optional,
  by default None.
  """
  tmf: str | None = field(default=None, metadata={"export_name": "o-tmf"})
  """
  *Original Translation Memory Format* - The orginal format the :class:`Tu` was
  exported from. Optional, by default None.
  """
  srclang: str | None = field(default=None)
  """
  *Source Language* - The language of the :class:`Tu`. A language code as described
  in the [RFC 3066]. Not case-sensitive. Optional, by default None.

  .. note::
    If any of the :class:`Tuv` elements in the :class:`Tu` can be considered
    the source language, value can be set to \\*all\\*.
  """
  notes: Sequence[Note] = field(default_factory=list, metadata={"exclude": True})
  """
  *Notes* - Used to provide information about the parent element.
  Optional, by default an empty list.
  """
  props: Sequence[Prop] = field(default_factory=list, metadata={"exclude": True})
  """
  *Properties* - Used to provide information about specific properties of the parent
  element. Optional, by default an empty list.
  """
  tuvs: Sequence[Tuv] = field(default_factory=list, metadata={"exclude": True})
  """
  *Translation Unit Variants* - Contains the :class:`Tuv` elements for the source
  and target languages.
  """

  def __iter__(self) -> Generator[Tuv, None, None]:
    yield from self.tuvs

  def __len__(self) -> int:
    return len(self.tuvs)


@dataclass(unsafe_hash=True, kw_only=True, slots=True)
class Tmx(StructuralElement):
  """
  *Translation Memory* - Contains the :class:`Header` and :class:`Tu` elements.
  """

  header: Header
  """
  *Header* - Contains information about the :class:`Tmx` file itself.
  """
  tus: Sequence[Tu] = field(default_factory=list, metadata={"exclude": True})
  """
  *Translation Units* - Contains the :class:`Tu` elements.
  """

  def __iter__(self) -> Generator[Tu, None, None]:
    yield from self.tus

  def __len__(self) -> int:
    return len(self.tus)
