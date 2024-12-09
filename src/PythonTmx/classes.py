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
  elem : XmlElement
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
  for e in elem:
    if elem.text is not None:
      result.append(elem.text)
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

  text: str
  """
  The text of the note.
  """
  lang: str | None = None
  """
  The locale of the text, by default None.

  A language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
  """
  encoding: str | None = None
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set, by default None

  One of the `IANA recommended charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
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
        The locale of the text, by default None.

        A language code as described in the
        `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
        Unlike the other TMX attributes, the values for lang are not case-sensitive.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set, by default None

        One of the `IANA recommended charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_

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


@define(kw_only=True)
class Prop:
  """
  A `<prop> <https://www.gala-global.org/tmx-14b#prop>` Element,
  used to define the various properties of the parent element.
  These properties are not defined by the standard.
  Can be attached to :class:`Header`, :class:`Tu` and :class:`Tuv`.
  """

  text: str
  """
  The text of the Prop.
  """
  type: str
  """
  The kind of data the element represents, by convention start with "x-".
  By default None.
  """
  lang: str | None = None
  """
  The locale of the text, by default None.

  A language code as described in the
  `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for lang are not case-sensitive.
    
  """
  encoding: str | None = None
  """
  encoding : str | None, optional
    The original or preferred code set of the data of the element in case
    it is to be re-encoded in a non-Unicode code set, by default None

    One of the `IANA recommended charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
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
        The locale of the text, by default None.

        A language code as described in the
        `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
        Unlike the other TMX attributes, the values for lang are not case-sensitive.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set, by default None

        One of the `IANA recommended charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_

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


@define(kw_only=True)
class Map:
  """
  The `<map> <https://www.gala-global.org/tmx-14b#map>`_ element, used to specify
  a user-defined character and some of its properties.
  Can oly be attached to :class:`Ude`.
  """

  unicode: str
  """
  The Unicode character value of the element. Must be a valid Unicode value
  (including values in the Private Use areas) in hexadecimal format.
  """
  code: str | None = None
  """
  The code-point value corresponding to the unicode character of a the element.
  Must be a Hexadecimal value prefixed with "#x".
  By default None.
  """
  ent: str | None = None
  """
  The entity name of the character defined by the element.
  Must be text in ASCII.
  By default None.
  """
  subst: str | None = None
  """
  An alternative string for the character defined in the element.
  Must be text in ASCII. By default None.
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
  One of the [IANA] `recommended charset <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
  if possible.
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
    elem : XmlElement
        The Element to parse.
    name: str
      The name of a element. Its value is not defined by the standard
    base: str | None = None
      The encoding upon which the re-mapping of the element is based.
      One of the [IANA] `recommended charset <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
      if possible.

      Required if at least of the :class:`Map` elements has a `code` attribute.
    maps: Iterable[Map], optional
      An of :class:`Map` elements.
      While any iterable (or even a generator expression) can be used,
      the resulting element :attr:`maps` will be a list of :class:`Map` elements.

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
  specify the metadata of the TMX file.
  Can only be attached to :class:`Tmx`.
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
  :class:`Prop` and :class:`Note`.
  
  A language code as described in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for adminlang are not case-sensitive.
  """
  srclang: str
  """
  The source language of the file.
  
  A language code as described in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_.
  Unlike the other TMX attributes, the values for srclang are not case-sensitive.
  """
  datatype: str
  """
  The type of the data contained in the file.
  """
  encoding: str | None = None
  """
  The original or preferred code set of the data of the element in case it is to
  be re-encoded in a non-Unicode code set, by default None

  One of the `IANA recommended charsets <https://www.iana.org/assignments/character-sets/character-sets.xhtml>`_
  """
  creationdate: str | datetime | None = None
  """
  The date and time the file was created, by default None
  It is recommended to use :external:class:`datetime.datetime` objects
  instead of raw strings. If a string is provided, it will be parsed as a
  :external:class:`datetime.datetime` object if it matches the format
  YYYYMMDDTHHMMSSZ, where T is the date/time separator, Z is the time zone offset,
  and the date/time is in Coordinated Universal Time (UTC).
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
  A MutableSequence of :class:`Prop` elements.
  While any iterable (or even a Generator expression) can technically be used,
  it is recommended to use a list or some other collection that preserves the
  order of the elements.
  At the very least, the container should support the ``append`` method if the
  :func:`add_prop <utils.add_prop>` function will be used.
  """
  notes: MutableSequence[Note] = field(factory=list)
  """
  A MutableSequence of :class:`Note` elements.
  While any iterable (or even a Generator expression) can technically be used,
  it is recommended to use a list or some other collection that preserves the
  order of the elements.
  At the very least, the container should support the ``append`` method if the
  :func:`add_note <utils.add_note>` function will be used.
  """
  udes: MutableSequence[Ude] = field(factory=list)
  """
  A MutableSequence of :class:`Ude` elements.
  While any iterable (or even a Generator expression) can technically be used,
  it is recommended to use a list or some other collection that preserves the
  order of the elements.
  At the very least, the container should support the ``append`` method if the
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
    elem : XmlElement
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
        :class:`Prop` and :class:`Note`. Must be a language code as described
        in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the
        other TMX attributes, the values for adminlang are not case-sensitive.
    srclang : str
        The source language of the file. Must be a language code as described
        in the `RFC 3066 <https://www.ietf.org/rfc/rfc3066.txt>`_. Unlike the
        other TMX attributes, the values for srclang are not case-sensitive.
    datatype : str
        The type of the data contained in the file.
    encoding : str | None, optional
        The original or preferred code set of the data of the element in case
        it is to be re-encoded in a non-Unicode code set. must be one of the
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
        The date and time the file was last change. It is recommended to use
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
        A Iterable of :class:`Prop` elements.
        While any iterable (or even a Generator expression) can technically be
        used, it is recommended to use a list or some other collection that
        preserves the order of the elements.
        At the very least, the container should support the ``append`` method
        if the :func:`add_prop <utils.add_prop>` function will be used.
        By default an empty list.
    notes : Iterable[Note] | None, optional
        A Iterable of :class:`Note` elements.
        While any iterable (or even a Generator expression) can technically be
        used, it is recommended to use a list or some other collection that
        preserves the order of the elements. At the very least, the container
        should support the ``append`` method if the
        :func:`add_note <utils.add_note>` function will be used.
        By default an empty list.
    udes : Iterable[Ude] | None, optional
        A Iterable of :class:`Ude` elements.
        While any iterable (or even a Generator expression) can technically be
        used, it is recommended to use a list or some other collection that
        preserves the order of the elements. At the very least, the container
        should support the ``append`` method if the
        :func:`add_ude <utils.add_ude>` function will be used.
        By default an empty list.
    """
    if not isinstance(elem, XmlElement):
      raise TypeError(f"Expected XmlElement, got {type(elem)}")
    if elem.tag != "header":
      raise ValueError(f"Expected <header> element, got {str(elem.tag)}")
    attribs = elem.attrib
    props, notes, udes = [], [], []
    for e in elem:
      if e.tag == "prop":
        props.append(Prop.from_element(e))
      elif e.tag == "note":
        notes.append(Note.from_element(e))
      elif e.tag == "ude":
        udes.append(Ude.from_element(e))
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
      except (TypeError, ValueError):
        pass
    if self.changedate is not None and not isinstance(self.changedate, datetime):
      try:
        self.changedate = datetime.strptime(self.changedate, r"%Y%m%dT%H%M%SZ")
      except (TypeError, ValueError):
        pass


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
