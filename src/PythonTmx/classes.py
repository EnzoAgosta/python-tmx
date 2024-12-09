from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import MutableSequence
from datetime import datetime
from typing import Iterable, Literal, TypeAlias, overload
from warnings import deprecated

import lxml.etree as et
from attrs import define, field, validate, validators

XmlElement: TypeAlias = et._Element | ET.Element
TmxElement: TypeAlias = "Note | Prop | Ude | Map | Header| Tu| Tuv| Tmx|Bpt | Ept | It | Ph | Hi | Ut | Sub | Ude"


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
      `mask` parameter.
  """
  result: list = []
  if elem.text is not None:
    result.append(elem.text)
  for e in elem:
    for e in elem:
      if str(e.tag) not in mask:
        continue
      if e.tag == "bpt":
        result.append(Bpt.from_element(e))
      elif e.tag == "ept":
        result.append(Ept.from_element(e))
      elif e.tag == "it":
        result.append(It.from_element(e))
      elif e.tag == "ph":
        result.append(Ph.from_element(e))
      elif e.tag == "hi":
        result.append(Hi.from_element(e))
      elif e.tag == "ut":
        result.append(Ut.from_element(e))
      elif e.tag == "sub":
        result.append(Sub.from_element(e))
      if e.tail is not None:
        result.append(e.tail)
  return result


@define(kw_only=True)
class Note:
  """
  A `<note> <https://www.gala-global.org/tmx-14b#note>`_ element,
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
  def from_element(
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

  @overload
  @classmethod
  def to_element(cls, note: Note, engine: Literal["std"]) -> ET.Element: ...
  @overload
  @classmethod
  def to_element(cls, note: Note, engine: Literal["lxml"]) -> et._Element: ...
  @classmethod
  def to_element(cls, note: Note, engine) -> XmlElement:
    def to_lxml(note: Note) -> et._Element:
      elem = et.Element("note")
      elem.text = note.text
      if note.lang is not None:
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", note.lang)
      if note.encoding is not None:
        elem.set("o-encoding", note.encoding)
      return elem

    def to_std(note: Note) -> ET.Element:
      elem = ET.Element("note")
      elem.text = note.text
      if note.lang is not None:
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", note.lang)
      if note.encoding is not None:
        elem.set("o-encoding", note.encoding)
      return elem

    validate(note)
    match engine:
      case "lxml":
        return to_lxml(note)
      case "std":
        return to_std(note)
      case _:
        raise ValueError(f"Unknown engine: {engine}")


@define(kw_only=True)
class Prop:
  """
  A `<prop> <https://www.gala-global.org/tmx-14b#prop>` Element,
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
    default=None, validator=validators.optional(validators.instance_of(str))
  )
  """
  The locale of the text. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
  """
  encoding: str | None = field(
    default=None, validator=validators.optional(validators.instance_of(str))
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
  def from_element(
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

  @overload
  @classmethod
  def to_element(cls, prop: Prop, engine: Literal["std"]) -> ET.Element: ...
  @overload
  @classmethod
  def to_element(cls, prop: Prop, engine: Literal["lxml"]) -> et._Element: ...
  @classmethod
  def to_element(cls, prop: Prop, engine) -> XmlElement:
    def to_lxml(prop: Prop) -> et._Element:
      elem = et.Element("prop")
      elem.text = prop.text
      if prop.lang is not None:
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", prop.lang)
      if prop.encoding is not None:
        elem.set("o-encoding", prop.encoding)
      if prop.type is not None:
        elem.set("type", prop.type)
      return elem

    def to_std(prop: Prop) -> ET.Element:
      elem = ET.Element("prop")
      elem.text = prop.text
      if prop.lang is not None:
        elem.set("{http://www.w3.org/XML/1998/namespace}lang", prop.lang)
      if prop.encoding is not None:
        elem.set("o-encoding", prop.encoding)
      if prop.type is not None:
        elem.set("type", prop.type)
      return elem

    validate(prop)
    match engine:
      case "lxml":
        return to_lxml(prop)
      case "std":
        return to_std(prop)
      case _:
        raise ValueError(f"Unknown engine: {engine}")


@define(kw_only=True)
class Map:
  """
  The `<map> <https://www.gala-global.org/tmx-14b#map>`_ element, used to specify
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
    validator=[
      validators.optional(validators.instance_of(str)),
      validators.optional(validators.matches_re(r"^#x.*?")),
    ],
  )

  """
  The code-point value corresponding to the unicode character of a the element.
  Must be a Hexadecimal value prefixed with "#x". By default None.
  """
  ent: str | None = field(
    default=None, validator=validators.optional(validators.instance_of(str))
  )
  """
  The entity name of the character defined by the element. Must be text in ASCII.
  By default None.
  """
  subst: str | None = None
  """
  An alternative string for the character defined in the element. Must be text
  in ASCII. By default None.
  """

  @staticmethod
  def from_element(
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


@define(kw_only=True)
class Ude:
  """
  The `<ude> <https://www.gala-global.org/tmx-14b#ude>`_ Element, used to specify
  a set of user-defined characters and/or, optionally their mapping from
  Unicode to the user-defined encoding.
  Can only be attached to :class:`Header`.
  """

  name: str
  """
  The name of a element. Its value is not defined by the standard
  """
  base: str | None = None
  """
  The encoding upon which the re-mapping of the element is based.
  Ideally one of the [IANA] `recommended charset
  <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  Required if at least of the :class:`Map` elements has a `code` attribute.
  """
  maps: MutableSequence[Map] = field(factory=list)
  """
  A MutableSequence of :class:`Map` elements.
  While any iterable (or even a Generator expression) can technically be used,
  it is recommended to use a list or some other collection that preserves the
  order of the elements.
  At the very least, the container should support the ``append`` method if the
  :func:`add_map <utils.add_map>` function will be used.
  """

  @staticmethod
  def from_element(
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
      maps = [Map.from_element(e) for e in elem if e.tag == "map"]
    else:
      for map in maps:
        if not isinstance(map, Map):
          raise TypeError(f"Expected Map, got {type(map)}")
    return Ude(
      name=name, base=base if base is not None else elem.get("base"), maps=list(maps)
    )


@define(kw_only=True)
class Header:
  """
  The `<header> <https://www.gala-global.org/tmx-14b#header>`_ element, used to
  specify the metadata of the TMX file. Can only be attached to :class:`Tmx`.
  A :class:`Tmx` can have only one :class:`Header` element.
  """

  creationtool: str
  """
  The tool that created the TMX document.
  """
  creationtoolversion: str
  """
  the version of the tool that created the TMX document.
  """
  segtype: Literal["block", "paragraph", "sentence", "phrase"]
  """
  The type of segmentation used in the file.
  """
  tmf: str
  """
  The format of the translation memory file from which the TMX document or
  segment thereof have been generated.
  """
  adminlang: str
  """
  The default language for the administrative and informative elements
  :class:`Prop` and :class:`Note`. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for adminlang are not case-sensitive.
  """
  srclang: str
  """
  The source language of the file. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for srclang are not case-sensitive.
  """
  datatype: str
  """
  The type of the data contained in the file.
  """
  encoding: str | None = None
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  creationdate: str | datetime | None = None
  """
  The date and time the file was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = None
  """
  The ID of the user that created the file, by default None
  """
  changedate: str | datetime | None = None
  """
  The date and time the file was last changed, by default None
  It is recommended to use :external:class:`datetime.datetime` objects
  instead of raw strings. If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  """
  changeid: str | None = None
  """
  The ID of the user that last changed the file, by default None
  """
  props: MutableSequence[Prop] = field(factory=list)
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_prop <utils.add_prop>` function will be used.
  """
  notes: MutableSequence[Note] = field(factory=list)
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_note <utils.add_note>` function will be used.
  """
  udes: MutableSequence[Ude] = field(factory=list)
  """
  A MutableSequence of :class:`Ude` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_ude <utils.add_ude>` function will be used.
  """

  @staticmethod
  def from_element(
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
        is does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        is does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    udes : Iterable[Ude] | None, optional
        A Iterable of :class:`Ude` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`udes` will be a list of :class:`Ude` elements. If the Iterable
        is does not preserve insertion order, the order of the resulting list
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
      props = [Prop.from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note.from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    if udes is None:
      udes = [Ude.from_element(e) for e in elem if e.tag == "ude"]
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
      segtype = elem.attrib["segtype"]  # type: ignore # validation should only be forced on export
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
      segtype=segtype,  # type: ignore # validation should only be forced on export
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


@define(kw_only=True)
class Tuv:
  """
  The `<tuv> <https://www.gala-global.org/tmx-14b#tuv>`_ Element, used to specify
  the translation of a segment of text in a :class:`Tu` Element.
  Can only be attached to :class:`Tu`.
  """

  segment: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(factory=list)
  """
  A MutableSequence of strings, or :class:`Bpt`, :class:`Ept`, :class:`It`,
  :class:`Ph`, :class:`Hi`, :class:`Ut` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements.
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_ept <utils.add_ept>`,
  :func:`add_it <utils.add_it>`, :func:`add_ph <utils.add_ph>`,
  :func:`add_hi <utils.add_hi>` or :func:`add_ut <utils.add_ut>` functions will
  be used. By default an empty list.
  """
  encoding: str | None = None
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  datatype: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  usagecount: str | int | None = None
  """
  The number of times the element has been used. By default None.
  """
  lastusagedate: str | datetime | None = None
  """
  The date and time the element was last used. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationtool: str | None = None
  """
  The tool that created the element. By default None.
  """
  creationtoolversion: str | None = None
  """
  The version of the tool that created the element. By default None.
  """
  creationdate: str | datetime | None = None
  """
  The date and time the element was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = None
  """
  The ID of the user that created the element, by default None 
  """
  changedate: str | datetime | None = None
  """
  The date and time the element was last changed. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  changeid: str | None = None
  """
  The ID of the user that last changed the element, by default None
  """
  tmf: str | None = None
  """
  The format of the translation memory file from which the element has been
  generated. By default None.
  """
  notes: MutableSequence[Note] = field(factory=list)
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_note <utils.add_note>` function will be used.
  """
  props: MutableSequence[Prop] = field(factory=list)
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_prop <utils.add_prop>` function will be used.
  """

  @staticmethod
  def from_element(
    elem: XmlElement,
    *,
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
        made of the provided elements. If the Iterable is does not preserve
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
        is does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        is does not preserve insertion order, the order of the resulting list
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
      props = [Prop.from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note.from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    return Tuv(
      segment=segment,
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
class Tu:
  """
  The `<tu> <https://www.gala-global.org/tmx-14b#tu>`_ Element, used to contain
  the data for a given translation unit. Can only be attached to :class:`Tmx`.
  """

  tuid: str | None = None
  """
  The ID of the translation unit. Its value is not defined by the standard.
  Must be a str without spaces.
  """
  encoding: str | None = None
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set. Ideally one of the `IANA recommended
  charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_.
  By default None.
  """
  datatype: str | None = None
  """
  The type of the data contained in the element. By default None.
  """
  usagecount: str | int | None = None
  """
  The number of times the element has been used. By default None.
  """
  lastusagedate: str | datetime | None = None
  """
  The date and time the element was last used. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationtool: str | None = None
  """
  The tool that created the element. By default None.
  """
  creationtoolversion: str | None = None
  """
  The version of the tool that created the element. By default None.
  """
  creationdate: str | datetime | None = None
  """
  The date and time the element was created. It is recommended to use
  :external:class:`datetime.datetime` objects instead of raw strings.
  If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
  By default None.
  """
  creationid: str | None = None
  """
  The ID of the user that created the element, by default None
  """
  changedate: str | datetime | None = None
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
  changeid: str | None = None
  """
  The ID of the user that last changed the element, by default None
  """
  tmf: str | None = None
  """
  The format of the translation memory file from which the element has been
  generated. By default None.
  """
  srclang: str | None = None
  """
  The source language of the element. Ideally a language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the other TMX
  attributes, the values for srclang are not case-sensitive.
  """
  tuvs: MutableSequence[Tuv] = field(factory=list)
  """
  A MutableSequence of :class:`Tuv` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements. At the very
  least, the container should support the ``append`` method if the
  :func:`add_tuv <utils.add_tuv>` function will be used.
  """
  notes: MutableSequence[Note] = field(factory=list)
  """
  A MutableSequence of :class:`Note` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_note <utils.add_note>` function will be used.
  """
  props: MutableSequence[Prop] = field(factory=list)
  """
  A MutableSequence of :class:`Prop` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a
  list or some other collection that preserves the order of the elements. At
  the very least, the container should support the ``append`` method if the
  :func:`add_prop <utils.add_prop>` function will be used.
  """

  @staticmethod
  def from_element(
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
        is does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`notes` will be a list of :class:`Note` elements. If the Iterable
        is does not preserve insertion order, the order of the resulting list
        cannot be guaranteed. By default an empty list.
    tuvs : Iterable[Tuv] | None, optional
        A Iterable of :class:`Tuv` elements. While any iterable (or even a
        Generator expression) can technically be used, the resulting element
        :attr:`tuvs` will be a list of :class:`Tuv` elements. If the Iterable
        is does not preserve insertion order, the order of the resulting list
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
      props = [Prop.from_element(e) for e in elem if e.tag == "prop"]
    else:
      props_ = []
      for prop in props:
        if not isinstance(prop, Prop):
          raise TypeError(f"Expected Prop, got {type(prop)}")
        props_.append(prop)
      props = props_
    if notes is None:
      notes = [Note.from_element(e) for e in elem if e.tag == "note"]
    else:
      notes_ = []
      for note in notes:
        if not isinstance(note, Note):
          raise TypeError(f"Expected Note, got {type(note)}")
        notes_.append(note)
      notes = notes_
    if tuvs is None:
      tuvs = [Tuv.from_element(e) for e in elem if e.tag == "tuv"]
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
class Tmx:
  """
  The `<tmx> <https://www.gala-global.org/tmx-14b#tmx>`_ element, used to contain
  the data for a given translation memory file. Cannot be attached to any other
  element.
  """

  header: Header | None = None
  """
  The :class:`Header` element, used to specify the metadata of the TMX file.
  """
  tus: MutableSequence[Tu] = field(factory=list)
  """
  A MutableSequence of :class:`Tu` elements. While any iterable (or even a
  Generator expression) can technically be used, it is recommended to use a list
  or some other collection that preserves the order of the elements. At the very
  least, the container should support the ``append`` method if the
  :func:`add_tu <utils.add_tu>` function will be used.
  """

  @staticmethod
  def from_element(
    elem: XmlElement, *, header: Header | None = None, tus: Iterable[Tu] | None = None
  ) -> Tmx:
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "tmx":
      raise ValueError(f"Expected <tmx> element, got {str(elem.tag)}")
    if header is None:
      if (header_elem := elem.find("header")) is not None:
        header = Header.from_element(header_elem)
      else:
        header = None
    if tus is None:
      if (body := elem.find("body")) is not None:
        tus = [Tu.from_element(e) for e in body if e.tag == "tu"]
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


@define(kw_only=True)
class Bpt:
  """
  The `<bpt> <https://www.gala-global.org/tmx-14b#bpt>`_ Element, to delimit the
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_it <utils.add_it>`,
  :func:`add_ph <utils.add_ph>`, :func:`add_hi <utils.add_hi>` or
  :func:`add_ut <utils.add_ut>` functions will be used. By default an empty list.
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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


@define(kw_only=True)
class Ept:
  """
  The `<ept> <https://www.gala-global.org/tmx-14b#ept>`_ Element, to delimit the
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_it <utils.add_it>`,
  :func:`add_ph <utils.add_ph>`, :func:`add_hi <utils.add_hi>` or
  :func:`add_ut <utils.add_ut>` functions will be used. By default an empty list.
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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


@define(kw_only=True)
class Hi:
  """
  The `<hi> <https://www.gala-global.org/tmx-14b#hi>`_ Element, used to delimit
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_it <utils.add_it>`,
  :func:`add_ph <utils.add_ph>`, :func:`add_hi <utils.add_hi>` or
  :func:`add_ut <utils.add_ut>` functions will be used. By default an empty list.
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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


@define(kw_only=True)
class It:
  """
  The `<it> <https://www.gala-global.org/tmx-14b#it>`_ Element, used to delimit
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_ept <utils.add_ept>`,
  :func:`add_it <utils.add_it>`, :func:`add_ph <utils.add_ph>`,
  :func:`add_hi <utils.add_hi>` or :func:`add_ut <utils.add_ut>` functions will
  be used. By default an empty list.
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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
      pos = elem.attrib["pos"]  # type: ignore # validation should only be forced on export
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
      pos=pos,  # type: ignore # validation should only be forced on export
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


@define(kw_only=True)
class Ph:
  """
  The `<ph> <https://www.gala-global.org/tmx-14b#ph>`_ Element, used to delimit
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_ept <utils.add_ept>`,
  :func:`add_it <utils.add_it>`, :func:`add_ph <utils.add_ph>`,
  :func:`add_hi <utils.add_hi>` or :func:`add_ut <utils.add_ut>` functions will
  be used. By default an empty list.
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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
      assoc=assoc if assoc is not None else elem.get("assoc"),  # type: ignore # validation should only be forced on export
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


@define(kw_only=True)
class Sub:
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_it <utils.add_it>`,
  :func:`add_ph <utils.add_ph>`, :func:`add_hi <utils.add_hi>` or
  :func:`add_ut <utils.add_ut>` functions will be used. By default an empty list. 
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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


@deprecated(
  "The Ut element is deprecated, "
  "please check https://www.gala-global.org/tmx-14b#ContentMarkup_Rules to "
  "know with which element to replace it with."
)
@define(kw_only=True)
class Ut:
  """
  The `<ut> <https://www.gala-global.org/tmx-14b#ut>`_ Element, used to delimit
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
  At the very least, the container should support the ``append`` method if the
  any of the :func:`add_bpt <utils.add_bpt>`, :func:`add_ept <utils.add_ept>`,
  :func:`add_it <utils.add_it>`, :func:`add_ph <utils.add_ph>`,
  :func:`add_hi <utils.add_hi>` or :func:`add_ut <utils.add_ut>` functions will
  be used. By default an empty list.  
  """

  @staticmethod
  def from_element(
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
        If the Iterable is does not preserve insertion order, the order of the
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
