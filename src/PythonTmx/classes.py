from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import MutableSequence
from datetime import datetime
from typing import Iterable, Literal, Self, TypeAlias
from warnings import deprecated

import lxml.etree as et
from attrs import define, field

XmlElement: TypeAlias = et._Element | ET.Element
TmxElement: TypeAlias = "Note | Prop | Ude | Map | Header| Tu| Tuv| Tmx|Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude"


@define(kw_only=True)
class Note:
  """
  A <note> element, used to give information about the parent element.
  Does not necessarily have to be in the same language as the parent element.
  Can be attached to :class:`Header`, :class:`Tu` and :class:`Tuv`.
  """

  text: str
  """
  The text of the note.
  """
  lang: str | None = None
  """
  The language of the note, by default None.
  """
  encoding: str | None = None
  """
  The original encoding of the text, by default None.
  """

  @classmethod
  def from_element(
    cls,
    elem: XmlElement,
    *,
    text: str | None = None,
    lang: str | None = None,
    encoding: str | None = None,
  ) -> Note:
    """
    Creates a :class:`Note` Element from a lxml `_Element` or an ElementTree
    Element.
    If an argument is provided, it will override the value parsed from the
    element.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    text : str | None, optional
        The text of the Note, by default None
    lang : str | None, optional
        The language of the Note, by default None
    encoding : str | None, optional
        The original encoding of the Note, by default None

    Returns
    -------
    Note
        A :class:`Note` Object with the attributes of the element.

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement.
    TypeError
        If any of the attributes is not a string.
    ValueError
        If `text` is not provided and the element does not have text.
    ValueError
        If the Element's tag is not 'note'

    Examples
    --------

    >>> from lxml.etree import Element
    >>> from PythonTmx.classes import Note
    >>> elem = Element("note")
    >>> elem.text = "This is a note"
    >>> elem.set("o-encoding", "utf-8")
    >>> note = Note.from_element(elem, lang="en", encoding="utf-16")
    >>> print(note)
    Note(text='This is a note', lang='en', encoding='utf-16')
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "note":
      raise ValueError(f"Expected <note> element, got {str(elem.tag)}")
    if text is None:
      if elem.text is None:
        raise ValueError("'text' must be provided or the element must have text")
      text = elem.text
    if lang is not None and not isinstance(lang, str):
      raise TypeError(f"Expected str for 'lang', got {type(lang)}")
    if encoding is not None and not isinstance(encoding, str):
      raise TypeError(f"Expected str for 'encoding', got {type(encoding)}")
    return Note(
      text=text,
      lang=lang
      if lang is not None
      else elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
      encoding=encoding if encoding is not None else elem.get("o-encoding"),
    )


@define(kw_only=True)
class Prop:
  """
  A <prop> Element, used to define the various properties of the parent element
  (or of the document when <prop> is used in the <header> element).
  These properties are not defined by the standard.
  """

  text: str
  """
  The text of the Prop.
  """
  type: str
  """
  The type of the Prop, by convention start with "x-".
  """
  lang: str | None = None
  """
  The language of the Prop, by default None.
  """
  encoding: str | None = None
  """
  The original encoding of the text, by default None.
  """

  @classmethod
  def from_element(
    cls,
    elem: XmlElement,
    *,
    text: str | None = None,
    type: str | None = None,
    lang: str | None = None,
    encoding: str | None = None,
  ) -> Prop:
    """
    Creates a :class:`Prop` Element from a lxml `_Element` or an ElementTree
    Element.
    If an argument is provided, it will override the value parsed from the
    element.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The element to parse.
    text : str | None, optional
        The text of the Prop, by default None
    type : str | None, optional
        The type of the Prop, by default None
        By convention start with "x-".
    lang : str | None, optional
        The language of the Prop, by default None
    encoding : str | None, optional
        The original encoding of the Prop, by default None

    Returns
    -------
    Prop
        A :class:`Prop` object.

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement.
    TypeError
        If any of the attributes is not a string.
    ValueError
        If `text` is not provided and the element does not have text.
    ValueError
        If `type` is not provided and the element does not have a 'type' attribute.
    ValueError
        If the Element's tag is not 'prop'

    Examples
    --------

    >>> from lxml.etree import Element
    >>> from PythonTmx.classes import Prop
    >>> elem = Element("prop")
    >>> elem.text = "This is a prop"
    >>> elem.set("type", "x-my-type")
    >>> elem.set("o-encoding", "utf-8")
    >>> prop = Prop.from_element(elem, lang="en", encoding="utf-16")
    >>> print(prop)
    Prop(text='This is a prop', type='x-my-type', lang='en', encoding='utf-16')
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "prop":
      raise ValueError(f"Expected <prop> element, got {str(elem.tag)}")
    if text is None:
      if elem.text is None:
        raise ValueError("'text' must be provided or the element must have text")
      text = elem.text
    if type is None:
      if elem.get("type") is None:
        raise ValueError(
          "'type' must be provided or the element must have a 'type' attribute"
        )
      type = elem.attrib["type"]
    if lang is not None and not isinstance(lang, str):
      raise TypeError(f"Expected str for 'lang', got {type(lang)}")
    if encoding is not None and not isinstance(encoding, str):
      raise TypeError(f"Expected str for 'encoding', got {type(encoding)}")
    return Prop(
      text=text,
      type=type,
      lang=lang
      if lang is not None
      else elem.get("{http://www.w3.org/XML/1998/namespace}lang"),
      encoding=encoding if encoding is not None else elem.get("o-encoding"),
    )


