from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import MutableSequence
from datetime import datetime
from typing import Iterable, Literal, TypeAlias
from warnings import deprecated

import lxml.etree as et
from attr import asdict
from attrs import define, field, validators

XmlElement: TypeAlias = et._Element | ET.Element
TmxElement: TypeAlias = "Note | Prop | Ude | Map | Header| Tu| Tuv| Tmx|Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude"

__all__ = [
  "Note",
  "Prop",
  "Ude",
  "Map",
  "Header",
  "Tu",
  "Tuv",
  "Tmx",
  "Bpt",
  "Ept",
  "It",
  "Ph",
  "Hi",
  "Ut",
  "Sub",
  "Ude",
]


@define
class SupportsSub:
  content: MutableSequence[str | Sub] = field(factory=list)

  def add_sub(
    self,
    sub: Sub | Iterable[Sub] | None = None,
    *,
    type: str | None = None,
    datatype: str | None = None,
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> None:
    if isinstance(sub, Iterable):
      for s in sub:
        self.add_sub(s, type=type, datatype=datatype, content=content)
      return
    if sub is None:
      sub_ = Sub(
        type=type, datatype=datatype, content=content if content is not None else []
      )
    if not isinstance(sub, Sub):
      raise TypeError("sub must be a Sub object")
    else:
      sub_ = Sub(
        type=type if type is not None else sub.type,
        datatype=datatype if datatype is not None else sub.datatype,
        content=content if content is not None else sub.content,
      )
    self.content.append(sub_)


@define
class SupportsInlineNoSub:
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)

  def add_bpt(
    self,
    bpt: Bpt | Iterable[Bpt] | None = None,
    *,
    content: Iterable[str | Sub] | None = None,
    i: int | str | None = None,
    x: int | str | None = None,
    type: str | None = None,
  ) -> None:
    if isinstance(bpt, Iterable):
      for b in bpt:
        self.add_bpt(b, i=i, x=x, type=type, content=content)
      return
    if bpt is None:
      if i is None:
        raise ValueError("i must be specified if bpt is None")
      bpt_ = Bpt(
        type=type, i=i, x=x, content=list(content) if content is not None else []
      )
    if not isinstance(bpt, Bpt):
      raise TypeError("bpt must be a Bpt object")
    else:
      bpt_ = Bpt(
        type=type if type is not None else bpt.type,
        i=i if i is not None else bpt.i,
        x=x if x is not None else bpt.x,
        content=list(content) if content is not None else bpt.content,
      )
    self.content.append(bpt_)

  def add_ept(
    self,
    ept: Ept | Iterable[Ept] | None = None,
    *,
    content: Iterable[str | Sub] | None = None,
    i: int | str | None = None,
  ) -> None:
    if isinstance(ept, Iterable):
      for b in ept:
        self.add_ept(b, i=i, content=content)
      return
    if ept is None:
      if i is None:
        raise ValueError("i must be specified if ept is None")
      ept_ = Ept(i=i, content=list(content) if content is not None else [])
    if not isinstance(ept, Ept):
      raise TypeError("ept must be a Ept object")
    else:
      ept_ = Ept(
        i=i if i is not None else ept.i,
        content=list(content) if content is not None else ept.content,
      )
    self.content.append(ept_)

  def add_ph(
    self,
    ph: Ph | Iterable[Ph] | None = None,
    *,
    content: Iterable[str | Sub] | None = None,
    i: int | str | None = None,
    x: int | str | None = None,
    assoc: Literal["p", "f", "b"] | None = None,
  ) -> None:
    if isinstance(ph, Iterable):
      for p in ph:
        self.add_ph(p, content=content, i=i, x=x, assoc=assoc)
      return
    if ph is None:
      ph_ = Ph(
        i=i, content=list(content) if content is not None else [], x=x, assoc=assoc
      )
    if not isinstance(ph, Ph):
      raise TypeError("ph must be a Ph object")
    else:
      ph_ = Ph(
        i=i, content=list(content) if content is not None else [], x=x, assoc=assoc
      )
    self.content.append(ph_)

  def add_it(
    self,
    it: It | Iterable[It] | None = None,
    *,
    content: Iterable[str | Sub] | None = None,
    pos: Literal["begin", "end"] | None = None,
    x: int | str | None = None,
    type: str | None = None,
  ) -> None:
    if isinstance(it, Iterable):
      for i in it:
        self.add_it(content=content, pos=pos, x=x, type=type)
      return
    if it is None:
      if pos is None:
        raise ValueError("pos must be specified if it is None")
      it_ = It(
        pos=pos, x=x, type=type, content=list(content) if content is not None else []
      )
    else:
      it_ = It(
        pos=pos if pos is not None else it.pos,
        x=x if x is not None else it.x,
        type=type if type is not None else it.type,
        content=list(content) if content is not None else it.content,
      )
    self.content.append(it_)

  def add_hi(
    self,
    hi: Hi | Iterable[Hi] | None = None,
    *,
    type: str | None = None,
    x: str | int | None = None,
    content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> None:
    if isinstance(hi, Iterable):
      for h in hi:
        self.add_hi(h, type=type, x=x, content=content)
      return
    if hi is None:
      hi_ = Hi(type=type, x=x, content=content if content is not None else [])
    if not isinstance(hi, Hi):
      raise TypeError("hi must be a Hi object")
    else:
      hi_ = Hi(
        type=type if type is not None else hi.type,
        x=x if x is not None else hi.x,
        content=content if content is not None else hi.content,
      )
    self.content.append(hi_)

  def add_ut(
    self,
    ut: Ut | Iterable[Ut] | None = None,
    *,
    x: str | int | None = None,
    content: MutableSequence[str | Sub] | None = None,
  ) -> None:
    if isinstance(ut, Iterable):
      for u in ut:
        self.add_ut(u, x=x, content=content)
      return
    if ut is None:
      ut_ = Ut(x=x, content=list(content) if content is not None else [])
    if not isinstance(ut, Ut):
      raise TypeError("ut must be a Ut object")
    else:
      ut_ = Ut(
        x=x if x is not None else ut.x,
        content=list(content) if content is not None else ut.content,
      )
    self.content.append(ut_)


@define
class SupportsNotesAndProps:
  notes: MutableSequence[Note] = field(factory=list)
  props: MutableSequence[Prop] = field(factory=list)

  def add_note(
    self,
    note: Note | Iterable[Note] | None = None,
    *,
    text: str | None = None,
    lang: str | None = None,
    encoding: str | None = None,
  ) -> None:
    """
    Creates a new :class:`Note` object and appends it to the :attr:`notes`
    attribute of the object.

    .. note::
        The :class:`Note` object that is added is `always` a new object.
        To add your :class:`Note` object to the :attr:`notes` attribute,
        you need to directly append it using notes.append(my_note).

        .. code-block:: python

            from PythonTmx import Tu, Note

            my_note = Note(text="Hello")
            my_tu = Tu()
            my_tu.add_note(my_note)
            my_tu.notes.append(my_note)
            # the tu added by add_note is not the same object as my_note
            assert my_tu.notes[0] is not my_note
            # the directly appended note is the same
            assert my_tu.notes[1] is my_note
            # both notes are equal
            assert my_tu.notes[0] == my_tu.notes[1]


    If an Iterable of :class:`Note` objects is passed, a new :class:`Note`
    object is created for each element in the iterable and appended to the
    :attr:`notes` attribute of the object.

    if `note` is None, both `text` and `type` must be specified.

    If both `note` and any other parameters are specified, the provided
    parameters will take precedence over the values from the :class:`Note` if
    provided

    If `note` is an Iterable of :class:`Note` objects, the provided
    arguments will be applied to each :class:`Note` object in the iterable.

    Parameters
    ----------
    note : Note | Iterable[Note] | None, optional
        The note to add to the :class:`Note` object.
        If None, :attr:`text <Note.text>` must be provided.
        By default, None.
        For more info see: :class:`Note`
    text : str, optional
        The text of the note.
        If None, `note` attreter must be provided.
        By default, None.
        For more info see: :attr:`text <Note.text>`
    encoding : str, optional
        The encoding of the note. By default, None.
        For more info see: :attr:`encoding <Note.encoding>`
    lang : str, optional
        The language of the note. By default, None.
        For more info see: :attr:`lang <Note.lang>`

    Raises
    ------
    TypeError
        If note is not a :class:`Note` object, if any of the objects in note is
        not a :class:`Note` object (if an Iterable is provided), or if both
        'note' and 'text' are None.

    Examples
    --------
    .. code-block:: python

        from PythonTmx import Note, Tu

        tu = Tu()
        tu.add_note(Note(text="This is a note", lang="en"), text="override text")
        print(tu.notes)
        # Output:
        # [Note(text='override text', lang='en', encoding=None)]

    See also
    --------
    :class:`Note`, :class:`Prop`, :meth:`add_prop`
    """
    if isinstance(note, Iterable):
      for n in note:
        self.add_note(n, text=text, encoding=encoding, lang=lang)
      return
    if not isinstance(note, Note):
      raise TypeError("note must be a Note object")
    elif note is None:
      if text is None:
        raise TypeError("if 'note' is None, 'text' must be provided")
      note_ = Note(text=text, lang=lang, encoding=encoding)
    else:
      note_ = Note(
        text=text if text is not None else note.text,
        lang=lang if lang is not None else note.lang,
        encoding=encoding if encoding is not None else note.encoding,
      )
    self.notes.append(note_)

  def add_prop(
    self,
    prop: Prop | Iterable[Prop] | None = None,
    *,
    text: str | None = None,
    type: str | None = None,
    lang: str | None = None,
    encoding: str | None = None,
  ) -> None:
    """
    Appends a :class:`Prop` to the :attr:`props` attribute of the object.

    .. note::
        The :class:`Prop` object that is added is `always` a new object.
        To add your :class:`Prop` object to the :attr:`props` attribute,
        you need to directly append it using notes.append(my_prop).

        .. code-block:: python

            from PythonTmx import Tu, Prop

            my_prop = Prop(text="Hello")
            my_tu = Tu()
            my_tu.add_prop(my_prop)
            my_tu.props.append(my_prop)
            # the tu added by add_prop is not the same object as my_prop
            assert my_tu.props[0] is not my_prop
            # the directly appended prop is the same
            assert my_tu.props[1] is my_prop
            # both props are equal
            assert my_tu.props[0] == my_tu.props[1]

    If an Iterable of :class:`Prop` objects is passed, a new :class:`Prop`
    object is created for each element in the iterable and appended to the
    :attr:`props` attribute of the object.

    if `prop` is None, both `text` and `type` must be specified.

    If both `prop` and any other parameters are specified, the provided
    parameters will take precedence over the values from the :class:`Prop` if
    provided

    If `prop` is an Iterable of :class:`Prop` objects, the provided
    arguments will be applied to each :class:`Prop` object in the iterable.

    Parameters
    ----------
    prop : Prop | Iterable[Prop] | None, optional
        The prop to add to the :class:`Prop` object.
        If None, `text` must be provided.
        By default, None.
        For more info see: :class:`Prop`
    text : str, optional
        The text of the prop.
        If None, `prop` attribute must be provided.
        By default, None.
        For more info see: :attr:`text <Prop.text>`
    type : str, optional
        The kind of data the element represents, by convention start with "x-".
        By default, None.
        For more info see: :attr:`type <Prop.type>`
    encoding : str, optional
        The encoding of the prop. By default, None.
        For more info see: :attr:`encoding <Prop.encoding>`
    lang : str, optional
        The language of the prop. By default, None.
        For more info see: :attr:`lang <Prop.lang>`

    Raises
    ------
    TypeError
        If prop is not a :class:`Prop` object, if any of the objects in prop is
        not a :class:`Prop` object (if an Iterable is provided), or if both
        'prop' and 'text' are None.

    Examples
    --------
    .. code-block:: python

        from PythonTmx import Prop, Tu

        tu = Tu()
        tu.add_prop(Prop(text="This is a note", type="x-fake"), text="override text")
        print(tu.props)
        # Output:
        # [Prop(text='override text', type='x-fake', lang=None, encoding=None)]

    See also
    --------
    :class:`Note`, :class:`Prop`, :meth:`add_note`
    """
    if isinstance(prop, Iterable):
      for p in prop:
        self.add_prop(p, text=text, encoding=encoding, lang=lang, type=type)
      return
    if not isinstance(prop, Prop):
      raise TypeError("prop must be a Prop object")
    elif prop is None:
      if text is None or type is None:
        raise TypeError("if 'prop' is None, 'text' and 'type' must be provided")
      prop_ = Prop(text=text, lang=lang, encoding=encoding, type=type)
    else:
      prop_ = Prop(
        text=text if text is not None else prop.text,
        lang=lang if lang is not None else prop.lang,
        encoding=encoding if encoding is not None else prop.encoding,
        type=type if type is not None else prop.type,
      )
    self.props.append(prop_)


def _fill_attributes(elem: XmlElement, attribs: dict) -> None:
  for k, v in attribs.items():
    match k:
      case "text":
        elem.text = v
      case "lang":
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", v)
      case "encoding" | "tmf":
        elem.set(f"o-{k}", v)
      case "i" | "x" | "usagecount":
        if not isinstance(v, int):
          v = int(v)
        elem.set(k, str(v))
      case "lastusagedate" | "creationdate" | "changedate":
        if not isinstance(v, datetime):
          v = datetime.fromisoformat(v)
        elem.set(k, v.strftime("%Y%m%dT%H%M%SZ"))
      case _:
        elem.set(k, v)


def _only_str(k, v) -> bool:
  return isinstance(v, str)


def _only_str_int_dt(k, v) -> bool:
  return isinstance(v, (str, int, datetime))


def _to_element_inline(
  elem: et._Element,
  content: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut | Sub],
  mask: Iterable[str],
) -> None:
  last: et._Element | None = None
  for i in content:
    if isinstance(i, str):
      if last is None:
        if elem.text is None:
          elem.text = ""
        elem.text += i
      else:
        if last.tail is None:
          last.tail = ""
        last.tail += i
    elif isinstance(i, Bpt) and "bpt" in mask:
      elem.append(Bpt._to_element(i))
      last = elem[-1]
    elif isinstance(i, Ept) and "ept" in mask:
      elem.append(Ept._to_element(i))
      last = elem[-1]
    elif isinstance(i, It) and "it" in mask:
      elem.append(It._to_element(i))
      last = elem[-1]
    elif isinstance(i, Ph) and "ph" in mask:
      elem.append(Ph._to_element(i))
      last = elem[-1]
    elif isinstance(i, Hi) and "hi" in mask:
      elem.append(Hi._to_element(i))
      last = elem[-1]
    elif isinstance(i, Ut) and "ut" in mask:
      elem.append(Ut._to_element(i))
      last = elem[-1]
    elif isinstance(i, Sub) and "sub" in mask:
      elem.append(Sub._to_element(i))
      last = elem[-1]
    else:
      raise TypeError(
        f"Element of type {type(i)} cannot be children of {str(elem.tag)} elements"
      )


def _parse_inline(elem: XmlElement, mask: Iterable[str]) -> list:
  """
  Internal function to parse inline elements. Returns a list of strings and
  :class:`Bpt`, :class:`Ept`, :class:`It`, :class:`Ph`, :class:`Hi`, :class:`Ut`
  and :class:`Sub` elements.
  The returned list will contain firtst the text of the element if it has any,
  then the object's representation of all children in document order, each
  followed by their tail text if any.

  Parameters
  ----------
  elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
      The element to parse.
  mask : Iterable[str]
      A list of tags that should converted to their corresponding objects.
      Any element whose tag is not in the mask will be ignored.

  Returns
  -------
  list
      A list of strings and :class:`Bpt`, :class:`Ept`, :class:`It`, :class:`Ph`,
      :class:`Hi`, :class:`Ut` and :class:`Sub` elements, depending on the
      `mask` attribute.
  """
  result: list = []
  if elem.text is not None:
    result.append(elem.text)
  for e in elem:
    for e in elem:
      if str(e.tag) not in mask:
        continue
      if e.tag == "bpt":
        result.append(Bpt._from_element(e))
      elif e.tag == "ept":
        result.append(Ept._from_element(e))
      elif e.tag == "it":
        result.append(It._from_element(e))
      elif e.tag == "ph":
        result.append(Ph._from_element(e))
      elif e.tag == "hi":
        result.append(Hi._from_element(e))
      elif e.tag == "ut":
        result.append(Ut._from_element(e))
      elif e.tag == "sub":
        result.append(Sub._from_element(e))
      if e.tail is not None:
        result.append(e.tail)
  return result


@define(kw_only=True)
class Note:
  """
  A `note <https://www.gala-global.org/tmx-14b#note>`_ element,
  used to give information about the parent element.
  Can be attached to :class:`Header`, :class:`Tu` and :class:`Tuv`.
  """

  text: str = field(validator=validators.instance_of(str))
  """
  The text of the note.
  """
  lang: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The locale of the text, by default None. Ideally a language code as
  described in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
  """
  encoding: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """

  @staticmethod
  def _from_element(
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
    elem : :external:class:`lxml Element <lxml.etree._Element>`_ | :external:class:`ElementTree Element <xml.etree.ElementTree.Element>`_
        The Element to parse.
    text : str | None, optional
        The text of the Note, by default None
    lang : str | None, optional
        The locale of the text. Ideally a language code as described in the
        `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
        Unlike the other TMX attributes, the values for lang are not case-sensitive.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set. Ideally one of the
        `IANA recommended charsets
        <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
        By default None.

    Returns
    -------
    Note
        A new :class:`Note` Object with the attributes of the element.

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If `text` is not provided and the element does not have text or the
        element's tag is not 'note'.

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

  @staticmethod
  def _to_element(note: Note) -> et._Element:
    """
    Convert a :class:`Note` to an :external:class:`lxml Element <lxml.etree._Element>`_.

    Parameters
    ----------
    note : Note
        The :class:`Note` to convert.

    Returns
    -------
    :external:class:`lxml Element <lxml.etree._Element>`_
        The converted :class:`Note` as an :external:class:`lxml Element <lxml.etree._Element>`_.
    """

    attribs = asdict(note, filter=_only_str)
    elem = et.Element("note")
    _fill_attributes(elem, attribs)
    return elem


@define(kw_only=True)
class Prop:
  """
  A `prop <https://www.gala-global.org/tmx-14b#prop>`_ Element,
  used to define the various properties of the parent element.
  These properties are not defined by the standard.
  Can be attached to :class:`Header`, :class:`Tu` and :class:`Tuv`.
  """

  text: str = field(validator=validators.instance_of(str))
  """
  The text of the Prop.
  """
  type: str = field(validator=validators.instance_of(str))
  """
  The kind of data the element represents, by convention start with "x-".
  By default None.
  """
  lang: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The locale of the text. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
  """
  encoding: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  encoding : str | None, optional
    The original or preferred code set of the data of the element in case
    it is to be re-encoded in a non-Unicode code set. Ideally one of the
    `IANA recommended charsets
    <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
    By default None.
  """

  @staticmethod
  def _from_element(
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
        The Element to parse.
    text : str | None, optional
        The text of the Note, by default None
    type : str | None, optional
        The kind of data the element represents, by convention start with "x-".
        By default None.
    lang : str | None, optional
        The locale of the text. Ideally a language code as described in the
        `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other
        TMX attributes, the values for lang are not case-sensitive.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set. Ideally one of the
        `IANA recommended charsets
        <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_

    Returns
    -------
    Note
        A new :class:`Note` Object with the attributes of the element.

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If `text` is not provided and the element does not have text,
        if `type` is not provided and the element does not have a 'type' attribute,
        or the element's tag is not 'prop'.

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

  @classmethod
  def _to_element(cls, prop: Prop) -> et._Element:
    """
    Convert a :class:`Prop` to an :external:class:`lxml Element <lxml.etree._Element>`_.

    Parameters
    ----------
    prop : Prop
        The :class:`Prop` to convert.

    Returns
    -------
    :external:class:`lxml Element <lxml.etree._Element>`_
        The converted :class:`Prop` as an :external:class:`lxml Element <lxml.etree._Element>`_.
    """

    attribs = asdict(prop, filter=_only_str)
    elem = et.Element("prop")
    _fill_attributes(elem, attribs)
    return elem


@define(kw_only=True)
class Map:
  """
  The `map <https://www.gala-global.org/tmx-14b#map>`_ element, used to specify
  a user-defined character and some of its properties. Can oly be attached to
  :class:`Ude`.
  """

  unicode: str = field(validator=validators.instance_of(str))
  """
  The Unicode character value of the element. Must be a valid Unicode value
  (including values in the Private Use areas) in hexadecimal format.
  """
  code: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )

  @code.validator
  def _code_validator(self, attribute, value):
    if value is not None:
      if not value.startswith("#x"):
        raise ValueError(
          f"code must be a Hexadecimal value prefixed with '#x'. " f"Got: {value!r}"
        )
      try:
        hex(int(value[2:], 16))
      except ValueError:
        raise ValueError(
          f"code must be a Hexadecimal value prefixed with '#x'. " f"Got: {value!r}"
        )

  """
  The code-point value corresponding to the unicode character of a the element.
  Must be a Hexadecimal value prefixed with "#x". By default None.
  """
  ent: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The entity name of the character defined by the element. Must be text in ASCII.
  By default None.
  """

  @ent.validator
  def _ent_validator(self, attribute, value: str):
    if value is not None:
      if not value.isascii():
        raise ValueError(f"Expected ASCII string, got {value!r}")

  subst: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  An alternative string for the character defined in the element. Must be text
  in ASCII. By default None.
  """

  @subst.validator
  def _subst_validator(self, attribute, value: str):
    if value is not None:
      if not value.isascii():
        raise ValueError(f"expected ASCII string, got {value!r}")

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    unicode: str | None = None,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
  ) -> Map:
    """
    Create a :class:`Map` from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    unicode : str | None, optional
      The Unicode character value of the element. Must be a valid Unicode value
      (including values in the Private Use areas) in hexadecimal format.
    code: str | None = None
      The code-point value corresponding to the unicode character of a the
      element. Must be a Hexadecimal value prefixed with "#x".
      By default None.
    ent: str | None = None
      The entity name of the character defined by the element.
      Must be text in ASCII. By default None.
    subst: str | None = None
      An alternative string for the character defined in the element. Must be
      text in ASCII. By default None.

    Returns
    -------
    Map
        A new :class:`Map` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        if `unicode` is not provided and the element does not have a 'unicode'
        attribute, or the element's tag is not 'map'.

    Examples
    --------
    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Map
    >>> elem = Element("map")
    >>> elem.set("unicode", "00A0")
    >>> elem.set("code", "#x00A0")
    >>> elem.set("ent", "nbsp")
    >>> elem.set("subst", " ")
    >>> map = Map.from_element(elem)
    >>> print(map)
    Map(unicode='00A0', code='#x00A0', ent='nbsp', subst=' ')
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if unicode is None:
      if elem.get("unicode") is None:
        raise ValueError("unicode is required")
      unicode = elem.attrib["unicode"]
    return Map(
      unicode=unicode,
      code=code if code is not None else elem.get("code"),
      ent=ent if ent is not None else elem.get("ent"),
      subst=subst if subst is not None else elem.get("subst"),
    )

  @classmethod
  def _to_element(cls, map: Map) -> et._Element:
    """
    Convert a :class:`Note` to an :external:class:`lxml Element <lxml.etree._Element>`_.

    Parameters
    ----------
    map : Map
        The :class:`Map` to convert.

    Returns
    -------
    :external:class:`lxml Element <lxml.etree._Element>`_
        The converted :class:`Map` as an :external:class:`lxml Element <lxml.etree._Element>`_.
    """

    attribs = asdict(map, filter=_only_str)
    elem = et.Element("map")
    _fill_attributes(elem, attribs)
    return elem


@define(kw_only=True)
class Ude:
  """
  The `ude <https://www.gala-global.org/tmx-14b#ude>`_ Element, used to specify
  a set of user-defined characters and/or, optionally their mapping from
  Unicode to the user-defined encoding.
  Can only be attached to :class:`Header`.
  """

  name: str = field(validator=validators.instance_of(str))
  """
  The name of a element. Its value is not defined by the standard
  """
  base: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The encoding upon which the re-mapping of the element is based.
  Ideally one of the [IANA] `recommended charset
  <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  Required if at least of the :class:`Map` elements has a `code` attribute.
  """
  maps: MutableSequence[Map] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Map)),
  )
  """
  A MutableSequence of :class:`Map` elements.
  While any iterable (or even a Generator expression) can technically be used,
  it is recommended to use a list or some other collection that preserves the
  order of the elements.
  At the very least, the container should support the ``append`` method if the
  :meth:`add_map` function will be used.
  """

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    name: str | None = None,
    base: str | None = None,
    maps: Iterable[Map] | None = None,
  ) -> Ude:
    """
    Create a :class:`Ude` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    name: str
      The name of the element. Its value is not defined by the standard
    base: str | None = None
      The encoding upon which the re-mapping of the element is based.
      Ideally one of the [IANA] `recommended charset
      <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
      Required if at least of the :class:`Map` elements has a `code` attribute.
    maps: Iterable[Map], optional
      An Iterable of :class:`Map` elements. While any iterable (or even a
      generator expression) can be used, the resulting element :attr:`maps`
      will be a list of :class:`Map` elements. If the Iterable is does not
      preserve insertion order, the order of the resulting list cannot be
      guaranteed. By default an empty list.

    Returns
    -------
    Ude
        A new :class:`Ude` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If `name` is not provided and the element does not have a 'name' attribute,
        or the element's tag is not 'ude'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Ude, Map
    >>> elem = Element("ude")
    >>> elem.set("name", "ude-name")
    >>> elem.set("base", "ude-base")
    >>> maps = [Map(unicode="#xF8FF", code="#xF0")]
    >>> ude = Ude.from_element(elem, maps=maps)
    >>> print(ude)
    Ude(name='ude-name', base='ude-base', maps=[Map(unicode='#xF8FF', code='#xF0', ent=None, subst=None)])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "ude":
      raise ValueError(f"Expected <ude> element, got {str(elem.tag)}")
    if name is None:
      if elem.get("name") is None:
        raise ValueError(
          "'name' must be provided or the element must have a 'name' attribute"
        )
      name = elem.attrib["name"]
    if maps is None:
      maps = [Map._from_element(e) for e in elem if e.tag == "map"]
    else:
      for map in maps:
        if not isinstance(map, Map):
          raise TypeError(f"Expected Map, got {type(map)}")
    return Ude(
      name=name, base=base if base is not None else elem.get("base"), maps=list(maps)
    )

  def _to_element(self) -> et._Element:
    """
    Convert a :class:`Note` to an :external:class:`lxml Element <lxml.etree._Element>`_.

    Parameters
    ----------
    map : Map
        The :class:`Map` to convert.

    Returns
    -------
    :external:class:`lxml Element <lxml.etree._Element>`_
        The converted :class:`Map` as an :external:class:`lxml Element <lxml.etree._Element>`_.
    """

    attribs = asdict(self, filter=_only_str_int_dt)
    elem = et.Element("ude")
    _fill_attributes(elem, attribs)
    for map in self.maps:
      if not isinstance(map, Map):
        raise TypeError(f"Expected Map, got {type(map)}")
      if map.code is not None and self.base is None:
        raise ValueError("base cannot be None if at least 1 map has a code attribute")
      elem.append(Map._to_element(map))
    return elem

  def add_map(
    self,
    map: Map | Iterable[Map],
    *,
    unicode: str | None = None,
    code: str | None = None,
    ent: str | None = None,
    subst: str | None = None,
  ) -> None:
    """
    Appends a :class:`Map` to the :attr:`maps <Ude.maps>` attribute of the current
    :class:`Ude`.

    .. note::
        The :class:`Map` object that is added is `always` a new object.
        To add your :class:`Map` object to the :attr:`maps <Ude.maps>` attribute,
        you need to directly append it using notes.append(my_map).

        .. code-block:: python

            from PythonTmx import Ude, Map

            my_map = Map(unicode="A")
            my_ude = Ude(name="my_ude")
            my_ude.add_map(my_map)
            my_ude.maps.append(my_map)
            # the map added by add_map is not the same object as my_map
            assert my_ude.maps[0] is not my_map
            # the directly appended map is the same
            assert my_ude.maps[1] is my_map
            # both maps are equal
            assert my_ude.maps[0] == my_ude.maps[1]

    If an Iterable of :class:`Map` objects is passed, a new :class:`Map`
    object is created for each element in the iterable and appended to the
    :attr:`maps <Ude.maps>` attribute of the object.

    if `map` is None, `unicode` must be specified.

    If both `map` and any other parameters are specified, the provided
    parameters will take precedence over the values from the :class:`Map` if
    provided

    If `map` is an Iterable of :class:`Map` objects, the provided
    arguments will be applied to each :class:`Map` object in the iterable.

    Parameters
    ----------
    map : Map | Iterable[Map] | None, optional
        The :class:`Map` object to add to the :class:`Ude` object.
        If None, :attr:`unicode <Map.unicode>` must be provided.
        By default, None.
        For more info see: :class:`Map`
    unicode : str, optional
        The Unicode character value of the element. Must be a valid Unicode value
        (including values in the Private Use areas) in hexadecimal format.
        By default, None.
        For more info see: :attr:`unicode <Map.unicode>`
    code : str | None, optional
        The code-point value corresponding to the unicode character of a the
        element. Must be a Hexadecimal value prefixed with "#x". By default None.
        By default, None.
        For more info see: :attr:`code <Map.code>`
    ent : str | None, optional
        The entity name of the character defined by the element. Must be text in
        ASCII. By default None.
        By default, None.
        For more info see: :attr:`ent <Map.ent>`
    subst : str | None, optional
        An alternative string for the character defined in the element. Must be
        text in ASCII. By default None.
        For more info see: :attr:`subst <Map.subst>`

    Raises
    ------
    TypeError
        If 'map' is not a :class:`Map` object, if any of the objects in 'map' is
        not a :class:`Map` object (if an Iterable is provided), or if both
        'map' and 'unicode' are None.

    Examples
    --------
    .. code-block:: python

        from PythonTmx import Map, Ude

        ude = Ude(name="ude-name")
        ude.add_map(Map(unicode="#xF8FF", code="#xF0"), unicode="override")
        print(ude.maps)
        # Output:
        # [Map(unicode='override', code='#xF0', ent=None, subst=None)]

    See also
    --------
    :class:`Map`, :class:`Ude`, :class:`Header`, :meth:`add_ude`
    """
    if isinstance(map, Iterable):
      for m in map:
        self.add_map(m, unicode=unicode, code=code, ent=ent, subst=subst)
      return
    if not isinstance(map, Map):
      raise TypeError("map must be a Map object")
    elif map is None:
      if unicode is None:
        raise TypeError("if 'map' is None, 'unicode' must be provided")
      map_ = Map(unicode=unicode, code=code, ent=ent, subst=subst)
    else:
      map_ = Map(
        unicode=unicode if unicode is not None else map.unicode,
        code=code if code is not None else map.code,
        ent=ent if ent is not None else map.ent,
        subst=subst if subst is not None else map.subst,
      )
    self.maps.append(map_)


@define(kw_only=True)
class Header(SupportsNotesAndProps):
  """
  The `header <https://www.gala-global.org/tmx-14b#header>`_ element, used to
  specify the metadata of the TMX file. Can only be attached to :class:`Tmx`.
  A :class:`Tmx` can have only one :class:`Header` element.
  """

  creationtool: str = field(validator=validators.instance_of(str))
  """
  The tool that created the TMX document.
  """
  creationtoolversion: str = field(validator=validators.instance_of(str))
  """
  the version of the tool that created the TMX document.
  """
  segtype: Literal["block", "paragraph", "sentence", "phrase"] = field(
    validator=validators.in_(("block", "paragraph", "sentence", "phrase"))
  )
  """
  The type of segmentation used in the file.
  """
  tmf: str = field(validator=validators.instance_of(str))
  """
  The format of the translation memory file from which the TMX document or
  segment thereof have been generated.
  """
  adminlang: str = field(validator=validators.instance_of(str))
  """
  The default language for the administrative and informative elements
  :class:`Prop` and :class:`Note`. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for adminlang are not case-sensitive.
  """
  srclang: str = field(validator=validators.instance_of(str))
  """
  The source language of the file. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for srclang are not case-sensitive.
  """
  datatype: str = field(validator=validators.instance_of(str))
  """
  The type of the data contained in the file.
  """
  encoding: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  creationdate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the file was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that created the file, by default None
  """
  changedate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the file was last changed, by default None
  It is recommended to use :external:class:`datetime.datetime` objects
  instead of raw strings. If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  """
  changeid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that last changed the file, by default None
  """
  props: MutableSequence[Prop] = field(
    factory=list, validator=validators.deep_iterable(validators.instance_of(Prop))
  )
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_prop` function will be used.
  """
  notes: MutableSequence[Note] = field(
    factory=list, validator=validators.deep_iterable(validators.instance_of(Note))
  )
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_note` function will be used.
  """
  udes: MutableSequence[Ude] = field(
    factory=list, validator=validators.deep_iterable(validators.instance_of(Ude))
  )
  """
  A MutableSequence of :class:`Ude` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_ude` function will be used.
  """

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
    tmf: str | None = None,
    adminlang: str | None = None,
    srclang: str | None = None,
    datatype: str | None = None,
    encoding: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    props: Iterable[Prop] | None = None,
    notes: Iterable[Note] | None = None,
    udes: Iterable[Ude] | None = None,
  ) -> Header:
    """
    Create a :class:`Header` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    creationtool : str
        The tool that created the TMX document.
    creationtoolversion : str
        The version of the tool that created the TMX document.
    segtype : Literal["block", "paragraph", "sentence", "phrase"]
        The type of segmentation used in the file.
    tmf : str
        The format of the translation memory file from which the TMX document or
        segment thereof have been generated.
    adminlang : str
        The default language for the administrative and informative elements
        :class:`Prop` and :class:`Note`. Ideally a language code as described
        in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the
        other TMX attributes, the values for adminlang are not case-sensitive.
    srclang : str
        The source language of the file. Ideally a language code as described
        in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the
        other TMX attributes, the values for srclang are not case-sensitive.
    datatype : str
        The type of the data contained in the file.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set. Ideally one of the
        `IANA recommended charsets
        <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
        By default None.
    creationdate : str | datetime | None, optional
        The date and time the file was created. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    creationid : str | None, optional
        The ID of the user that created the file, by default None
        By default None.
    changedate : str | datetime | None, optional
        The date and time the file was last changed. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    changeid : str | None, optional
        The ID of the user that last changed the file, by default None
        By default None.
    props : Iterable[Prop] | None, optional
        A Iterable of :class:`Prop` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`props` will be a list of :class:`Prop` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    udes : Iterable[Ude] | None, optional
        A Iterable of :class:`Ude` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`udes` will be a list of :class:`Ude` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.

    Returns
    -------
    Header
        A new :class:`Header` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'header'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Header, Prop, Note, Ude, Map
    >>> elem = Element("header")
    >>> elem.set("creationtool", "tool")
    >>> elem.set("creationtoolversion", "1.0")
    >>> elem.set("segtype", "block")
    >>> elem.set("o-tmf", "tmx")
    >>> elem.set("adminlang", "en")
    >>> elem.set("srclang", "en")
    >>> elem.set("datatype", "text")
    >>> elem.set("encoding", "utf-8")
    >>> elem.set("creationdate", "20240101T000000Z")
    >>> elem.set("creationid", "user")
    >>> elem.set("changedate", "20240101T000000Z")
    >>> elem.set("changeid", "user")
    >>> props = [Prop(text="prop-text", type="x-prop-type")]
    >>> notes = [Note(text="note-text", lang="en")]
    >>> udes = [
    ...   Ude(
    ...     name="ude-name", base="ude-base", maps=[Map(unicode="#xF8FF", code="#xF0")]
    ...   )
    ... ]
    >>> header = Header.from_element(elem, props=props, notes=notes, udes=udes)
    >>> print(header)
    Header(creationtool='tool', creationtoolversion='1.0', segtype='block', tmf='tmx', adminlang='en', srclang='en', datatype='text', encoding=None, creationdate='20240101T000000Z', creationid='user', changedate='20240101T000000Z', changeid='user', props=[Prop(text='prop-text', type='x-prop-type', lang=None, encoding=None)], notes=[Note(text='note-text', lang='en', encoding=None)], udes=[Ude(name='ude-name', base='ude-base', maps=[Map(unicode='#xF8FF', code='#xF0', ent=None, subst=None)])])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "header":
      raise ValueError(f"Expected <header> element, got {str(elem.tag)}")
    attribs = elem.attrib
    if props is None:
      props = [Prop._from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note._from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    if udes is None:
      udes = [Ude._from_element(e) for e in elem if e.tag == "ude"]
    else:
      udes_ = []
      for ude in udes:
        if not isinstance(ude, Ude):
          raise TypeError(f"Expected Ude, got {type(ude)}")
        udes_.append(ude)
      udes = udes_
    if creationtool is None:
      if elem.get("creationtool") is None:
        raise ValueError(
          "'creationtool' must be provided or the element must have a 'creationtool' attribute"
        )
      creationtool = elem.attrib["creationtool"]
    if creationtoolversion is None:
      if elem.get("creationtoolversion") is None:
        raise ValueError(
          "'creationtoolversion' must be provided or the element must have a 'creationtoolversion' attribute"
        )
      creationtoolversion = elem.attrib["creationtoolversion"]
    if segtype is None:
      if elem.get("segtype") is None:
        raise ValueError(
          "'segtype' must be provided or the element must have a 'segtype' attribute"
        )
      segtype = elem.attrib["segtype"]  # type: ignore
    if tmf is None:
      if elem.get("o-tmf") is None:
        raise ValueError(
          "'tmf' must be provided or the element must have a 'tmf' attribute"
        )
      tmf = elem.attrib["o-tmf"]
    if adminlang is None:
      if elem.get("adminlang") is None:
        raise ValueError(
          "'adminlang' must be provided or the element must have a 'adminlang' attribute"
        )
      adminlang = elem.attrib["adminlang"]
    if srclang is None:
      if elem.get("srclang") is None:
        raise ValueError(
          "'srclang' must be provided or the element must have a 'srclang' attribute"
        )
      srclang = elem.attrib["srclang"]
    if datatype is None:
      if elem.get("datatype") is None:
        raise ValueError(
          "'datatype' must be provided or the element must have a 'datatype' attribute"
        )
      datatype = elem.attrib["datatype"]
    return Header(
      creationtool=creationtool,
      creationtoolversion=creationtoolversion,
      segtype=segtype,  # type: ignore
      tmf=tmf,
      adminlang=adminlang,
      srclang=srclang,
      datatype=datatype,
      encoding=encoding if encoding is not None else attribs.get("o-encoding"),
      creationdate=creationdate
      if creationdate is not None
      else attribs.get("creationdate"),
      creationid=creationid if creationid is not None else attribs.get("creationid"),
      changedate=changedate if changedate is not None else attribs.get("changedate"),
      changeid=changeid if changeid is not None else attribs.get("changeid"),
      props=props,
      notes=notes,
      udes=udes,
    )

  def __attrs_post__init__(self):
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.creationdate = datetime.fromisoformat(self.creationdate)
        except ValueError:
          pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.changedate = datetime.fromisoformat(self.changedate)
        except ValueError:
          pass

  def add_ude(
    self,
    ude: Ude | Iterable[Ude] | None = None,
    *,
    name: str | None = None,
    base: str | None = None,
    maps: Iterable[Map] | None = None,
  ) -> None:
    """
    Appends a :class:`Ude` to the :attr:`udes` attribute of the current
    :class:`Header`.

    .. note::
        The :class:`Ude` object that is added is `always` a new object.
        To add your :class:`Ude` object to the :attr:`udes <Header.udes>` attribute,
        you need to directly append it using notes.append(my_ude).

        .. code-block:: python

            from PythonTmx import Header, Ude

            my_header = Header(
              creationtool="python-tmx",
              creationtoolversion="0.3",
              segtype="block",
              tmf="Microsoft Translator",
              adminlang="en",
              srclang="en",
              datatype="PlainText",
            )
            my_ude = Ude(name="my_ude")
            my_header.add_ude(my_ude)
            my_header.udes.append(my_ude)
            # the header added by add_ude is not the same object as my_ude
            assert my_header.udes[0] is not my_ude
            # the directly appended ude is the same
            assert my_header.udes[1] is my_ude
            # both udes are equal
            assert my_header.udes[0] == my_header.udes[1]

    If an Iterable of :class:`Ude` objects is passed, a new :class:`Ude`
    object is created for each element in the iterable and appended to the
    :attr:`maps <Ude.maps>` attribute of the object.

    if `ude` is None, `unicode` must be specified.

    If both `ude` and any other parameters are specified, the provided
    parameters will take precedence over the values from the :class:`Ude` if
    provided

    If `ude` is an Iterable of :class:`Ude` objects, the provided
    arguments will be applied to each :class:`Ude` object in the iterable.

    Parameters
    ----------
    ude : Ude | Iterable[Ude] | None, optional
        The ude to add to the :class:`Ude` object.
        If None, `unicode` must be provided.
        By default, None.
        For more info see: :class:`Ude`
    name : str, optional
        The name of a element. Its value is not defined by the standard
        By default, None.
        For more info see: :attr:`name <Ude.name>`
    base : str | None, optional
        The encoding upon which the re-mapping of the element is based.
        By default, None.
        For more info see: :attr:`base <Ude.base>`
    maps : Iterable[Map] | None, optional
        An Iterable of :class:`Map` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`maps <Ude.maps>` will be a list of :class:`Map` elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.
        For more info see: :attr:`maps <Ude.maps>` and :class:`Map`.


    Raises
    ------
    TypeError
        If 'ude' is not a :class:`Ude` object, if any of the objects in 'ude' is
        not a :class:`Ude` object (if an Iterable is provided), or if both
        'ude' and 'name' are None.

    Examples
    --------
    .. code-block:: python

        from PythonTmx import Header, Ude, Map

        my_header = Header(
          creationtool="python-tmx",
          creationtoolversion="0.3",
          segtype="block",
          tmf="Microsoft Translator",
          adminlang="en",
          srclang="en",
          datatype="PlainText",
        )
        my_ude = Ude(name="my_ude")
        my_header.add_ude(my_ude, maps=[Map(unicode=str(x)) for x in range(2)])
        print(my_header.udes)
        # Output (formatted for readability):
        # [
        #   Ude(
        #     name="my_ude",
        #     base=None,
        #     maps=[
        #       Map(unicode="0", code=None, ent=None, subst=None),
        #       Map(unicode="1", code=None, ent=None, subst=None),
        #     ],
        #   )
        # ]


    See also
    --------
    :class:`Map`, :class:`Ude`, :class:`Header`, :meth:`add_map <Ude.add_map>`
    """
    if isinstance(ude, Iterable):
      for u in ude:
        self.add_ude(u, name=name, base=base, maps=maps)
      return
    if not isinstance(ude, Ude):
      raise TypeError("ude must be a Ude object")
    elif ude is None:
      if name is None:
        raise ValueError("if 'ude' is None, 'name' must be provided")
      ude_ = Ude(name=name, base=base, maps=[])
    else:
      ude_ = Ude(
        name=name if name is not None else ude.name,
        base=base if base is not None else ude.base,
      )
    if maps is not None:
      if not isinstance(maps, Iterable):
        raise TypeError("maps must be an iterable")
      ude_.add_map(maps)
    self.udes.append(ude_)

  def add_note(self, note=None, *, text=None, lang=None, encoding=None):
    return super().add_note(note, text=text, lang=lang, encoding=encoding)

  def add_prop(self, prop=None, *, text=None, type=None, lang=None, encoding=None):
    return super().add_prop(prop, text=text, type=type, lang=lang, encoding=encoding)

  @staticmethod
  def _to_element(header: Header) -> et._Element:
    attribs = asdict(header, filter=_only_str_int_dt)
    elem = et.Element("header")
    _fill_attributes(elem, attribs)
    for prop in header.props:
      if not isinstance(prop, Prop):
        raise TypeError(f"Expected Prop, got {type(prop)}")
      elem.append(Prop._to_element(prop))
    for note in header.notes:
      if not isinstance(note, Note):
        raise TypeError(f"Expected Note, got {type(note)}")
      elem.append(Note._to_element(note))
    for ude in header.udes:
      if not isinstance(ude, Ude):
        raise TypeError(f"Expected Ude, got {type(ude)}")
      elem.append(Ude._to_element(ude))
    return elem


@define(kw_only=True)
class Bpt(SupportsSub):
  """
  The `bpt <https://www.gala-global.org/tmx-14b#bpt>`_ Element, to delimit the
  beginning of a paired sequence of native codes. Each :class:`Bpt` must have a
  corresponding :class:`Ept` element within their parent element. Can only be
  attached to :class:`Tuv`, :class:`Hi`, :class:`Sub`.
  """

  i: int | str
  """
  Used to pair the :class:`Bpt` with the corresponding :class:`Ept` element.
  Must be unique for each :class:`Bpt` element within the same parent element.
  """
  x: int | str | None = None
  """
  Used to match inline elements :class:`Bpt`, :class:`It`,
  :class:`Ph`, :class:`Hi` and :class:`Ut` elements between the :class:`Tuv`
  of the same :class:`Tu` element.
  Note that an :class:`Ept` element is matched based on x attribute of its
  corresponding :class:`Bpt` element.
  By default None.
  """
  type: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  content: MutableSequence[str | Sub] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Sub` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method.
  By default an empty list.
  """

  def add_sub(self, sub=None, *, type=None, datatype=None, content=None):
    return super().add_sub(sub, type=type, datatype=datatype, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    i: int | str | None = None,
    x: int | str | None = None,
    type: str | None = None,
    content: Iterable[str | Sub] | None = None,
  ) -> Bpt:
    """
    Create a :class:`Bpt` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    i : int | str | None, optional
        Used to pair the :class:`Bpt` with the corresponding :class:`Ept` element.
        Must be unique for each :class:`Bpt` element within the same parent element.
        By default None.
    x : int | str | None, optional
        Used to match inline elements :class:`Bpt`, :class:`It`, :class:`Ph`,
        :class:`Hi` and :class:`Ut` elements between the :class:`Tuv` of the
        same :class:`Tu` element. Note that an :class:`Ept` element is matched
        based on x attribute of its corresponding :class:`Bpt` element.
        By default None.
    type : str | None, optional
        The type of the data contained in the element. By default None.
    content : Iterable[str | Sub] | None, optional
        A Iterable of strings, or :class:`Sub` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Bpt
        A new :class:`Bpt` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'bpt'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element, SubElement
    >>> from PythonTmx.classes import Bpt
    >>> elem = Element("bpt")
    >>> elem.set("i", "1")
    >>> elem.set("x", "1")
    >>> elem.set("type", "x-my-type")
    >>> elem.text = "bpt-text"
    >>> sub = SubElement(elem, "sub", type="x-my-type")
    >>> sub.text = "sub-text"
    >>> bpt = Bpt.from_element(elem)
    >>> print(bpt)
    Bpt(i=1, x=1, type='x-my-type', content=['bpt-text', Sub(type='x-my-type', datatype=None, content=['sub-text'])])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "bpt":
      raise ValueError(f"Expected <bpt> element, got {str(elem.tag)}")
    if i is None:
      if elem.get("i") is None:
        raise ValueError(
          "'i' must be provided or the element must have a 'i' attribute"
        )
      i = elem.attrib["i"]
    if content is None:
      content = _parse_inline(elem, mask=("sub",))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Sub, str)):
          raise TypeError(f"Expected Sub, got {type(e)}")
        content_.append(e)
      content = content_
    return Bpt(
      i=i,
      x=x if x is not None else elem.get("x"),
      type=type if type is not None else elem.get("type"),
      content=content,
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

  @staticmethod
  def _to_element(bpt: Bpt) -> et._Element:
    attribs = asdict(bpt, filter=_only_str_int_dt)
    elem = et.Element("bpt")
    _fill_attributes(elem, attribs)
    _to_element_inline(elem, bpt.content, ("sub",))
    return elem


@define(kw_only=True)
class Ept(SupportsSub):
  """
  The `ept <https://www.gala-global.org/tmx-14b#ept>`_ Element, to delimit the
  end of a paired sequence of native codes. Each :class:`Ept` must have a
  corresponding :class:`Bpt` element within their parent element. Can only be attached to
  :class:`Tuv`, :class:`Hi`, :class:`Sub`.
  """

  i: int | str
  """
  Used to pair the :class:`Bpt` with the corresponding :class:`Ept` element.
  Must be unique for each :class:`Bpt` element within the same parent element.
  """
  content: MutableSequence[str | Sub] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Sub` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method.
  By default an empty list.
  """

  def add_sub(self, sub=None, *, type=None, datatype=None, content=None):
    return super().add_sub(sub, type=type, datatype=datatype, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    i: int | str | None = None,
    content: Iterable[str | Sub] | None = None,
  ) -> Ept:
    """
    Create a :class:`Ept` Element from an XmlElement.


    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    i : int | str | None, optional
        Used to pair the :class:`Bpt` with the corresponding :class:`Ept`
        element. Must be unique for each :class:`Bpt` element within the same
        parent element. By default None.
    content : Iterable[str | Sub] | None, optional
        A Iterable of strings, or :class:`Sub` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Ept
        A new :class:`Ept` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'ept'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element, SubElement
    >>> from PythonTmx.classes import Ept
    >>> elem = Element("ept")
    >>> elem.set("i", "1")
    >>> elem.text = "ept-text"
    >>> sub = SubElement(elem, "sub", type="x-my-type")
    >>> sub.text = "sub-text"
    >>> ept = Ept.from_element(elem)
    >>> print(ept)
    Ept(i=1, content=['ept-text', Sub(type='x-my-type', datatype=None, content=['sub-text'])])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "ept":
      raise ValueError(f"Expected <ept> element, got {str(elem.tag)}")
    if i is None:
      if elem.get("i") is None:
        raise ValueError(
          "'i' must be provided or the element must have a 'i' attribute"
        )
      i = elem.attrib["i"]
    if content is None:
      content = _parse_inline(elem, mask=("sub",))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Sub, str)):
          raise TypeError(f"Expected Sub, got {type(e)}")
        content_.append(e)
      content = content_
    return Ept(
      i=i,
      content=content,
    )

  def __attrs_post_init__(self):
    if self.i is not None and not isinstance(self.i, int):
      try:
        self.i = int(self.i)
      except (TypeError, ValueError):
        pass

  @staticmethod
  def _to_element(ept: Ept) -> et._Element:
    attribs = asdict(ept, filter=_only_str_int_dt)
    elem = et.Element("ept")
    _fill_attributes(elem, attribs)
    _to_element_inline(elem, ept.content, ("sub",))
    return elem


@define(kw_only=True)
class Hi(SupportsInlineNoSub):
  """
  The `hi <https://www.gala-global.org/tmx-14b#hi>`_ Element, used to delimit
  a section of text that has special meaning, such as a terminological unit, a
  proper name, an item that should not be modified, etc. Can only be attached to
  :class:`Tuv`, :class:`Bpt`, :class:`Ept`, :class:`It`, :class:`Ph`, :class:`Hi`,
  :class:`Ut`.
  """

  x: int | str | None = None
  """
  Used to match inline elements :class:`Bpt`, :class:`It`,
  :class:`Ph`, :class:`Hi` and :class:`Ut` elements between the :class:`Tuv`
  of the same :class:`Tu` element.
  Note that an :class:`Ept` element is matched based on x attribute of its
  corresponding :class:`Bpt` element.
  By default None.
  """
  type: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
  :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append``.
  By default an empty list.
  """

  def add_bpt(self, bpt=None, *, content=None, i=None, x=None, type=None):
    return super().add_bpt(bpt, content=content, i=i, x=x, type=type)

  def add_ept(self, ept=None, *, content=None, i=None):
    return super().add_ept(ept, content=content, i=i)

  def add_hi(self, hi=None, *, type=None, x=None, content=None):
    return super().add_hi(hi, type=type, x=x, content=content)

  def add_it(self, it=None, *, content=None, pos=None, x=None, type=None):
    return super().add_it(it, content=content, pos=pos, x=x, type=type)

  def add_ph(self, ph=None, *, content=None, i=None, x=None, assoc=None):
    return super().add_ph(ph, content=content, i=i, x=x, assoc=assoc)

  def add_ut(self, ut=None, *, x=None, content=None):
    return super().add_ut(ut, x=x, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    x: int | str | None = None,
    type: str | None = None,
    content: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> Hi:
    """
    Create a :class:`Hi` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    x : int | str | None, optional
        Used to match inline elements :class:`Bpt`, :class:`It`, :class:`Ph`,
        :class:`Hi` and :class:`Ut` elements between the :class:`Tuv` of the
        same :class:`Tu` element. Note that an :class:`Ept` element is matched
        based on x attribute of its corresponding :class:`Bpt` element.
        By default None.
    type : str | None, optional
        The type of the data contained in the element. By default None.
    content : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None, optional
        A Iterable of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
        :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Hi
        A new :class:`Hi` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'hi'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Hi
    >>> elem = Element("hi")
    >>> elem.set("x", "1")
    >>> elem.set("type", "x-my-type")
    >>> elem.text = "hi-text"
    >>> hi = Hi.from_element(elem)
    >>> print(hi)
    Hi(x=1, type='x-my-type', content=['hi-text'])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "hi":
      raise ValueError(f"Expected <hi> element, got {str(elem.tag)}")
    if content is None:
      content = _parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut"))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Bpt, Ept, It, Ph, Hi, Ut, str)):
          raise TypeError(f"Expected Bpt, Ept, It, Ph, Hi, Ut or str, got {type(e)}")
        content_.append(e)
      content = content_
    return Hi(
      x=x if x is not None else elem.get("x"),
      type=type if type is not None else elem.get("type"),
      content=content,
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass

  @staticmethod
  def _to_element(hi: Hi) -> et._Element:
    attribs = asdict(hi, filter=_only_str_int_dt)
    elem = et.Element("hi")
    _fill_attributes(elem, attribs)
    _to_element_inline(
      elem,
      hi.content,
      (
        "bpt",
        "ept",
        "it",
        "ph",
        "hi",
        "ut",
      ),
    )
    return elem


@define(kw_only=True)
class It(SupportsSub):
  """
  The `it <https://www.gala-global.org/tmx-14b#it>`_ Element, used to delimit
  a beginning/ending sequence of native codes that does not have its
  corresponding ending/beginning within the segment.
  """

  pos: Literal["begin", "end"]
  """
  The position of the element. Must be "begin" or "end".
  """
  x: int | str | None = None
  """
  Used to match inline elements :class:`Bpt`, :class:`It`,
  :class:`Ph`, :class:`Hi` and :class:`Ut` elements between the :class:`Tuv`
  of the same :class:`Tu` element.
  Note that an :class:`Ept` element is matched based on x attribute of its
  corresponding :class:`Bpt` element.
  By default None.
  """
  type: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  content: MutableSequence[str | Sub] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Sub` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method.
  By default an empty list.
  """

  def add_sub(self, sub=None, *, type=None, datatype=None, content=None):
    return super().add_sub(sub, type=type, datatype=datatype, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    pos: Literal["begin", "end"] | None = None,
    x: int | str | None = None,
    type: str | None = None,
    content: Iterable[str | Sub] | None = None,
  ) -> It:
    """
    Create a :class:`It` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    pos : Literal["begin", "end"]
        The position of the element. Must be "begin" or "end".
    x : int | str | None, optional
        Used to match inline elements :class:`Bpt`, :class:`It`, :class:`Ph`,
        :class:`Hi` and :class:`Ut` elements between the :class:`Tuv` of the
        same :class:`Tu` element. Note that an :class:`Ept` element is matched
        based on x attribute of its corresponding :class:`Bpt` element.
        By default None.
    type : str | None, optional
        The type of the data contained in the element. By default None.
    content : Iterable[str | Sub] | None, optional
        A Iterable of strings, or :class:`Sub` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    It
        A new :class:`It` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'it'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import It
    >>> elem = Element("it")
    >>> elem.set("pos", "begin")
    >>> elem.set("x", "1")
    >>> elem.set("type", "x-my-type")
    >>> elem.text = "it-text"
    >>> it = It.from_element(elem)
    >>> print(it)
    It(pos='begin', x=1, type='x-my-type', content=['it-text'])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "it":
      raise ValueError(f"Expected <it> element, got {str(elem.tag)}")
    if pos is None:
      if elem.get("pos") is None:
        raise ValueError(
          "'pos' must be provided or the element must have a 'pos' attribute"
        )
      pos = elem.attrib["pos"]  # type: ignore
    if content is None:
      content = _parse_inline(elem, mask=("sub",))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Sub, str)):
          raise TypeError(f"Expected Sub, got {type(e)}")
        content_.append(e)
      content = content_
    return It(
      pos=pos,  # type: ignore
      x=x if x is not None else elem.get("x"),
      type=type if type is not None else elem.get("type"),
      content=content,
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass

  @staticmethod
  def _to_element(it: It) -> et._Element:
    attribs = asdict(it, filter=_only_str_int_dt)
    elem = et.Element("it")
    _fill_attributes(elem, attribs)
    _to_element_inline(elem, it.content, ("sub",))
    return elem


@define(kw_only=True)
class Ph(SupportsSub):
  """
  The `ph <https://www.gala-global.org/tmx-14b#ph>`_ Element, used to delimit
  a sequence of native standalone codes in the segment
  """

  i: int | str | None = None
  """
  Used to pair the :class:`Bpt` with the corresponding :class:`Ept` element.
  Must be unique for each :class:`Bpt` element within the same parent element.
  """
  x: int | str | None = None
  """
  Used to match inline elements :class:`Bpt`, :class:`It`,
  :class:`Ph`, :class:`Hi` and :class:`Ut` elements between the :class:`Tuv`
  of the same :class:`Tu` element.
  Note that an :class:`Ept` element is matched based on x attribute of its
  corresponding :class:`Bpt` element.
  By default None.
  """
  assoc: Literal["p", "f", "b"] | None = None
  """
  The association of the element. Must be "p", "f" or "b".
  """
  content: MutableSequence[str | Sub] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Sub` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method.
  By default an empty list.
  """

  def add_sub(self, sub=None, *, type=None, datatype=None, content=None):
    return super().add_sub(sub, type=type, datatype=datatype, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    x: int | str | None = None,
    assoc: Literal["p", "f", "b"] | None = None,
    content: Iterable[str | Sub] | None = None,
  ) -> Ph:
    """
    Create a :class:`Ph` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    x : int | str | None, optional
        Used to match inline elements :class:`Bpt`, :class:`It`, :class:`Ph`,
        :class:`Hi` and :class:`Ut` elements between the :class:`Tuv` of the
        same :class:`Tu` element. Note that an :class:`Ept` element is matched
        based on x attribute of its corresponding :class:`Bpt` element.
        By default None.
    assoc : Literal["p", "f", "b"] | None, optional
        The association of the element. Must be "p", "f" or "b".
        By default None.
    content : Iterable[str | Sub] | None, optional
        A Iterable of strings, or :class:`Sub` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Ph
        A new :class:`Ph` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'ph'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Ph
    >>> elem = Element("ph")
    >>> elem.set("x", "1")
    >>> elem.set("assoc", "p")
    >>> elem.text = "ph-text"
    >>> ph = Ph.from_element(elem)
    >>> print(ph)
    Ph(i=None, x=1, assoc='p', content=['ph-text'])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "ph":
      raise ValueError(f"Expected <ph> element, got {str(elem.tag)}")
    if content is None:
      content = _parse_inline(elem, mask=("sub",))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Sub, str)):
          raise TypeError(f"Expected Sub, got {type(e)}")
        content_.append(e)
      content = content_
    return Ph(
      x=x if x is not None else elem.get("x"),
      assoc=assoc if assoc is not None else elem.get("assoc"),  # type: ignore
      content=content,
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

  @staticmethod
  def _to_element(ph: Ph) -> et._Element:
    attribs = asdict(ph, filter=_only_str_int_dt)
    elem = et.Element("ph")
    _fill_attributes(elem, attribs)
    _to_element_inline(elem, ph.content, ("sub",))
    return elem


@define(kw_only=True)
class Sub(SupportsInlineNoSub):
  type: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  datatype: str | None = None
  """
  The data type of the element. By default None.
  """
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
  :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append``.
  By default an empty list. 
  """

  def add_bpt(self, bpt=None, *, content=None, i=None, x=None, type=None):
    return super().add_bpt(bpt, content=content, i=i, x=x, type=type)

  def add_ept(self, ept=None, *, content=None, i=None):
    return super().add_ept(ept, content=content, i=i)

  def add_hi(self, hi=None, *, type=None, x=None, content=None):
    return super().add_hi(hi, type=type, x=x, content=content)

  def add_it(self, it=None, *, content=None, pos=None, x=None, type=None):
    return super().add_it(it, content=content, pos=pos, x=x, type=type)

  def add_ph(self, ph=None, *, content=None, i=None, x=None, assoc=None):
    return super().add_ph(ph, content=content, i=i, x=x, assoc=assoc)

  def add_ut(self, ut=None, *, x=None, content=None):
    return super().add_ut(ut, x=x, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    type: str | None = None,
    datatype: str | None = None,
    content: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
  ) -> Sub:
    """
    Create a :class:`Sub` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    type : str | None, optional
        The type of the data contained in the element. By default None.
    datatype : str | None, optional
        The data type of the element. By default None.
    content : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None, optional
        A Iterable of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
        :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Sub
        A new :class:`Sub` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If the element's tag is not 'sub'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Sub
    >>> elem = Element("sub")
    >>> elem.set("type", "x-my-type")
    >>> elem.set("datatype", "x-my-type")
    >>> elem.text = "sub-text"
    >>> sub = Sub.from_element(elem)
    >>> print(sub)
    Sub(type='x-my-type', datatype='x-my-type', content=['sub-text'])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "sub":
      raise ValueError(f"Expected <sub> element, got {str(elem.tag)}")
    if content is None:
      content = _parse_inline(elem, mask=("bpt", "ept", "it", "ph", "hi", "ut"))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Bpt, Ept, It, Ph, Hi, Ut, str)):
          raise TypeError(f"Expected Bpt, Ept, It, Ph, Hi, Ut or str, got {type(e)}")
        content_.append(e)
      content = content_
    return Sub(
      type=type if type is not None else elem.get("type"),
      datatype=datatype if datatype is not None else elem.get("datatype"),
      content=content,
    )

  @staticmethod
  def _to_element(sub: Sub) -> et._Element:
    attribs = asdict(sub, filter=_only_str_int_dt)
    elem = et.Element("sub")
    _fill_attributes(elem, attribs)
    _to_element_inline(
      elem,
      sub.content,
      (
        "bpt",
        "ept",
        "it",
        "ph",
        "hi",
        "ut",
      ),
    )
    return elem


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@define(kw_only=True)
class Ut(SupportsSub):
  """
  The `ut <https://www.gala-global.org/tmx-14b#ut>`_ Element, used to delimit
  a sequence of native unknown codes in the segment.
  This element has been DEPRECATED. Use the guidelines outlined in the `Rules
  for Inline Elements <https://www.gala-global.org/tmx-14b#ContentMarkup_Rules>`_
  section of the Tmx standard to choose which inline
  element to used instead of Ut.
  """

  x: int | str | None = None
  """
  Used to match inline elements :class:`Bpt`, :class:`It`,
  :class:`Ph`, :class:`Hi` and :class:`Ut` elements between the :class:`Tuv`
  of the same :class:`Tu` element.
  Note that an :class:`Ept` element is matched based on x attribute of its
  corresponding :class:`Bpt` element.
  By default None.
  """
  content: MutableSequence[str | Sub] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Sub` elements. While any iterable
  (or even a Generator expression) can technically be used, it is recommended to
  use a list or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append``.
  By default an empty list.  
  """

  def add_sub(self, sub=None, *, type=None, datatype=None, content=None):
    return super().add_sub(sub, type=type, datatype=datatype, content=content)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    x: int | str | None = None,
    content: Iterable[str | Sub] | None = None,
  ) -> Ut:
    """
    Create a :class:`Ut` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    x : int | str | None, optional
        Used to match inline elements :class:`Bpt`, :class:`It`, :class:`Ph`,
        :class:`Hi` and :class:`Ut` elements between the :class:`Tuv` of the
        same :class:`Tu` element. Note that an :class:`Ept` element is matched
        based on x attribute of its corresponding :class:`Bpt` element.
        By default None.
    content : Iterable[str | Sub] | None, optional
        A Iterable of strings, or :class:`Sub` elements. While any iterable
        (or even a Generator expression) can technically be used, the resulting
        element :attr:`content` will be a list of made of the provided elements.
        If the Iterable does not preserve insertion order, the order of the
        resulting list cannot be guaranteed. By default an empty list.

    Returns
    -------
    Ut
        A new :class:`Ut` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If any of the attributes is not provided and the element does not have
        all of the required attributes, or the element's tag is not 'ut'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Ut
    >>> elem = Element("ut")
    >>> elem.set("x", "1")
    >>> elem.text = "ut-text"
    >>> ut = Ut.from_element(elem)
    >>> print(ut)
    Ut(x=1, content=['ut-text'])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "ut":
      raise ValueError(f"Expected <ut> element, got {str(elem.tag)}")
    if content is None:
      content = _parse_inline(elem, mask=("sub",))
    else:
      content_ = []
      for e in content:
        if not isinstance(e, (Sub, str)):
          raise TypeError(f"Expected Sub, got {type(e)}")
        content_.append(e)
      content = content_
    return Ut(
      x=x if x is not None else elem.get("x"),
      content=content,
    )

  def __attrs_post_init__(self):
    if self.x is not None and not isinstance(self.x, int):
      try:
        self.x = int(self.x)
      except (TypeError, ValueError):
        pass

  @staticmethod
  def _to_element(ut: Ut) -> et._Element:
    attribs = asdict(ut, filter=_only_str_int_dt)
    elem = et.Element("ut")
    _fill_attributes(elem, attribs)
    _to_element_inline(elem, ut.content, ("sub"))
    return elem


@define(kw_only=True)
class Tuv(SupportsNotesAndProps):
  """
  The `tuv <https://www.gala-global.org/tmx-14b#tuv>`_ Element, used to specify
  the translation of a segment of text in a :class:`Tu` Element.
  Can only be attached to :class:`Tu`.
  """

  segment: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    factory=list,
    validator=validators.deep_iterable(
      validators.instance_of((str, Bpt, Ept, It, Ph, Hi, Ut))
    ),
  )
  """
  A MutableSequence of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
  :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method.
  By default an empty list.
  """
  lang: str = field(validator=validators.instance_of(str))
  """
  The language of the segment. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
  """
  encoding: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  datatype: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The type of the data contained in the element. By default None.
  """
  usagecount: str | int | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(int))
    ),
  )
  """
  The number of times the element has been used. By default None.
  """
  lastusagedate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the element was last used. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationtool: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The tool that created the element. By default None.
  """
  creationtoolversion: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The version of the tool that created the element. By default None.
  """
  creationdate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the element was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that created the element, by default None 
  """
  changedate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the element was last changed. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  changeid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that last changed the element, by default None
  """
  tmf: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The format of the translation memory file from which the element has been
  generated. By default None.
  """
  notes: MutableSequence[Note] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Note)),
  )
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_note` function will be used.
  """
  props: MutableSequence[Prop] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Prop)),
  )
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_prop` function will be used.
  """

  def add_note(self, note=None, *, text=None, lang=None, encoding=None):
    return super().add_note(note, text=text, lang=lang, encoding=encoding)

  def add_prop(self, prop=None, *, text=None, type=None, lang=None, encoding=None):
    return super().add_prop(prop, text=text, type=type, lang=lang, encoding=encoding)

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    lang: str | None = None,
    segment: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
    encoding: str | None = None,
    datatype: str | None = None,
    usagecount: str | int | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    props: Iterable[Prop] | None = None,
    notes: Iterable[Note] | None = None,
  ) -> Tuv:
    """
    Create a :class:`Tuv` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse..
    segment : Iterable[str  |  Bpt  |  Ept  |  It  |  Ph  |  Hi  |  Ut] | None, optional
        Any Iterable of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`, :class:`Ph`,
        :class:`Hi`, :class:`Ut` elements. While any iterable (or even a Generator expression)
        can technically be used, the resulting element :attr:`segment` will be a list of
        made of the provided elements. If the Iterable does not preserve
        insertion order, the order of the resulting list cannot be guaranteed.
        By default an empty list.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set. Ideally one of the
        `IANA recommended charsets
        <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
        By default None.
    datatype : str | None, optional
        The data type of the element. By default None.
    usagecount : str | int | None, optional
        The number of times the element has been used. By default None.
    lastusagedate : str | datetime | None, optional
        The date and time the element was last used. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    creationtool : str | None, optional
        The tool that created the TMX document.
    creationtoolversion : str | None, optional
        The version of the tool that created the TMX document.
    creationdate : str | datetime | None, optional
        The date and time the element was created. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    creationid : str | None, optional
        The ID of the user that created the element, by default None
    changedate : str | datetime | None, optional
        The date and time the element was last changed. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time
        zone offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    changeid : str | None, optional
        The ID of the user that last changed the element, by default None
    tmf : str | None, optional
        The format of the translation memory file from which the element has
        been generated. By default None.
    props : Iterable[Prop] | None, optional
        A Iterable of :class:`Prop` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`props` will be a list of :class:`Prop` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or if 'segment' contains an element that
        is not a :class:`Bpt`, :class:`Ept`, :class:`It`, :class:`Ph`, :class:`Hi`
        or :class:`Ut`.
    ValueError
        If the element's tag is not 'tuvs'.

    Examples
    --------
    >>> from PythonTmx.classes import Tuv
    >>> from xml.etree.ElementTree import Element, SubElement
    >>> elem = Element("tuv")
    >>> elem.set("o-encoding", "utf-8")
    >>> elem.set("datatype", "x-my-type")
    >>> elem.set("usagecount", "10")
    >>> elem.set("lastusagedate", "20240101T000000Z")
    >>> elem.set("creationtool", "tool")
    >>> elem.set("creationtoolversion", "1.0")
    >>> elem.set("creationdate", "20240101T000000Z")
    >>> elem.set("creationid", "user")
    >>> elem.set("changedate", "20240101T000000Z")
    >>> elem.set("changeid", "user")
    >>> elem.set("o-tmf", "tmx")
    >>> prop = SubElement(elem, "prop", type="x-prop-type")
    >>> prop.text = "prop-text"
    >>> note = SubElement(elem, "note", lang="en")
    >>> note.text = "note-text"
    >>> seg = SubElement(elem, "seg")
    >>> seg.text = "seg-text"
    >>> bpt = SubElement(seg, "bpt", i="1")
    >>> bpt.text = "bpt-text"
    >>> bpt.tail = "in-between bpt and ept"
    >>> ept = SubElement(seg, "ept", i="1")
    >>> ept.text = "ept-text"
    >>> ept.tail = "after ept"
    >>> tuv = Tuv.from_element(elem)
    >>> print(tuv)
    Tuv(segment=['seg-text', Bpt(i=1, x=None, type=None, content=[]), 'in-between bpt and ept', Ept(i=1, content=[]), 'after ept', 'seg-text', Bpt(i=1, x=None, type=None, content=[]), 'in-between bpt and ept', Ept(i=1, content=[]), 'after ept'], encoding='utf-8', datatype='x-my-type', usagecount=10, lastusagedate=datetime.datetime(2024, 1, 1, 0, 0), creationtool='tool', creationtoolversion='1.0', creationdate=datetime.datetime(2024, 1, 1, 0, 0), creationid='user', changedate=datetime.datetime(2024, 1, 1, 0, 0), changeid='user', tmf='tmx', notes=[Note(text='note-text', lang=None, encoding=None)], props=[Prop(text='prop-text', type='x-prop-type', lang=None, encoding=None)])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "tuv":
      raise ValueError(f"Expected <tuv> element, got {str(elem.tag)}")
    if lang is None:
      if elem.get("{http://www.w3.org/XML/1998/namespace}lang") is None:
        raise ValueError(
          "'lang' must be provided or the element must have a 'xml:lang' attribute"
        )
      lang = elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
    if segment is None:
      if (seg := elem.find("seg")) is None:
        segment = []
      else:
        segment = _parse_inline(seg, mask=("bpt", "ept", "it", "ph", "hi", "ut"))
    else:
      segment_ = []
      for e in segment:
        if not isinstance(e, (Bpt, Ept, It, Ph, Hi, Ut, str)):
          raise TypeError(f"Expected Bpt, Ept, It, Ph, Hi, Ut or str, got {type(e)}")
        segment_.append(e)
      segment = segment_
    if props is None:
      props = [Prop._from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note._from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    return Tuv(
      segment=segment,
      lang=lang,
      encoding=encoding if encoding is not None else elem.get("o-encoding"),
      datatype=datatype if datatype is not None else elem.get("datatype"),
      usagecount=usagecount if usagecount is not None else elem.get("usagecount"),
      lastusagedate=lastusagedate
      if lastusagedate is not None
      else elem.get("lastusagedate"),
      creationtool=creationtool
      if creationtool is not None
      else elem.get("creationtool"),
      creationtoolversion=creationtoolversion
      if creationtoolversion is not None
      else elem.get("creationtoolversion"),
      creationdate=creationdate
      if creationdate is not None
      else elem.get("creationdate"),
      creationid=creationid if creationid is not None else elem.get("creationid"),
      changedate=changedate if changedate is not None else elem.get("changedate"),
      changeid=changeid if changeid is not None else elem.get("changeid"),
      tmf=tmf if tmf is not None else elem.get("o-tmf"),
      props=props,
      notes=notes,
    )

  @staticmethod
  def _to_element(tuv: Tuv) -> et._Element:
    attribs = asdict(tuv, filter=_only_str_int_dt)
    elem = et.Element("tuv")
    _fill_attributes(elem, attribs)
    for note in tuv.notes:
      if not isinstance(note, Note):
        raise TypeError(f"Expected Note, got {type(note)}")
      elem.append(Note._to_element(note))
    for prop in tuv.props:
      if not isinstance(prop, Prop):
        raise TypeError(f"Expected Prop, got {type(prop)}")
      elem.append(Prop._to_element(prop))
    seg = et.SubElement(elem, "seg")
    seg.text = ""
    _to_element_inline(seg, tuv.segment, ("bpt", "ept", "it", "ph", "hi", "ut"))
    return elem

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.lastusagedate = datetime.fromisoformat(self.lastusagedate)
        except ValueError:
          pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.creationdate = datetime.fromisoformat(self.creationdate)
        except ValueError:
          pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.changedate = datetime.fromisoformat(self.changedate)
        except ValueError:
          pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass


@define(kw_only=True)
class Tu(SupportsNotesAndProps):
  """
  The `tu <https://www.gala-global.org/tmx-14b#tu>`_ Element, used to contain
  the data for a given translation unit. Can only be attached to :class:`Tmx`.
  """

  tuid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the translation unit. Its value is not defined by the standard.
  Must be a str without spaces.
  """
  encoding: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  datatype: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The type of the data contained in the element. By default None.
  """
  usagecount: str | int | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(int))
    ),
  )
  """
  The number of times the element has been used. By default None.
  """
  lastusagedate: str | datetime | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The date and time the element was last used. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationtool: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The tool that created the element. By default None.
  """
  creationtoolversion: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The version of the tool that created the element. By default None.
  """
  creationdate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the element was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that created the element, by default None
  """
  changedate: str | datetime | None = field(
    default=None,
    validator=validators.optional(
      validators.or_(validators.instance_of(str), validators.instance_of(datetime))
    ),
  )
  """
  The date and time the element was last changed. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None
  """
  The type of segmentation used in the element. By default None.
  """
  changeid: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The ID of the user that last changed the element, by default None
  """
  tmf: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The format of the translation memory file from which the element has been
  generated. By default None.
  """
  srclang: str | None = field(
    default=None,
    validator=validators.optional(validators.instance_of(str)),
  )
  """
  The source language of the element. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for srclang are not case-sensitive.
  """
  tuvs: MutableSequence[Tuv] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Tuv)),
  )
  """
  A MutableSequence of :class:`Tuv` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements. At the very
  least, the container should support the ``append`` method if the
  :meth:`add_tuv` function will be used.
  """
  notes: MutableSequence[Note] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Note)),
  )
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_note` function will be used.
  """
  props: MutableSequence[Prop] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Prop)),
  )
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :meth:`add_prop` function will be used.
  """

  @staticmethod
  def _from_element(
    elem: XmlElement,
    *,
    tuid: str | None = None,
    encoding: str | None = None,
    datatype: str | None = None,
    usagecount: str | int | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    srclang: str | None = None,
    props: Iterable[Prop] | None = None,
    notes: Iterable[Note] | None = None,
    tuvs: Iterable[Tuv] | None = None,
  ) -> Tu:
    """
    Create a :class:`Tu` Element from an XmlElement.

    Parameters
    ----------
    elem : :external:class:`lxml.etree._Element` | :external:class:`xml.etree.ElementTree.Element`
        The Element to parse.
    tuid : str | None, optional
        The ID of the translation unit. Its value is not defined by the standard.
        Must be a str without spaces. By default None.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case it
        is to be re-encoded in a non-Unicode code set. Ideally one of the `IANA
        recommended charsets
        <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
        By default None.
    datatype : str | None, optional
        The type of the data contained in the element. By default None.
    usagecount : str | int | None, optional
        The number of times the element has been used. By default None.
    lastusagedate : str | datetime | None, optional
        The date and time the element was last used. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    creationtool : str | None, optional
        The tool that created the element. By default None.
    creationtoolversion : str | None, optional
        The version of the tool that created the element. By default None.
    creationdate : str | datetime | None, optional
        The date and time the element was created. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    creationid : str | None, optional
        The ID of the user that created the element, by default None
    changedate : str | datetime | None, optional
        The date and time the element was last changed. It is recommended to use
        :external:class:`datetime.datetime` objects instead of raw strings.
        If a string is provided, it will be parsed as a
        :external:class:`datetime.datetime` object if it matches the format
        YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone
        offset, and the date/time is in Coordinated Universal Time (UTC).
        By default None.
    changeid : str | None, optional
        The ID of the user that last changed the element, by default None
    tmf : str | None, optional
        The format of the translation memory file from which the element has been
        generated. By default None.
    srclang : str | None, optional
        The source language of the element. Ideally a language code as described
        in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the
        other TMX attributes, the values for srclang are not case-sensitive.
    props : Iterable[Prop] | None, optional
        A Iterable of :class:`Prop` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`props` will be a list of :class:`Prop` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    tuvs : Iterable[Tuv] | None, optional
        A Iterable of :class:`Tuv` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`tuvs <Tu.tuvs>` will be a list of :class:`Tuv` elements. If the Iterable
        does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.

    Returns
    -------
    Tu
        A new :class:`Tu` Object with the provided values

    Raises
    ------
    TypeError
        If `elem` is not an XmlElement, or any of the attributes is not a string.
    ValueError
        If the element's tag is not 'tu'.

    Examples
    --------

    >>> from xml.etree.ElementTree import Element
    >>> from PythonTmx.classes import Tu, Prop, Note, Tuv, Bpt
    >>> from datetime import datetime
    >>> elem = Element("tu")
    >>> elem.set("tuid", "tuid")
    >>> elem.set("o-encoding", "utf-8")
    >>> elem.set("datatype", "x-my-type")
    >>> elem.set("usagecount", "10")
    >>> elem.set("lastusagedate", "20240101T000000Z")
    >>> elem.set("creationtool", "tool")
    >>> elem.set("creationtoolversion", "1.0")
    >>> elem.set("creationdate", "20240101T000000Z")
    >>> elem.set("creationid", "user")
    >>> elem.set("changedate", "20240101T000000Z")
    >>> elem.set("changeid", "user")
    >>> props = [Prop(text="prop-text", type="x-prop-type")]
    >>> notes = [Note(text="note-text", lang="en")]
    >>> tuvs = [
    ...   Tuv(
    ...     segment=["seg-text", Bpt(i=1, x=1, type="x-my-type", content=["bpt-text"])],
    ...     encoding="utf-8",
    ...     datatype="x-my-type",
    ...     usagecount=10,
    ...     lastusagedate=datetime(2024, 1, 1, 0, 0),
    ...     creationtool="tool",
    ...     creationtoolversion="1.0",
    ...     creationdate=datetime(2024, 1, 1, 0, 0),
    ...     creationid="user",
    ...     changedate=datetime(2024, 1, 1, 0, 0),
    ...     changeid="user",
    ...     tmf="tmx",
    ...   )
    ... ]
    >>> tu = Tu.from_element(elem, tuvs=tuvs, props=props, notes=notes)
    >>> print(tu)
    Tu(tuid='tuid', encoding='utf-8', datatype='x-my-type', usagecount=10, lastusagedate=datetime.datetime(2024, 1, 1, 0, 0), creationtool='tool', creationtoolversion='1.0', creationdate=datetime.datetime(2024, 1, 1, 0, 0), creationid='user', changedate=datetime.datetime(2024, 1, 1, 0, 0), segtype=None, changeid='user', tmf=None, srclang=None, tuvs=[Tuv(segment=['seg-text', Bpt(i=1, x=1, type='x-my-type', content=['bpt-text'])], encoding='utf-8', datatype='x-my-type', usagecount=10, lastusagedate=datetime.datetime(2024, 1, 1, 0, 0), creationtool='tool', creationtoolversion='1.0', creationdate=datetime.datetime(2024, 1, 1, 0, 0), creationid='user', changedate=datetime.datetime(2024, 1, 1, 0, 0), changeid='user', tmf='tmx', notes=[], props=[])], notes=[Note(text='note-text', lang='en', encoding=None)], props=[Prop(text='prop-text', type='x-prop-type', lang=None, encoding=None)])
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "tu":
      raise ValueError(f"Expected <tu> element, got {str(elem.tag)}")
    attribs = elem.attrib
    if props is None:
      props = [Prop._from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note._from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    if tuvs is None:
      tuvs = [Tuv._from_element(e) for e in elem if e.tag == "tuv"]
    else:
      tuvs_ = []
      for tuv in tuvs:
        if not isinstance(tuv, Tuv):
          raise TypeError(f"Expected Tuv, got {type(tuv)}")
        tuvs_.append(tuv)
      tuvs = tuvs_
    return Tu(
      tuid=tuid if tuid is not None else attribs.get("tuid"),
      encoding=encoding if encoding is not None else attribs.get("o-encoding"),
      datatype=datatype if datatype is not None else attribs.get("datatype"),
      usagecount=usagecount if usagecount is not None else attribs.get("usagecount"),
      lastusagedate=lastusagedate
      if lastusagedate is not None
      else attribs.get("lastusagedate"),
      creationtool=creationtool
      if creationtool is not None
      else attribs.get("creationtool"),
      creationtoolversion=creationtoolversion
      if creationtoolversion is not None
      else attribs.get("creationtoolversion"),
      creationdate=creationdate
      if creationdate is not None
      else attribs.get("creationdate"),
      creationid=creationid if creationid is not None else attribs.get("creationid"),
      changedate=changedate if changedate is not None else attribs.get("changedate"),
      changeid=changeid if changeid is not None else attribs.get("changeid"),
      tmf=tmf if tmf is not None else attribs.get("o-tmf"),
      srclang=srclang if srclang is not None else attribs.get("srclang"),
      props=props,
      notes=notes,
      tuvs=tuvs,
    )

  @staticmethod
  def _to_element(tu: Tu) -> et._Element:
    attribs = asdict(tu, filter=_only_str_int_dt)
    elem = et.Element("tu")
    _fill_attributes(elem, attribs)
    for note in tu.notes:
      if not isinstance(note, Note):
        raise TypeError(f"Expected Note, got {type(note)}")
      elem.append(Note._to_element(note))
    for prop in tu.props:
      if not isinstance(prop, Prop):
        raise TypeError(f"Expected Prop, got {type(prop)}")
      elem.append(Prop._to_element(prop))
    for tuv in tu.tuvs:
      if not isinstance(tuv, Tuv):
        raise TypeError(f"Expected Tuv, got {type(tuv)}")
      elem.append(Tuv._to_element(tuv))
    return elem

  def __attrs_post_init__(self):
    if self.lastusagedate is not None and not isinstance(self.lastusagedate, datetime):
      try:
        self.lastusagedate = datetime.strptime(self.lastusagedate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.lastusagedate = datetime.fromisoformat(self.lastusagedate)
        except ValueError:
          pass
    if self.creationdate is not None and not isinstance(self.creationdate, datetime):
      try:
        self.creationdate = datetime.strptime(self.creationdate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.creationdate = datetime.fromisoformat(self.creationdate)
        except ValueError:
          pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except TypeError:
        pass
      except ValueError:
        try:
          self.changedate = datetime.fromisoformat(self.changedate)
        except ValueError:
          pass
    if self.usagecount is not None and not isinstance(self.usagecount, int):
      try:
        self.usagecount = int(self.usagecount)
      except (TypeError, ValueError):
        pass

  def add_note(self, note=None, *, text=None, lang=None, encoding=None):
    return super().add_note(note, text=text, lang=lang, encoding=encoding)

  def add_prop(self, prop=None, *, text=None, type=None, lang=None, encoding=None):
    return super().add_prop(prop, text=text, type=type, lang=lang, encoding=encoding)

  def add_tuv(
    self,
    tuv: Tuv | Iterable[Tuv] | None = None,
    *,
    lang: str | None = None,
    segment: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
    encoding: str | None = None,
    datatype: str | None = None,
    usagecount: str | int | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    notes: Iterable[Note] | None = None,
    props: Iterable[Prop] | None = None,
  ) -> None:
    """
    Appends a :class:`Tuv` to the :attr:`tuvs <Tu.tuvs>` attribute of the current
    :class:`Tu`.

    .. note::
        The :class:`Tuv` object that is added is `always` a new object.
        To add your :class:`Tuv` object to the :attr:`tuvs <Tu.tuvs>` attribute,
        you need to directly append it using notes.append(my_tuv).

        .. code-block:: python

            from PythonTmx import Tu, Tuv

            my_tuv = Tuv(encoding="utf-8", segment=["This is a segment"])
            my_tu = Tu()
            my_tu.add_tuv(my_tuv)
            my_tu.tuvs.append(my_tuv)
            # the tu added by add_tuv is not the same object as my_tuv
            assert my_tu.tuvs[0] is not my_tuv
            # the directly appended tuv is the same
            assert my_tu.tuvs[1] is my_tuv
            # both tuvs are equal
            assert my_tu.tuvs[0] == my_tu.tuvs[1]

    If an Iterable of :class:`Tuv` objects is passed, a new :class:`Tuv`
    object is created for each element in the iterable and appended to the
    :attr:`tuvs <Tu.tuvs>` attribute of the object.

    if `tuv` is None, a new tuv will be created with the provided arguments.
    if `tuv` is not None and any of the arguments are not None, the provided
    arguments will be used to update the new tuv before it is added to the object.
    The original `tuv` is not modified.

    Parameters:
    -----------
    tuv : Tuv | Iterable[Tuv] | None, optional
        The tuv to add. If None, :attr:`segment` must be provided.
        By default, None.
        For more info see: :class:`Tuv`
    lang : str | None, optional
        The language of the tuv, by default None.
        For more info see: :attr:`lang <Tuv.lang>`
    segment : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None, optional
        The segment of the tuv, by default an empty list.
        For more info see: :attr:`segment <Tuv.segment>`
    encoding : str | None, optional
        The encoding of the tuv, by default None.
        For more info see: :attr:`encoding <Tuv.encoding>`
    datatype : str | None, optional
        The datatype of the tuv, by default None.
        For more info see: :attr:`datatype <Tuv.datatype>`
    usagecount : str | int | None, optional
        The usagecount of the tuv, by default None.
        For more info see: :attr:`usagecount <Tuv.usagecount>`
    lastusagedate : str | datetime | None, optional
        The lastusagedate of the tuv, by default None.
        For more info see: :attr:`lastusagedate <Tuv.lastusagedate>`
    creationtool : str | None, optional
        The creationtool of the tuv, by default None.
        For more info see: :attr:`creationtool <Tuv.creationtool>`
    creationtoolversion : str | None, optional
        The creationtoolversion of the tuv, by default None.
        For more info see: :attr:`creationtoolversion <Tuv.creationtoolversion>`
    creationdate : str | datetime | None, optional
        The creationdate of the tuv, by default None.
        For more info see: :attr:`creationdate <Tuv.creationdate>`
    creationid : str | None, optional
        The creationid of the tuv, by default None.
        For more info see: :attr:`creationid <Tuv.creationid>`
    changedate : str | datetime | None, optional
        The changedate of the tuv, by default None.
        For more info see: :attr:`changedate <Tuv.changedate>`
    changeid : str | None, optional
        The changeid of the tuv, by default None.
        For more info see: :attr:`changeid <Tuv.changeid>`
    tmf : str | None, optional
        The tmf of the tuv, by default None.
        For more info see: :attr:`tmf <Tuv.tmf>`
    notes : Iterable[Note] | None, optional
        The notes of the tuv, by default an empty list.
        For more info see: :attr:`notes <Tuv.notes>`
    props : Iterable[Prop] | None, optional
        The props of the tuv, by default an empty list.
        For more info see: :attr:`props <Tuv.props>`

    Raises:
    -------
    TypeError
        If `tuv` is not a `Tuv` object or if any of the objects in 'tuv' is
        not a `Tuv` object (if an Iterable is provided).

    Examples:
    ---------
    .. code-block:: python

        from PythonTmx import Tu, Tuv

        tuv = Tuv(segment=["This is a segment"])
        tu = Tu()
        tu.add_tuv(tuv, lang="en", encoding="utf-8")
        print(tu.tuvs)
        # Output (formatted for readiblity):
        #  [
        #   Tuv(
        #     segment=["This is a segment"],
        #     lang="en",
        #     encoding="utf-8",
        #     datatype=None,
        #     usagecount=None,
        #     lastusagedate=None,
        #     creationtool=None,
        #     creationtoolversion=None,
        #     creationdate=None,
        #     creationid=None,
        #     changedate=None,
        #     changeid=None,
        #     tmf=None,
        #     notes=[],
        #     props=[])
        #  ]

    See also:
    ---------
    :class:`Tuv`, :class:`Tu`, :meth:`add_tu`
    """
    if isinstance(tuv, Iterable):
      for t in tuv:
        self.add_tuv(
          t,
          lang=lang,
          segment=segment,
          encoding=encoding,
          datatype=datatype,
          usagecount=usagecount,
          lastusagedate=lastusagedate,
          creationtool=creationtool,
          creationtoolversion=creationtoolversion,
          creationdate=creationdate,
          creationid=creationid,
          changedate=changedate,
          changeid=changeid,
          tmf=tmf,
          notes=notes,
          props=props,
        )
      return
    elif tuv is None:
      if lang is None:
        raise ValueError("if 'tuv' is None, 'lang' must be provided")
      tuv_ = Tuv(
        encoding=encoding,
        lang=lang,
        datatype=datatype,
        usagecount=usagecount,
        lastusagedate=lastusagedate,
        creationtool=creationtool,
        creationtoolversion=creationtoolversion,
        creationdate=creationdate,
        creationid=creationid,
        changedate=changedate,
        changeid=changeid,
        tmf=tmf,
      )
    if isinstance(tuv, Tuv):
      tuv_ = Tuv(
        lang=lang if lang is not None else tuv.lang,
        encoding=encoding if encoding is not None else tuv.encoding,
        datatype=datatype if datatype is not None else tuv.datatype,
        usagecount=usagecount if usagecount is not None else tuv.usagecount,
        lastusagedate=lastusagedate if lastusagedate is not None else tuv.lastusagedate,
        creationtool=creationtool if creationtool is not None else tuv.creationtool,
        creationtoolversion=creationtoolversion
        if creationtoolversion is not None
        else tuv.creationtoolversion,
        creationdate=creationdate if creationdate is not None else tuv.creationdate,
        creationid=creationid if creationid is not None else tuv.creationid,
        changedate=changedate if changedate is not None else tuv.changedate,
        changeid=changeid if changeid is not None else tuv.changeid,
        tmf=tmf if tmf is not None else tuv.tmf,
      )
    else:
      raise TypeError("tuv must be a Tuv")
    tuv_.add_note(notes if notes is not None else tuv.notes)
    tuv_.add_prop(props if props is not None else tuv.props)
    if segment is not None:
      tuv_.segment = list(segment)
    else:
      tuv_.segment = tuv.segment
    self.tuvs.append(tuv_)


@define(kw_only=True)
class Tmx:
  """
  The `tmx <https://www.gala-global.org/tmx-14b#tmx>`_ element, used to contain
  the data for a given translation memory file. Cannot be attached to any other
  element.
  """

  header: Header | None = field(
    default=None, validator=validators.optional(validators.instance_of(Header))
  )
  """
  The :class:`Header` element, used to specify the metadata of the TMX file.
  """
  tus: MutableSequence[Tu] = field(
    factory=list,
    validator=validators.deep_iterable(member_validator=validators.instance_of(Tu)),
  )
  """
  A MutableSequence of :class:`Tu` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements. At the very
  least, the container should support the ``append`` method if the
  :meth:`add_tu` function will be used.
  """

  @staticmethod
  def _from_element(
    elem: XmlElement, *, header: Header | None = None, tus: Iterable[Tu] | None = None
  ) -> Tmx:
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "tmx":
      raise ValueError(f"Expected <tmx> element, got {str(elem.tag)}")
    if header is None:
      if (header_elem := elem.find("header")) is not None:
        header = Header._from_element(header_elem)
      else:
        header = None
    if tus is None:
      if (body := elem.find("body")) is not None:
        tus = [Tu._from_element(e) for e in body if e.tag == "tu"]
      else:
        tus = []
    else:
      tus_ = []
      for tu in tus:
        if not isinstance(tu, Tu):
          raise TypeError(f"Expected Tu, got {type(tu)}")
        tus_.append(tu)
      tus = tus_
    return Tmx(header=header, tus=tus)

  def add_tu(
    self,
    tu: Tu | Iterable[Tu] | None = None,
    *,
    tuid: str | None = None,
    encoding: str | None = None,
    datatype: str | None = None,
    usagecount: str | None = None,
    lastusagedate: str | datetime | None = None,
    creationtool: str | None = None,
    creationtoolversion: str | None = None,
    creationdate: str | datetime | None = None,
    creationid: str | None = None,
    changedate: str | datetime | None = None,
    segtype: Literal["block", "paragraph", "sentence", "phrase"] | None = None,
    changeid: str | None = None,
    tmf: str | None = None,
    srclang: str | None = None,
    tuvs: Iterable[Tuv] | None = None,
    notes: Iterable[Note] | None = None,
    props: Iterable[Prop] | None = None,
  ) -> None:
    """
    Appends a :class:`Tu` to the :attr:`tus <Tmx.tus>` attribute of the current
    :class:`Tmx`.

    .. note::
        The :class:`Tu` object that is added is `always` a new object.
        To add your :class:`Tu` object to the :attr:`tus <Tmx.tus>` attribute,
        you need to directly append it using notes.append(my_tu).

        .. code-block:: python

            from PythonTmx import Tmx, Tu

            my_tu = Tu()
            my_tmx = Tmx()
            my_tmx.add_tu(my_tu)
            my_tmx.tus.append(my_tu)
            # the tmx added by add_tu is not the same object as my_tu
            assert my_tmx.tus[0] is not my_tu
            # the directly appended tu is the same
            assert my_tmx.tus[1] is my_tu
            # both tus are equal
            assert my_tmx.tus[0] == my_tmx.tus[1]

    If an Iterable of :class:`Tu` objects is passed, a new :class:`Tu`
    object is created for each element in the iterable and appended to the
    :attr:`tus <Tmx.tus>` attribute of the object.

    if `tu` is None, a new tu will be created with the provided arguments.
    if `tu` is not None and any of the arguments are not None, the provided
    arguments will be used to update the new tu before it is added to the object.
    The original `tu` is not modified.

    Parameters:
    -----------
    tu : Tu | Iterable[Tu] | None, optional
        The tu to add. If None, :attr:`tuid` must be provided.
        By default, None.
        For more info see: :class:`Tu`
    tuid : str | None, optional
        The tuid of the tu, by default None.
        For more info see: :attr:`tuid <Tu.tuid>`
    encoding : str | None, optional
        The encoding of the tu, by default None.
        For more info see: :attr:`encoding <Tu.encoding>`
    datatype : str | None, optional
        The datatype of the tu, by default None.
        For more info see: :attr:`datatype <Tu.datatype>`
    usagecount : str | None, optional
        The usagecount of the tu, by default None.
        For more info see: :attr:`usagecount <Tu.usagecount>`
    lastusagedate : str | datetime | None, optional
        The lastusagedate of the tu, by default None.
        For more info see: :attr:`lastusagedate <Tu.lastusagedate>`
    creationtool : str | None, optional
        The creationtool of the tu, by default None.
        For more info see: :attr:`creationtool <Tu.creationtool>`
    creationtoolversion : str | None, optional
        The creationtoolversion of the tu, by default None.
        For more info see: :attr:`creationtoolversion <Tu.creationtoolversion>`
    creationdate : str | datetime | None, optional
        The creationdate of the tu, by default None.
        For more info see: :attr:`creationdate <Tu.creationdate>`
    creationid : str | None, optional
        The creationid of the tu, by default None.
        For more info see: :attr:`creationid <Tu.creationid>`
    changedate : str | datetime | None, optional
        The changedate of the tu, by default None.
        For more info see: :attr:`changedate <Tu.changedate>`
    segtype : Literal["block", "paragraph", "sentence", "phrase"] | None, optional
        The segtype of the tu, by default None.
        For more info see: :attr:`segtype <Tu.segtype>`
    changeid : str | None, optional
        The changeid of the tu, by default None.
        For more info see: :attr:`changeid <Tu.changeid>`
    tmf : str | None, optional
        The tmf of the tu, by default None.
        For more info see: :attr:`tmf <Tu.tmf>`
    srclang : str | None, optional
        The srclang of the tu, by default None.
        For more info see: :attr:`srclang <Tu.srclang>`
    tuvs : Iterable[Tuv] | None, optional
        The tuvs of the tu, by default an empty list.
        For more info see: :attr:`tuvs <Tu.tuvs>`
    notes : Iterable[Note] | None, optional
        The notes of the tu, by default an empty list.
        For more info see: :attr:`notes <Tu.notes>`
    props : Iterable[Prop] | None, optional
        The props of the tu, by default an empty list.
        For more info see: :attr:`props <Tu.props>`

    Raises:
    -------
    TypeError
        If `tu` is not a `Tu` object or if any of the objects in 'tu' is
        not a `Tu` object (if an Iterable is provided).

    Examples:
    ---------
    .. code-block:: python

        from PythonTmx import Tmx, Tu

        tu = Tu()
        tmx = Tmx()
        tmx.add_tu(tu, tuid="tuid", encoding="utf-8")
        print(tmx.tus)
        # Output (formatted for readiblity):
        #  [
        #   Tu(
        #     tuid="tuid",
        #     encoding="utf-8",
        #     datatype=None,
        #     usagecount=None,
        #     lastusagedate=None,
        #     creationtool=None,
        #     creationtoolversion=None,,
        #     creationdate=None,
        #     creationid=None,
        #     changedate=None,
        #     segtype=None,
        #     changeid=None,
        #     tmf=None,
        #     srclang=None,
        #     tuvs=[],
        #     notes=[],
        #     props=[],
        #   )
        #  ]

    See also:
    ---------
    :class:`Tu`, :class:`Tmx`, :meth:`add_tuv`
    """
    [
      Tu(
        tuid="tuid",
        encoding="utf-8",
        datatype=None,
        usagecount=None,
        lastusagedate=None,
        creationtool=None,
        creationtoolversion=None,
        creationdate=None,
        creationid=None,
        changedate=None,
        segtype=None,
        changeid=None,
        tmf=None,
        srclang=None,
        tuvs=[],
        notes=[],
        props=[],
      )
    ]
    if isinstance(tu, Iterable):
      for t in tu:
        self.add_tu(
          t,
          tuid=tuid,
          encoding=encoding,
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
          tmf=tmf,
          srclang=srclang,
          tuvs=tuvs,
          notes=notes,
          props=props,
        )
      return
    elif tu is None:
      tu_ = Tu(
        tuid=tuid,
        encoding=encoding,
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
        tmf=tmf,
        srclang=srclang,
      )
    if isinstance(tu, Tu):
      tu_ = Tu(
        tuid=tuid if tuid is not None else tu.tuid,
        encoding=encoding if encoding is not None else tu.encoding,
        datatype=datatype if datatype is not None else tu.datatype,
        usagecount=usagecount if usagecount is not None else tu.usagecount,
        lastusagedate=lastusagedate if lastusagedate is not None else tu.lastusagedate,
        creationtool=creationtool if creationtool is not None else tu.creationtool,
        creationtoolversion=creationtoolversion
        if creationtoolversion is not None
        else tu.creationtoolversion,
        creationdate=creationdate if creationdate is not None else tu.creationdate,
        creationid=creationid if creationid is not None else tu.creationid,
        changedate=changedate if changedate is not None else tu.changedate,
        segtype=segtype if segtype is not None else tu.segtype,
        changeid=changeid if changeid is not None else tu.changeid,
        tmf=tmf if tmf is not None else tu.tmf,
        srclang=srclang if srclang is not None else tu.srclang,
      )
    else:
      raise TypeError("tu must be a Tu object")
    tu_.add_note(notes if notes is not None else tu.notes)
    tu_.add_prop(props if props is not None else tu.props)
    tu_.add_tuv(tuvs if tuvs is not None else tu.tuvs)
    self.tus.append(tu_)

  @staticmethod
  def _to_element(tmx: Tmx) -> et._Element:
    elem = et.Element("tmx", version="1.4")
    if tmx.header is None:
      raise TypeError("Cannot export Tmx with an empty header")
    elem.append(Header._to_element(tmx.header))
    body = et.SubElement(elem, "body")
    for tu in tmx.tus:
      if not isinstance(tu, Tu):
        raise TypeError(f"Expected Tu, got {type(tu)}")
      body.append(Tu._to_element(tu))
    return elem