@define(kw_only=True)
class Map:
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None

  @classmethod
  def from_element(
    cls,
    elem: XmlElement,
    *,
    unicode: str | None = None,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
  ) -> Self:
    return cls(
      unicode=unicode if unicode is not None else elem.get("unicode"),  # type: ignore
      code=code if code is not None else elem.get("code"),
      ent=ent if ent is not None else elem.get("ent"),
      subst=subst if subst is not None else elem.get("subst"),
    )


@define(kw_only=True)
class Ude:
  name: str
  base: str | None = None
  maps: MutableSequence[Map] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib, maps=[Map.from_element(e) for e in elem if e.tag == "map"]
    )


@define(kw_only=True)
class Header:
  creationtool: str
  creationtoolversion: str
  segtype: str
  tmf: str
  adminlang: str
  srclang: str
  datatype: str
  encoding: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  changeid: str | None = None
  props: MutableSequence[Prop] = field(factory=list)
  notes: MutableSequence[Note] = field(factory=list)
  udes: MutableSequence[Ude] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    attribs = elem.attrib
    props, notes, udes = [], [], []
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
      elif e.tag == "ude":
        udes.append(Ude.from_element(e))
    return cls(
      encoding=attribs.pop("o-encoding"),
      tmf=attribs.pop("o-tmf"),
      **attribs,
      props=props,
      notes=notes,
      udes=udes,
    )

  def __attrs_post__init__(self):
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass


def _parse_inline(seg: XmlElement, mask: Iterable[str]) -> list:
  segment: list = []
  for e in seg:
    if seg.text is not None:
      segment.append(seg.text)
    for e in seg:
      if str(e.tag) not in mask:
        continue
      if e.tag == "bpt":
        segment.append(Bpt.from_element(e))
      elif e.tag == "ept":
        segment.append(Ept.from_element(e))
      elif e.tag == "it":
        segment.append(It.from_element(e))
      elif e.tag == "ph":
        segment.append(Ph.from_element(e))
      elif e.tag == "hi":
        segment.append(Hi.from_element(e))
      elif e.tag == "ut":
        segment.append(Ut.from_element(e))
      elif e.tag == "sub":
        segment.append(Sub.from_element(e))
      if e.tail is not None:
        segment.append(e.tail)
  return segment


@define(kw_only=True)
class Tuv:
  segment: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | int | None = None
  lastusagedate: str | datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  changeid: str | None = None
  tmf: str | None = None
  notes: MutableSequence[Note] = field(factory=list)
  props: MutableSequence[Prop] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    attribs = elem.attrib
    encoding = attribs.pop("o-encoding")
    tmf = attribs.pop("o-tmf")
    props, notes = [], []
    if (seg := elem.find("seg")) is not None:
      segment = _parse_inline(seg, mask=("bpt", "ept", "it", "ph", "hi", "ut"))
    else:
      segment = []
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
    return cls(
      segment=segment,
      encoding=encoding,
      tmf=tmf,
      props=props,
      notes=notes,
      **attribs,
    )

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Tu:
  tuid: str | None = None
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | int | None = None
  lastusagedate: str | datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | datetime | None = None
  creationid: str | None = None
  changedate: str | datetime | None = None
  segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
  changeid: str | None = None
  tmf: str | None = None
  srclang: str | None = None
  tuvs: MutableSequence[Tuv] = field(factory=list)
  notes: MutableSequence[Note] = field(factory=list)
  props: MutableSequence[Prop] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    props, notes, tuvs = [], [], []
    attribs = elem.attrib
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
      elif e.tag == "tuv":
        tuvs.append(Tuv.from_element(e))
    return cls(
      encoding=attribs.pop("o-encoding"),
      tmf=attribs.pop("o-tmf"),
      **attribs,
      props=props,
      notes=notes,
      tuvs=tuvs,
    )

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Tmx:
  header: Header | None = None
  tus: MutableSequence[Tu] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    if (header_elem := elem.find("header")) is not None:
      header = Header.from_element(header_elem)
    else:
      header = None
    tus: MutableSequence[Tu] = []
    if (body := elem.find("body")) is not None:
      for e in body:
        if e.tag == "tu":
          tus.append(Tu.from_element(e))
    return cls(header=header, tus=tus)


@define(kw_only=True)
class Bpt:
  i: int | str
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Ept:
  i: int | str
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Hi:
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut")),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class It:
  pos: Literal["begin", "end"]
  x: int | str | None = None
  type: str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Ph:
  i: int | str | None = None
  x: int | str | None = None
  assoc: Literal["p", "f", "b"] | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Sub:
  type: str | None = None
  datatype: str | None = None
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut")),
    )


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@define(kw_only=True)
class Ut:
  x: int | str | None = None
  content: MutableSequence[str | Sub] = field(factory=list)

  @classmethod
  def from_element(cls, elem: XmlElement) -> Self:
    return cls(
      **elem.attrib,
      content=_parse_inline(elem, mask=("sub",)),
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass
