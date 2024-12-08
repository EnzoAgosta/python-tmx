from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from typing import Literal, TypeAlias

from PythonTmx.classes import (
  Bpt,
  Ept,
  Header,
  Hi,
  It,
  Map,
  Note,
  Ph,
  Prop,
  Sub,
  Tmx,
  Tu,
  Tuv,
  Ude,
  Ut,
)

SupportsNote: TypeAlias = Header | Tu | Tuv
SupportsProp: TypeAlias = Header | Tu | Tuv
SupportsBpt: TypeAlias = Tuv | Hi | Sub
SupportsEpt: TypeAlias = Tuv | Hi | Sub
SupportsIt: TypeAlias = Tuv | Hi | Sub
SupportsPh: TypeAlias = Tuv | Hi | Sub
SupportsHi: TypeAlias = Tuv | Hi | Sub
SupportsUt: TypeAlias = Tuv | Hi | Sub
SupportsSub: TypeAlias = Bpt | Ept | It | Ph | Ut


def add_note(
  obj: SupportsNote,
  note: Note | None = None,
  *,
  text: str | None = None,
  lang: str | None = None,
  encoding: str | None = None,
) -> None:
  """
  Appends a `Note` to the object if it supports notes.
  If `note` is None, a new note will be created with the provided arguments.
  if `note` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new note before it is added to the object.
  The original `note` is not modified.


  Parameters
  ----------
  obj : SupportsNote
      A class that supports notes, namely Header, Tu and Tuv.
  note : Note | None, optional
      The note to add, by default None
  text : str
      the text of the note.
  lang : str | None, optional
      the language of the note, by default None
  encoding : str | None, optional
      The original encoding of the note, by default None

  Raises
  ------
  TypeError
      If `obj` is not a `Header`, `Tu` or `Tuv`.
  TypeError
      If `note` is not a `Note` object.
  ValueError
      If `note` is None and `text` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_note
  >>> from PythonTmx.classes import Tu, Note
  >>> tu = Tu()
  >>> add_note(tu, text="This is a note")
  >>> add_note(tu, text="This is another note", lang="en")
  >>> print(tu.notes)
  [Note(text='This is a note', lang=None, encoding=None), Note(text='This is another note', lang='en', encoding=None)]
  """
  if not isinstance(obj, SupportsNote):
    raise TypeError("'obj' must be one of Header, Tu or Tuv")
  if not isinstance(note, Note) and note is not None:
    raise TypeError("'note' must be a Note object")
  if note is not None:
    new_note = Note(
      text=text if text is not None else note.text,
      encoding=encoding if encoding is not None else note.encoding,
      lang=lang if lang is not None else note.lang,
    )
  else:
    if text is None:
      raise ValueError("Either 'note' or 'text' must be provided to create a new note")
    new_note = Note(text=text, lang=lang, encoding=encoding)
  obj.notes.append(new_note)


def add_notes(obj: SupportsNote, notes: Iterable[Note]) -> None:
  """
  Appends notes to the object.

  Parameters
  ----------
  obj : SupportsNote
      A class that supports notes, namely `Header`, `Tu` and `Tuv`.
  notes : Iterable[Note]
      An Iterable of `Note` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Header`, `Tu` or `Tuv`.
  TypeError
      If any of the `notes` are not `Note` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_notes
  >>> from PythonTmx.classes import Tu, Note
  >>> tu = Tu()
  >>> add_notes(tu, [Note(text="This is a note"), Note(text="This is another note")])
  >>> print(tu.notes)
  [Note(text='This is a note', lang=None, encoding=None), Note(text='This is another note', lang=None, encoding=None)]
  """
  if not isinstance(obj, SupportsNote):
    raise TypeError("'obj' must be one of Header, Tu or Tuv")
  for note in notes:
    if not isinstance(note, Note):
      raise TypeError(
        "'notes' must be an iterable of Note objects but found a "
        f"{type(note)} object"
      )
    add_note(obj, note)


def add_prop(
  obj: SupportsProp,
  prop: Prop | None = None,
  *,
  text: str | None = None,
  type: str | None = None,
  lang: str | None = None,
  encoding: str | None = None,
) -> None:
  """Appends a `Prop` to the object if it supports props.
  If `prop` is None, a new prop will be created with the provided arguments.
  if `prop` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new prop before it is added to the object.
  The original `prop` is not modified.

  Parameters
  ----------
  obj : SupportsProp
      A class that supports props, namely `Header`, `Tu` and `Tuv`.
  prop : Prop | None, optional
      The prop to add, by default None
  text : str | None, optional
      The text of the prop, by default None
  type : str | None, optional
      The type of the prop, by default None
  lang : str | None, optional
      The language of the prop, by default None
  encoding : str | None, optional
      The original encoding of the prop, by default None

  Raises
  ------
  TypeError
      If `obj` is not a `Header`, `Tu` or `Tuv`.
  TypeError
      If `prop` is not a `Prop` object.
  ValueError
      If `prop` is None and `text` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_prop
  >>> from PythonTmx.classes import Tu, Prop
  >>> tu = Tu()
  >>> add_prop(tu, text="This is a prop", type="type")
  >>> add_prop(tu, text="This is another prop", type="type", lang="en")
  >>> print(tu.props)
  [Prop(text='This is a prop', type='type', lang=None, encoding=None), Prop(text='This is another prop', type='type', lang='en', encoding=None)]
  """
  if not isinstance(obj, SupportsProp):
    raise TypeError("'obj' must be one of Header, Tu or Tuv")
  if not isinstance(prop, Prop) and prop is not None:
    raise TypeError("'prop' must be a Prop object")
  if prop is not None:
    new_prop = Prop(
      text=text if text is not None else prop.text,
      type=type if type is not None else prop.type,
      encoding=encoding if encoding is not None else prop.encoding,
      lang=lang if lang is not None else prop.lang,
    )
  else:
    if text is None or type is None:
      raise ValueError(
        "Either 'prop' or 'text' and 'type' must be provided to create a new prop"
      )
    new_prop = Prop(text=text, type=type, lang=lang, encoding=encoding)
  obj.props.append(new_prop)


def add_props(obj: SupportsProp, props: Iterable[Prop]) -> None:
  """Appends props to the object if it supports props.
  If any of the `props` are not `Prop` objects, a `TypeError` will be raised.

  Parameters
  ----------
  obj : SupportsProp
      A class that supports props, namely `Header`, `Tu` and `Tuv`.
  props : Iterable[Prop]
      An Iterable of `Prop` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Header`, `Tu` or `Tuv`.
  TypeError
      If any of the `props` are not `Prop` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_props
  >>> from PythonTmx.classes import Tu, Prop
  >>> tu = Tu()
  >>> add_props(
  ...   tu,
  ...   [
  ...     Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8"),
  ...     Prop(text="This is another prop", type="type", lang="en", encoding="UTF-8"),
  ...   ],
  ... )
  >>> print(tu.props)
  [Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8'), Prop(text='This is another prop', type='type', lang='en', encoding='UTF-8')]
  """
  if not isinstance(obj, SupportsProp):
    raise TypeError("'obj' must be one of Header, Tu or Tuv")
  for prop in props:
    if not isinstance(prop, Prop):
      raise TypeError(
        "'props' must be an iterable of Prop objects but found a "
        f"{type(prop)} object"
      )
    add_prop(obj, prop)


def add_ude(
  header: Header,
  ude: Ude | None = None,
  *,
  name: str | None = None,
  base: str | None = None,
  maps: Iterable[Map] | None = None,
) -> None:
  """
  Appends a `Ude` to the `Header`.
  If `ude` is None, a new ude will be created with the provided arguments.
  if `ude` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new ude before it is added to the object.
  The original `ude` is not modified.

  Parameters
  ----------
  header : Header
      The header to add the ude to.
  ude : Ude | None, optional
      The ude to add, by default None
  name : str | None, optional
      The name of the ude, by default None
  base : str | None, optional
      The base of the ude, by default None
  maps : Iterable[Map] | None, optional
      The maps of the ude, by default an empty list

  Raises
  ------
  TypeError
      If `header` is not a `Header`.
  TypeError
      If `ude` is not a `Ude` object.
  ValueError
      If `ude` is None and `name` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_ude
  >>> from PythonTmx.classes import Header, Ude, Map
  >>> header = Header(
  ...   creationtool="python-tmx",
  ...   creationtoolversion="0.3",
  ...   segtype="block",
  ...   tmf="Microsoft Translator",
  ...   adminlang="en",
  ...   srclang="en",
  ...   datatype="PlainText",
  ... )
  >>> add_ude(
  ...   header,
  ...   name="name",
  ...   base="base",
  ...   maps=[Map(unicode="a", code="A", ent="A", subst="a")],
  ... )
  >>> print(header.udes)
  [Ude(name='name', base='base', maps=[Map(unicode='a', code='A', ent='A', subst='a')])]
  """
  if not isinstance(header, Header):
    raise TypeError("'header' must be a Header object")
  if not isinstance(ude, Ude) and ude is not None:
    raise TypeError("'ude' must be a Ude object")
  if ude is not None:
    new_ude = Ude(
      name=name if name is not None else ude.name,
      base=base if base is not None else ude.base,
      maps=list(maps) if maps is not None else ude.maps,
    )
  else:
    if name is None:
      raise ValueError("Either 'ude' or 'name' must be provided to create a new ude")
    new_ude = Ude(name=name, base=base, maps=list(maps) if maps is not None else [])
  header.udes.append(new_ude)


def add_udes(header: Header, udes: Iterable[Ude]) -> None:
  """
  Appends udes to the header.

  Parameters
  ----------
  header : Header
      The header to add udes to.
  udes : Iterable[Ude]
      An Iterable of `Ude` objects.

  Raises
  ------
  TypeError
      If `header` is not a `Header`.
  TypeError
      If any of the `udes` are not `Ude` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_udes
  >>> from PythonTmx.classes import Header, Ude, Map
  >>> header = Header(
  ...   creationtool="python-tmx",
  ...   creationtoolversion="0.3",
  ...   segtype="block",
  ...   tmf="Microsoft Translator",
  ...   adminlang="en",
  ...   srclang="en",
  ...   datatype="PlainText",
  ... )
  >>> add_udes(
  ...   header,
  ...   [
  ...     Ude(
  ...       name="ude1",
  ...       base="ude1",
  ...       maps=[Map(unicode="a", code="A", ent="A", subst="a")],
  ...     ),
  ...     Ude(
  ...       name="ude2",
  ...       base="ude2",
  ...       maps=[Map(unicode="b", code="B", ent="B", subst="b")],
  ...     ),
  ...   ],
  ... )
  >>> print(header.udes)
  [Ude(name='ude1', base='ude1', maps=[Map(unicode='a', code='A', ent='A', subst='a')]), Ude(name='ude2', base='ude2', maps=[Map(unicode='b', code='B', ent='B', subst='b')])]
  """

  if not isinstance(header, Header):
    raise TypeError("'header' must be a Header object")
  for ude in udes:
    if not isinstance(ude, Ude):
      raise TypeError(
        "'udes' must be an iterable of Ude objects but found a " f"{type(ude)} object"
      )
    add_ude(header, ude)


def add_map(
  ude: Ude,
  map: Map | None = None,
  *,
  unicode: str | None = None,
  code: str | None = None,
  ent: str | None = None,
  subst: str | None = None,
) -> None:
  """
  Appends a `Map` to the Ude.
  If `map` is None, a new map will be created with the provided arguments.
  if `map` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new map before it is added to the object.
  The original `map` is not modified.

  Parameters
  ----------
  ude : Ude
      A class that supports maps, namely `Ude`.
  map : Map | None, optional
      The map to add, by default None
  unicode : str | None, optional
      The unicode of the map, by default None
  code : str | None, optional
      The code of the map, by default None
  ent : str | None, optional
      The ent of the map, by default None
  subst : str | None, optional
      The subst of the map, by default None

  Raises
  ------
  TypeError
      If `ude` is not a `Ude`.
  TypeError
      If `map` is not a `Map` object.
  ValueError
      If `map` is None and `unicode` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_map
  >>> from PythonTmx.classes import Ude, Map
  >>> ude = Ude(name="ude1", base="ude1")
  >>> add_map(ude, unicode="a", code="A", ent="A", subst="a")
  >>> print(ude.maps)
  [Map(unicode='a', code='A', ent='A', subst='a')]
  """
  if not isinstance(ude, Ude):
    raise TypeError("'ude' must be a Ude object")
  if not isinstance(map, Map) and map is not None:
    raise TypeError("'map' must be a Map object")
  if map is not None:
    new_map = Map(
      unicode=unicode if unicode is not None else map.unicode,
      code=code if code is not None else map.code,
      ent=ent if ent is not None else map.ent,
      subst=subst if subst is not None else map.subst,
    )
  else:
    if unicode is None:
      raise ValueError("Either 'map' or 'unicode' must be provided to create a new map")
    new_map = Map(unicode=unicode, code=code, ent=ent, subst=subst)
  ude.maps.append(new_map)


def add_maps(ude: Ude, maps: Iterable[Map]) -> None:
  """
  Appends maps to the object.

  Parameters
  ----------
  ude : Ude
      A class that supports maps, namely `Ude`.
  maps : Iterable[Map]
      An Iterable of `Map` objects.

  Raises
  ------
  TypeError
      If `ude` is not a `Ude`.
  TypeError
      If any of the `maps` are not `Map` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_maps
  >>> from PythonTmx.classes import Ude, Map
  >>> ude = Ude(name="ude1", base="ude1")
  >>> add_maps(
  ...   ude,
  ...   [
  ...     Map(unicode="a", code="A", ent="A", subst="a"),
  ...     Map(unicode="b", code="B", ent="B", subst="b"),
  ...   ],
  ... )
  >>> print(ude.maps)
  [Map(unicode='a', code='A', ent='A', subst='a'), Map(unicode='b', code='B', ent='B', subst='b')]
  """
  if not isinstance(ude, Ude):
    raise TypeError("'ude' must be a Ude object")
  for map in maps:
    if not isinstance(map, Map):
      raise TypeError(
        "'maps' must be an iterable of Map objects but found a " f"{type(map)} object"
      )
    add_map(ude, map)


def add_tuv(
  tu: Tu,
  tuv: Tuv | None = None,
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
  notes: Iterable[Note] | None = None,
  props: Iterable[Prop] | None = None,
) -> None:
  """
  Appends a `Tuv` to the `Tu`.
  If `tuv` is None, a new tuv will be created with the provided arguments.
  if `tuv` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new tuv before it is added to the object.
  The original `tuv` is not modified.

  Parameters
  ----------
  tu : Tu
      The tu to add the tuv to.
  tuv : Tuv | None, optional
      The tuv to add, by default None
  segment : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut], optional
      The segment of the tuv, by default an empty list
  encoding : str | None, optional
      The encoding of the tuv, by default None
  datatype : str | None, optional
      The datatype of the tuv, by default None
  usagecount : str | int | None, optional
      The usagecount of the tuv, by default None
  lastusagedate : str | datetime | None, optional
      The lastusagedate of the tuv, by default None
  creationtool : str | None, optional
      The creationtool of the tuv, by default None
  creationtoolversion : str | None, optional
      The creationtoolversion of the tuv, by default None
  creationdate : str | datetime | None, optional
      The creationdate of the tuv, by default None
  creationid : str | None, optional
      The creationid of the tuv, by default None
  changedate : str | datetime | None, optional
      The changedate of the tuv, by default None
  changeid : str | None, optional
      The changeid of the tuv, by default None
  tmf : str | None, optional
      The tmf of the tuv, by default None
  notes : Iterable[Note] | None, optional
      The notes of the tuv, by default an empty list
  props : Iterable[Prop] | None, optional
      The props of the tuv, by default an empty list

  Raises
  ------
  TypeError
      If `tu` is not a `Tu`.
  TypeError
      If `tuv` is not a `Tuv` object.

  Examples
  --------
  >>> from PythonTmx.utils import add_tuv
  >>> from PythonTmx.classes import Tu, Tuv
  >>> tu = Tu()
  >>> add_tuv(tu, segment=["This is a segment"])
  >>> print(tu.tuvs)
  [Tuv(segment=['This is a segment'], encoding=None, datatype=None, usagecount=None, lastusagedate=None, creationtool=None, creationtoolversion=None, creationdate=None, creationid=None, changedate=None, changeid=None, tmf=None, notes=[], props=[])]
  """
  if not isinstance(tu, Tu):
    raise TypeError("'tu' must be a Tu object")
  if not isinstance(tuv, Tuv) and tuv is not None:
    raise TypeError("'tuv' must be a Tuv object")
  if tuv is not None:
    new_tuv = Tuv(
      segment=list(segment) if segment is not None else tuv.segment,
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
      notes=list(notes) if notes is not None else tuv.notes,
      props=list(props) if props is not None else tuv.props,
    )
  else:
    new_tuv = Tuv(
      segment=list(segment) if segment is not None else [],
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
      notes=list(notes) if notes is not None else [],
      props=list(props) if props is not None else [],
    )
  tu.tuvs.append(new_tuv)


def add_tuvs(tu: Tu, tuvs: Iterable[Tuv]) -> None:
  """
  Appends tuvs to the Tu.

  Parameters
  ----------
  tu : Tu
      The tu to add tuvs to.
  tuvs : Iterable[Tuv]
      An Iterable of `Tuv` objects.

  Raises
  ------
  TypeError
      If `tu` is not a `Tu`.
  TypeError
      If any of the `tuvs` are not `Tuv` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_tuvs
  >>> from PythonTmx.classes import Note, Prop, Tuv, Tu
  >>> tu = Tu()
  >>> add_tuvs(
  ...   tu,
  ...   [
  ...     Tuv(
  ...       segment=["This is a segment"],
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="1",
  ...       lastusagedate="20230301T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230301T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230301T000000Z",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       notes=[Note(text="This is a note", lang="en", encoding="UTF-8")],
  ...       props=[
  ...         Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8")
  ...       ],
  ...     ),
  ...     Tuv(
  ...       segment=["This is another segment"],
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="2",
  ...       lastusagedate="20230302T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230302T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230302T000000Z",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       notes=[Note(text="This is another note", lang="en", encoding="UTF-8")],
  ...       props=[
  ...         Prop(
  ...           text="This is another prop", type="type", lang="en", encoding="UTF-8"
  ...         )
  ...       ],
  ...     ),
  ...   ],
  ... )
  >>> print(tu.tuvs)
  [Tuv(segment=['This is a segment'], encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is a note', lang='en', encoding='UTF-8')], props=[Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8')]), Tuv(segment=['This is another segment'], encoding='UTF-8', datatype='PlainText', usagecount=2, lastusagedate=datetime.datetime(2023, 3, 2, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 2, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 2, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is another note', lang='en', encoding='UTF-8')], props=[Prop(text='This is another prop', type='type', lang='en', encoding='UTF-8')])]
  """
  if not isinstance(tu, Tu):
    raise TypeError("'tu' must be a Tu object")
  for tuv in tuvs:
    if not isinstance(tuv, Tuv):
      raise TypeError(
        "'tuvs' must be an iterable of Tuv objects but found a " f"{type(tuv)} object"
      )
    add_tuv(tu, tuv)


def add_tu(
  tmx: Tmx,
  tu: Tu | None = None,
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
  Appends a `Tu` to the Tmx.
  If `tu` is None, a new tu will be created with the provided arguments.
  if `tu` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new tu before it is added to the object.
  The original `tu` is not modified.

  Parameters
  ----------
  tmx : Tmx
      The tmx to add the tu to.
  tu : Tu | None, optional
      The tu to add, by default None
  tuid : str | None, optional
      The tuid of the tu, by default None
  encoding : str | None, optional
      The encoding of the tu, by default None
  datatype : str | None, optional
      The datatype of the tu, by default None
  usagecount : str | None, optional
      The usagecount of the tu, by default None
  lastusagedate : str | datetime | None, optional
      The lastusagedate of the tu, by default None
  creationtool : str | None, optional
      The creationtool of the tu, by default None
  creationtoolversion : str | None, optional
      The creationtoolversion of the tu, by default None
  creationdate : str | datetime | None, optional
      The creationdate of the tu, by default None
  creationid : str | None, optional
      The creationid of the tu, by default None
  changedate : str | datetime | None, optional
      The changedate of the tu, by default None
  segtype : Literal["block", "paragraph", "sentence", "phrase"] | None, optional
      The segtype of the tu, by default None
  changeid : str | None, optional
      The changeid of the tu, by default None
  tmf : str | None, optional
      The tmf of the tu, by default None
  srclang : str | None, optional
      The srclang of the tu, by default None
  tuvs : Iterable[Tuv] | None, optional
      The tuvs of the tu, by default an empty list
  notes : Iterable[Note] | None, optional
      The notes of the tu, by default an empty list
  props : Iterable[Prop] | None, optional
      The props of the tu, by default an empty list

  Raises
  ------
  TypeError
      If `tmx` is not a `Tmx`.
  TypeError
      If `tu` is not a `Tu` object.

  Examples
  --------
  >>> from PythonTmx.utils import add_tu
  >>> from PythonTmx.classes import Tmx, Tu, Tuv, Note, Prop
  >>> tmx = Tmx()
  >>> add_tu(
  ...   tmx,
  ...   tuid="tuid",
  ...   encoding="UTF-8",
  ...   datatype="PlainText",
  ...   usagecount="1",
  ...   lastusagedate="20230301T000000Z",
  ...   creationtool="python-tmx",
  ...   creationtoolversion="0.3",
  ...   creationdate="20230301T000000Z",
  ...   creationid="python-tmx",
  ...   changedate="20230301T000000Z",
  ...   segtype="block",
  ...   changeid="python-tmx",
  ...   tmf="Microsoft Translator",
  ...   srclang="en",
  ...   tuvs=[
  ...     Tuv(
  ...       segment=["This is a segment"],
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="1",
  ...       lastusagedate="20230301T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230301T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230301T000000Z",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       notes=[Note(text="This is a note", lang="en", encoding="UTF-8")],
  ...       props=[
  ...         Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8")
  ...       ],
  ...     ),
  ...     Tuv(
  ...       segment=["This is another segment"],
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="2",
  ...       lastusagedate="20230302T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230302T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230302T000000Z",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       notes=[Note(text="This is another note", lang="en", encoding="UTF-8")],
  ...       props=[
  ...         Prop(
  ...           text="This is another prop", type="type", lang="en", encoding="UTF-8"
  ...         )
  ...       ],
  ...     ),
  ...   ],
  ... )
  >>> print(tmx.tus)
  [Tu(tuid='tuid', encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), segtype='block', changeid='python-tmx', tmf='Microsoft Translator', srclang='en', tuvs=[Tuv(segment=['This is a segment'], encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is a note', lang='en', encoding='UTF-8')], props=[Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8')]), Tuv(segment=['This is another segment'], encoding='UTF-8', datatype='PlainText', usagecount=2, lastusagedate=datetime.datetime(2023, 3, 2, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 2, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 2, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is another note', lang='en', encoding='UTF-8')], props=[Prop(text='This is another prop', type='type', lang='en', encoding='UTF-8')])], notes=[], props=[])]
  """
  if not isinstance(tmx, Tmx):
    raise TypeError("'tmx' must be a Tmx object")
  if tu is not None:
    new_tu = Tu(
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
      tuvs=list(tuvs) if tuvs is not None else tu.tuvs,
      notes=list(notes) if notes is not None else tu.notes,
      props=list(props) if props is not None else tu.props,
    )
  else:
    new_tu = Tu(
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
      tuvs=list(tuvs) if tuvs is not None else [],
      notes=list(notes) if notes is not None else [],
      props=list(props) if props is not None else [],
    )
  tmx.tus.append(new_tu)


def add_tus(tmx: Tmx, tus: Iterable[Tu]) -> None:
  """
  Appends tus to the Tmx.

  Parameters
  ----------
  tmx : Tmx
      The tmx to add tus to.
  tus : Iterable[Tu]
      An Iterable of `Tu` objects.

  Raises
  ------
  TypeError
      If `tmx` is not a `Tmx`.
  TypeError
      If any of the `tus` are not `Tu` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_tus
  >>> from PythonTmx.classes import Tmx, Tu, Tuv, Note, Prop
  >>> tmx = Tmx()
  >>> add_tus(
  ...   tmx,
  ...   [
  ...     Tu(
  ...       tuid="tuid",
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="1",
  ...       lastusagedate="20230301T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230301T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230301T000000Z",
  ...       segtype="block",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       srclang="en",
  ...       tuvs=[
  ...         Tuv(
  ...           segment=["This is a segment"],
  ...           encoding="UTF-8",
  ...           datatype="PlainText",
  ...           usagecount="1",
  ...           lastusagedate="20230301T000000Z",
  ...           creationtool="python-tmx",
  ...           creationtoolversion="0.3",
  ...           creationdate="20230301T000000Z",
  ...           creationid="python-tmx",
  ...           changedate="20230301T000000Z",
  ...           changeid="python-tmx",
  ...           tmf="Microsoft Translator",
  ...           notes=[Note(text="This is a note", lang="en", encoding="UTF-8")],
  ...           props=[
  ...             Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8")
  ...           ],
  ...         ),
  ...         Tuv(
  ...           segment=["This is another segment"],
  ...           encoding="UTF-8",
  ...           datatype="PlainText",
  ...           usagecount="2",
  ...           lastusagedate="20230302T000000Z",
  ...           creationtool="python-tmx",
  ...           creationtoolversion="0.3",
  ...           creationdate="20230302T000000Z",
  ...           creationid="python-tmx",
  ...           changedate="20230302T000000Z",
  ...           changeid="python-tmx",
  ...           tmf="Microsoft Translator",
  ...           notes=[Note(text="This is another note", lang="en", encoding="UTF-8")],
  ...           props=[
  ...             Prop(
  ...               text="This is another prop",
  ...               type="type",
  ...               lang="en",
  ...               encoding="UTF-8",
  ...             )
  ...           ],
  ...         ),
  ...       ],
  ...       notes=[],
  ...       props=[],
  ...     ),
  ...     Tu(
  ...       tuid="tuid",
  ...       encoding="UTF-8",
  ...       datatype="PlainText",
  ...       usagecount="1",
  ...       lastusagedate="20230301T000000Z",
  ...       creationtool="python-tmx",
  ...       creationtoolversion="0.3",
  ...       creationdate="20230301T000000Z",
  ...       creationid="python-tmx",
  ...       changedate="20230301T000000Z",
  ...       segtype="block",
  ...       changeid="python-tmx",
  ...       tmf="Microsoft Translator",
  ...       srclang="en",
  ...       tuvs=[
  ...         Tuv(
  ...           segment=["This is a segment"],
  ...           encoding="UTF-8",
  ...           datatype="PlainText",
  ...           usagecount="1",
  ...           lastusagedate="20230301T000000Z",
  ...           creationtool="python-tmx",
  ...           creationtoolversion="0.3",
  ...           creationdate="20230301T000000Z",
  ...           creationid="python-tmx",
  ...           changedate="20230301T000000Z",
  ...           changeid="python-tmx",
  ...           tmf="Microsoft Translator",
  ...           notes=[Note(text="This is a note", lang="en", encoding="UTF-8")],
  ...           props=[
  ...             Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8")
  ...           ],
  ...         ),
  ...         Tuv(
  ...           segment=["This is another segment"],
  ...           encoding="UTF-8",
  ...           datatype="PlainText",
  ...           usagecount="2",
  ...           lastusagedate="20230302T000000Z",
  ...           creationtool="python-tmx",
  ...           creationtoolversion="0.3",
  ...           creationdate="20230302T000000Z",
  ...           creationid="python-tmx",
  ...           changedate="20230302T000000Z",
  ...           changeid="python-tmx",
  ...           tmf="Microsoft Translator",
  ...           notes=[Note(text="This is another note", lang="en", encoding="UTF-8")],
  ...           props=[
  ...             Prop(
  ...               text="This is another prop",
  ...               type="type",
  ...               lang="en",
  ...               encoding="UTF-8",
  ...             )
  ...           ],
  ...         ),
  ...       ],
  ...       notes=[],
  ...       props=[],
  ...     ),
  ...   ],
  ... )
  >>> print(tmx.tus)
  [Tu(tuid='tuid', encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), segtype='block', changeid='python-tmx', tmf='Microsoft Translator', srclang='en', tuvs=[Tuv(segment=['This is a segment'], encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is a note', lang='en', encoding='UTF-8')], props=[Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8')]), Tuv(segment=['This is another segment'], encoding='UTF-8', datatype='PlainText', usagecount=2, lastusagedate=datetime.datetime(2023, 3, 2, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 2, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 2, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is another note', lang='en', encoding='UTF-8')], props=[Prop(text='This is another prop', type='type', lang='en', encoding='UTF-8')])], notes=[], props=[]), Tu(tuid='tuid', encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), segtype='block', changeid='python-tmx', tmf='Microsoft Translator', srclang='en', tuvs=[Tuv(segment=['This is a segment'], encoding='UTF-8', datatype='PlainText', usagecount=1, lastusagedate=datetime.datetime(2023, 3, 1, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is a note', lang='en', encoding='UTF-8')], props=[Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8')]), Tuv(segment=['This is another segment'], encoding='UTF-8', datatype='PlainText', usagecount=2, lastusagedate=datetime.datetime(2023, 3, 2, 0, 0), creationtool='python-tmx', creationtoolversion='0.3', creationdate=datetime.datetime(2023, 3, 2, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 2, 0, 0), changeid='python-tmx', tmf='Microsoft Translator', notes=[Note(text='This is another note', lang='en', encoding='UTF-8')], props=[Prop(text='This is another prop', type='type', lang='en', encoding='UTF-8')])], notes=[], props=[])]
  """
  if not isinstance(tmx, Tmx):
    raise TypeError("'tmx' must be a Tmx object")
  for tu in tus:
    if not isinstance(tu, Tu):
      raise TypeError(
        "'tus' must be an iterable of Tu objects but found a " f"{type(tu)} object"
      )
    add_tu(tmx, tu)


def add_header(
  tmx: Tmx,
  header: Header | None = None,
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
  udes: Iterable[Ude] | None = None,
  notes: Iterable[Note] | None = None,
  props: Iterable[Prop] | None = None,
) -> None:
  """
  Appends a `Header` to the Tmx.
  If `header` is None, a new header will be created with the provided arguments.
  if `header` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new header before it is added to the object.
  The original `header` is not modified.

  Parameters
  ----------
  tmx : Tmx
      The tmx to add the header to.
  header : Header | None, optional
      The header to add, by default None
  creationtool : str | None, optional
      The creationtool of the header, by default None
  creationtoolversion : str | None, optional
      The creationtoolversion of the header, by default None
  segtype : Literal["block", "paragraph", "sentence", "phrase"] | None, optional
      The segtype of the header, by default None
  tmf : str | None, optional
      The tmf of the header, by default None
  adminlang : str | None, optional
      The adminlang of the header, by default None
  srclang : str | None, optional
      The srclang of the header, by default None
  datatype : str | None, optional
      The datatype of the header, by default None
  encoding : str | None, optional
      The encoding of the header, by default None
  creationdate : str | datetime | None, optional
      The creationdate of the header, by default None
  creationid : str | None, optional
      The creationid of the header, by default None
  changedate : str | datetime | None, optional
      The changedate of the header, by default None
  changeid : str | None, optional
      The changeid of the header, by default None
  udes : Iterable[Ude] | None, optional
      The udes of the header, by default an empty list
  notes : Iterable[Note] | None, optional
      The notes of the header, by default an empty list
  props : Iterable[Prop] | None, optional
      The props of the header, by default an empty list

  Raises
  ------
  TypeError
      If `tmx` is not a `Tmx`.
  TypeError
      If `header` is not a `Header` object.
  TypeError
      If `header` is None and any of the required arguments are None.
  ValueError
      if Tmx.header is not None

  Examples
  --------
  >>> from PythonTmx.utils import add_header
  >>> from PythonTmx.classes import Tmx, Header, Note, Prop
  >>> tmx = Tmx()
  >>> add_header(
  ...   tmx,
  ...   creationtool="python-tmx",
  ...   creationtoolversion="0.3",
  ...   segtype="block",
  ...   tmf="Microsoft Translator",
  ...   adminlang="en",
  ...   srclang="en",
  ...   datatype="PlainText",
  ...   encoding="UTF-8",
  ...   creationdate="20230301T000000Z",
  ...   creationid="python-tmx",
  ...   changedate="20230301T000000Z",
  ...   changeid="python-tmx",
  ...   notes=[Note(text="This is a note", lang="en", encoding="UTF-8")],
  ...   props=[Prop(text="This is a prop", type="type", lang="en", encoding="UTF-8")],
  ...   udes=[
  ...     Ude(
  ...       name="ude1",
  ...       base="ude1",
  ...       maps=[Map(unicode="a", code="A", ent="A", subst="a")],
  ...     ),
  ...     Ude(
  ...       name="ude2",
  ...       base="ude2",
  ...       maps=[Map(unicode="b", code="B", ent="B", subst="b")],
  ...     ),
  ... )
  >>> print(tmx.header)
  Header(creationtool='python-tmx', creationtoolversion='0.3', segtype='block', tmf='Microsoft Translator', adminlang='en', srclang='en', datatype='PlainText', encoding='UTF-8', creationdate=datetime.datetime(2023, 3, 1, 0, 0), creationid='python-tmx', changedate=datetime.datetime(2023, 3, 1, 0, 0), changeid='python-tmx', notes=[Note(text='This is a note', lang='en', encoding='UTF-8')], props=[Prop(text='This is a prop', type='type', lang='en', encoding='UTF-8')])
  """
  if not isinstance(tmx, Tmx):
    raise TypeError("'tmx' must be a Tmx object")
  if tmx.header is not None:
    raise ValueError(
      "Cannot add a new header to a Tmx object that already has a header"
    )
  if not isinstance(header, Header) and header is not None:
    raise TypeError("'header' must be a Header object")
  if header is not None:
    new_header = Header(
      creationtool=creationtool if creationtool is not None else header.creationtool,
      creationtoolversion=creationtoolversion
      if creationtoolversion is not None
      else header.creationtoolversion,
      segtype=segtype if segtype is not None else header.segtype,
      tmf=tmf if tmf is not None else header.tmf,
      adminlang=adminlang if adminlang is not None else header.adminlang,
      srclang=srclang if srclang is not None else header.srclang,
      datatype=datatype if datatype is not None else header.datatype,
      encoding=encoding if encoding is not None else header.encoding,
      creationdate=creationdate if creationdate is not None else header.creationdate,
      creationid=creationid if creationid is not None else header.creationid,
      changedate=changedate if changedate is not None else header.changedate,
      changeid=changeid if changeid is not None else header.changeid,
      notes=list(notes) if notes is not None else header.notes,
      props=list(props) if props is not None else header.props,
    )
  else:
    if any(
      arg is None
      for arg in (
        creationtool,
        creationtoolversion,
        segtype,
        tmf,
        adminlang,
        srclang,
        datatype,
      )
    ):
      raise TypeError(
        "Either 'header' or all of the required arguments must be provided to create a new header"
      )
    new_header = Header(
      creationtool=creationtool,  # type: ignore
      creationtoolversion=creationtoolversion,  # type: ignore
      segtype=segtype,  # type: ignore
      tmf=tmf,  # type: ignore
      adminlang=adminlang,  # type: ignore
      srclang=srclang,  # type: ignore
      datatype=datatype,  # type: ignore
      encoding=encoding,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      changeid=changeid,
      udes=list(udes) if udes is not None else [],
      notes=list(notes) if notes is not None else [],
      props=list(props) if props is not None else [],
    )
  tmx.header = new_header


def add_bpt(
  obj: SupportsBpt,
  bpt: Bpt | None = None,
  *,
  i: int | str | None = None,
  x: int | str | None = None,
  type: str | None = None,
  content: Iterable[str | Sub] | None = None,
) -> None:
  """
  Appends a `Bpt` to the object if it supports bpts.
  If `bpt` is None, a new bpt will be created with the provided arguments.
  if `bpt` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new bpt before it is added to the object.
  The original `bpt` is not modified.

  Parameters
  ----------
  obj : SupportsBpt
      A class that supports Tuv, Hi, Sub.
  bpt : Bpt | None, optional
      The bpt to add, by default None
  i : int | str | None, optional
      The i of the bpt, by default None
  x : int | str | None, optional
      The x of the bpt, by default None
  type : str | None, optional
      The type of the bpt, by default None
  content : Iterable[str | Sub] | None, optional
      The content of the bpt, by default an empty list

  Raises
  ------
  TypeError
      If `obj` does not support Bpt objects.
  TypeError
      If `bpt` is not a `Bpt` object.
  ValueError
      If `bpt` is None and any of the required arguments are None.

  Examples
  --------
  >>> from PythonTmx.utils import add_bpt
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_bpt(tuv, i="1", x="1", type="bpt", content=["This is a bpt"])
  >>> print(tuv.segment)
  ['This is a segment', Bpt(i=1, x=1, type='bpt', content=['This is a bpt'])]
  """
  if not isinstance(obj, SupportsBpt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(bpt, Bpt) and bpt is not None:
    raise TypeError("'bpt' must be a Bpt object")
  if bpt is not None:
    new_bpt = Bpt(
      i=i if i is not None else bpt.i,
      x=x if x is not None else bpt.x,
      type=type if type is not None else bpt.type,
      content=list(content) if content is not None else bpt.content,
    )
  else:
    if i is None:
      raise ValueError("Either 'bpt' or 'i' must be provided to create a new bpt")
    new_bpt = Bpt(
      i=i, x=x, type=type, content=list(content) if content is not None else []
    )
  if isinstance(obj, Tuv):
    obj.segment.append(new_bpt)
  else:
    obj.content.append(new_bpt)


def add_bpts(obj: SupportsBpt, bpts: Iterable[Bpt]) -> None:
  """
  Appends bpts to the object.

  Parameters
  ----------
  obj : SupportsBpt
      A class that supports Bpt objects, namely Tuv, Hi, Sub.
  bpts : Iterable[Bpt]
      An Iterable of `Bpt` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `bpts` are not `Bpt` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_bpts
  >>> from PythonTmx.classes import Bpt, Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_bpts(
  ...   tuv,
  ...   [
  ...     Bpt(i="1", x="1", type="bpt", content=["This is a bpt"]),
  ...     Bpt(i="2", x="2", type="bpt", content=["This is another bpt"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', Bpt(i=1, x=1, type='bpt', content=['This is a bpt']), Bpt(i=2, x=2, type='bpt', content=['This is another bpt'])]
  """
  if not isinstance(obj, SupportsBpt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for bpt in bpts:
    if not isinstance(bpt, Bpt):
      raise TypeError(
        "'bpts' must be an iterable of Bpt objects but found a " f"{type(bpt)} object"
      )
    add_bpt(obj, bpt)


def add_ept(
  obj: SupportsEpt,
  ept: Ept | None = None,
  *,
  i: int | str | None = None,
  content: Iterable[str | Sub] | None = None,
) -> None:
  """
  Appends a `Ept` to the object if it supports epts.
  If `ept` is None, a new ept will be created with the provided arguments.
  if `ept` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new ept before it is added to the object.
  The original `ept` is not modified.

  Parameters
  ----------
  obj : SupportsEpt
      A class that supports epts, namely Tuv, Hi, Sub.
  ept : Ept | None, optional
      The ept to add, by default None
  i : int | str | None, optional
      The i of the ept, by default None
  content : Iterable[str | Sub] | None, optional
      The content of the ept, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `ept` is not a `Ept` object.
  ValueError
      If `ept` is None and `i` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_ept
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_ept(tuv, i="1", content=["This is a ept"])
  >>> print(tuv.segment)
  ['This is a segment', Ept(i=1, content=['This is a ept'])]
  """
  if not isinstance(obj, SupportsEpt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(ept, Ept) and ept is not None:
    raise TypeError("'ept' must be a Ept object")
  if ept is not None:
    new_ept = Ept(
      i=i if i is not None else ept.i,
      content=list(content) if content is not None else ept.content,
    )
  else:
    if i is None:
      raise ValueError("Either 'ept' or 'i' must be provided to create a new ept")
    new_ept = Ept(i=i, content=list(content) if content is not None else [])
  if isinstance(obj, Tuv):
    obj.segment.append(new_ept)
  else:
    obj.content.append(new_ept)


def add_epts(obj: SupportsEpt, epts: Iterable[Ept]) -> None:
  """
  Appends epts to the object.

  Parameters
  ----------
  obj : SupportsEpt
      A class that supports epts, namely Tuv, Hi, Sub.
  epts : Iterable[Ept]
      An Iterable of `Ept` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `epts` are not `Ept` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_epts
  >>> from PythonTmx.classes import Ept, Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_epts(
  ...   tuv,
  ...   [
  ...     Ept(i="1", content=["This is a ept"]),
  ...     Ept(i="2", content=["This is another ept"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', Ept(i=1, content=['This is a ept']), Ept(i=2, content=['This is another ept'])]
  """
  if not isinstance(obj, SupportsEpt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for ept in epts:
    if not isinstance(ept, Ept):
      raise TypeError(
        "'epts' must be an iterable of Ept objects but found a " f"{type(ept)} object"
      )
    add_ept(obj, ept)


def add_hi(
  obj: SupportsHi,
  hi: Hi | None = None,
  *,
  x: int | str | None = None,
  type: str | None = None,
  content: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
) -> None:
  """
  Appends a `Hi` to the object if it supports hi.
  If `hi` is None, a new hi will be created with the provided arguments.
  if `hi` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new hi before it is added to the object.
  The original `hi` is not modified.

  Parameters
  ----------
  obj : SupportsHi
      A class that supports hi, namely Tuv, Hi, Sub.
  hi : Hi | None, optional
      The hi to add, by default None
  x : int | str | None, optional
      The x of the hi, by default None
  type : str | None, optional
      The type of the hi, by default None
  content : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None, optional
      The content of the hi, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `hi` is not a `Hi` object.
  ValueError
      If `hi` is None and `x` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_hi
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_hi(tuv, x="1", type="hi", content=["This is a hi"])
  >>> print(tuv.segment)
  ['This is a segment', Hi(x=1, type='hi', content=['This is a hi'])]
  """
  if not isinstance(obj, SupportsHi):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(hi, Hi) and hi is not None:
    raise TypeError("'hi' must be a Hi object")
  if hi is not None:
    new_hi = Hi(
      x=x if x is not None else hi.x,
      type=type if type is not None else hi.type,
      content=list(content) if content is not None else hi.content,
    )
  else:
    if x is None:
      raise ValueError("Either 'hi' or 'x' must be provided to create a new hi")
    new_hi = Hi(x=x, type=type, content=list(content) if content is not None else [])
  if isinstance(obj, Tuv):
    obj.segment.append(new_hi)
  else:
    obj.content.append(new_hi)


def add_his(obj: SupportsHi, his: Iterable[Hi]) -> None:
  """
  Appends his to the object.

  Parameters
  ----------
  obj : SupportsHi
      A class that supports hi, namely Tuv, Hi, Sub.
  his : Iterable[Hi]
      An Iterable of `Hi` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `his` are not `Hi` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_his
  >>> from PythonTmx.classes import Tuv, Hi
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_his(
  ...   tuv,
  ...   [
  ...     Hi(x="1", type="hi", content=["This is a hi"]),
  ...     Hi(x="2", type="hi", content=["This is another hi"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', Hi(x=1, type='hi', content=['This is a hi']), Hi(x=2, type='hi', content=['This is another hi'])]
  """
  if not isinstance(obj, SupportsHi):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for hi in his:
    if not isinstance(hi, Hi):
      raise TypeError(
        "'his' must be an iterable of Hi objects but found a " f"{type(hi)} object"
      )
    add_hi(obj, hi)


def add_it(
  obj: SupportsIt,
  it: It | None = None,
  *,
  pos: Literal["begin", "end"] | None = None,
  x: int | str | None = None,
  type: str | None = None,
  content: Iterable[str | Sub] | None = None,
) -> None:
  """
  Appends a `It` to the object if it supports its.
  If `it` is None, a new it will be created with the provided arguments.
  if `it` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new it before it is added to the object.
  The original `it` is not modified.

  Parameters
  ----------
  obj : SupportsIt
      A class that supports its, namely Tuv, Hi, Sub.
  it : It | None, optional
      The it to add, by default None
  pos : Literal["begin", "end"] | None, optional
      The pos of the it, by default None
  x : int | str | None, optional
      The x of the it, by default None
  type : str | None, optional
      The type of the it, by default None
  content : Iterable[str | Sub] | None, optional
      The content of the it, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `it` is not a `It` object.
  ValueError
      If `it` is None and `pos` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_it
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_it(tuv, pos="begin", x="1", type="it", content=["This is a it"])
  >>> print(tuv.segment)
  ['This is a segment', It(pos='begin', x=1, type='it', content=['This is a it'])]
  """
  if not isinstance(obj, SupportsIt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(it, It) and it is not None:
    raise TypeError("'it' must be a It object")
  if it is not None:
    new_it = It(
      pos=pos if pos is not None else it.pos,
      x=x if x is not None else it.x,
      type=type if type is not None else it.type,
      content=list(content) if content is not None else it.content,
    )
  else:
    if pos is None:
      raise ValueError("Either 'it' or 'pos' must be provided to create a new it")
    new_it = It(
      pos=pos, x=x, type=type, content=list(content) if content is not None else []
    )
  if isinstance(obj, Tuv):
    obj.segment.append(new_it)
  else:
    obj.content.append(new_it)


def add_its(obj: SupportsIt, its: Iterable[It]) -> None:
  """
  Appends its to the object.

  Parameters
  ----------
  obj : SupportsIt
      A class that supports its, namely Tuv, Hi, Sub.
  its : Iterable[It]
      An Iterable of `It` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `its` are not `It` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_its
  >>> from PythonTmx.classes import It, Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_its(
  ...   tuv,
  ...   [
  ...     It(pos="begin", x="1", type="it", content=["This is a it"]),
  ...     It(pos="end", x="2", type="it", content=["This is another it"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', It(pos='begin', x=1, type='it', content=['This is a it']), It(pos='end', x=2, type='it', content=['This is another it'])]
  """
  if not isinstance(obj, SupportsIt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for it in its:
    if not isinstance(it, It):
      raise TypeError(
        "'its' must be an iterable of It objects but found a " f"{type(it)} object"
      )
    add_it(obj, it)


def add_ph(
  obj: SupportsPh,
  ph: Ph | None = None,
  *,
  x: int | str | None = None,
  assoc: Literal["p", "f", "b"] | None = None,
  content: Iterable[str | Sub] | None = None,
) -> None:
  """
  Appends a `Ph` to the object if it supports phs.
  If `ph` is None, a new ph will be created with the provided arguments.
  if `ph` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new ph before it is added to the object.
  The original `ph` is not modified.

  Parameters
  ----------
  obj : SupportsPh
      A class that supports phs, namely Tuv, Hi, Sub.
  ph : Ph | None, optional
      The ph to add, by default None
  x : int | str | None, optional
      The x of the ph, by default None
  assoc : Literal["p", "f", "b"] | None, optional
      The assoc of the ph, by default None
  content : Iterable[str | Sub] | None, optional
      The content of the ph, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `ph` is not a `Ph` object.
  ValueError
      If `ph` is None and `x` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_ph
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_ph(tuv, x="1", assoc="p", content=["This is a ph"])
  >>> print(tuv.segment)
  ['This is a segment', Ph(i=None, x=1, assoc='p', content=['This is a ph'])]
  """
  if not isinstance(obj, SupportsPh):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(ph, Ph) and ph is not None:
    raise TypeError("'ph' must be a Ph object")
  if ph is not None:
    new_ph = Ph(
      x=x if x is not None else ph.x,
      assoc=assoc if assoc is not None else ph.assoc,
      content=list(content) if content is not None else ph.content,
    )
  else:
    if x is None:
      raise ValueError("Either 'ph' or 'x' must be provided to create a new ph")
    new_ph = Ph(x=x, assoc=assoc, content=list(content) if content is not None else [])
  if isinstance(obj, Tuv):
    obj.segment.append(new_ph)
  else:
    obj.content.append(new_ph)


def add_phs(obj: SupportsPh, phs: Iterable[Ph]) -> None:
  """
  Appends phs to the object.

  Parameters
  ----------
  obj : SupportsPh
      A class that supports phs, namely Tuv, Hi, Sub.
  phs : Iterable[Ph]
      An Iterable of `Ph` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `phs` are not `Ph` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_phs
  >>> from PythonTmx.classes import Ph, Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_phs(
  ...   tuv,
  ...   [
  ...     Ph(x="1", assoc="p", content=["This is a ph"]),
  ...     Ph(x="2", assoc="p", content=["This is another ph"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', Ph(i=None, x=1, assoc='p', content=['This is a ph']), Ph(i=None, x=2, assoc='p', content=['This is another ph'])]
  """
  if not isinstance(obj, SupportsPh):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for ph in phs:
    if not isinstance(ph, Ph):
      raise TypeError(
        "'phs' must be an iterable of Ph objects but found a " f"{type(ph)} object"
      )
    add_ph(obj, ph)


def add_ut(
  obj: SupportsUt,
  ut: Ut | None = None,
  *,
  x: int | str | None = None,
  content: Iterable[str | Sub] | None = None,
) -> None:
  """
  Appends a `Ut` to the object if it supports uts.
  If `ut` is None, a new ut will be created with the provided arguments.
  if `ut` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new ut before it is added to the object.
  The original `ut` is not modified.

  Parameters
  ----------
  obj : SupportsUt
      A class that supports uts, namely Tuv, Hi, Sub.
  ut : Ut | None, optional
      The ut to add, by default None
  x : int | str | None, optional
      The x of the ut, by default None
  content : Iterable[str | Sub] | None, optional
      The content of the ut, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `ut` is not a `Ut` object.
  ValueError
      If `ut` is None and `x` is None.

  Examples
  --------
  >>> from PythonTmx.utils import add_ut
  >>> from PythonTmx.classes import Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_ut(tuv, x="1", content=["This is a ut"])
  >>> print(tuv.segment)
  ['This is a segment', Ut(x=1, content=['This is a ut'])]
  """
  if not isinstance(obj, SupportsUt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  if not isinstance(ut, Ut) and ut is not None:
    raise TypeError("'ut' must be a Ut object")
  if ut is not None:
    new_ut = Ut(
      x=x if x is not None else ut.x,
      content=list(content) if content is not None else ut.content,
    )
  else:
    if x is None:
      raise ValueError("Either 'ut' or 'x' must be provided to create a new ut")
    new_ut = Ut(x=x, content=list(content) if content is not None else [])
  if isinstance(obj, Tuv):
    obj.segment.append(new_ut)
  else:
    obj.content.append(new_ut)


def add_uts(obj: SupportsUt, uts: Iterable[Ut]) -> None:
  """
  Appends uts to the object.

  Parameters
  ----------
  obj : SupportsUt
      A class that supports uts, namely Tuv, Hi, Sub.
  uts : Iterable[Ut]
      An Iterable of `Ut` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `uts` are not `Ut` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_uts
  >>> from PythonTmx.classes import Ut, Tuv
  >>> tuv = Tuv(segment=["This is a segment"])
  >>> add_uts(
  ...   tuv,
  ...   [
  ...     Ut(x="1", content=["This is a ut"]),
  ...     Ut(x="2", content=["This is another ut"]),
  ...   ],
  ... )
  >>> print(tuv.segment)
  ['This is a segment', Ut(x=1, content=['This is a ut']), Ut(x=2, content=['This is another ut'])]
  """
  if not isinstance(obj, SupportsUt):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for ut in uts:
    if not isinstance(ut, Ut):
      raise TypeError(
        "'uts' must be an iterable of Ut objects but found a " f"{type(ut)} object"
      )
    add_ut(obj, ut)


def add_sub(
  obj: SupportsSub,
  sub: Sub | None = None,
  *,
  type: str | None = None,
  datatype: str | None = None,
  content: Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None = None,
) -> None:
  """
  Appends a `Sub` to the object if it supports subs.
  If `sub` is None, a new sub will be created with the provided arguments.
  if `sub` is not None and any of the arguments are not None, the provided
  arguments will be used to update the new sub before it is added to the object.
  The original `sub` is not modified.

  Parameters
  ----------
  obj : SupportsSub
      A class that supports subs, namely Tuv, Hi, Sub.
  sub : Sub | None, optional
      The sub to add, by default None
  type : str | None, optional
      The type of the sub, by default None
  datatype : str | None, optional
      The datatype of the sub, by default None
  content : Iterable[str | Bpt | Ept | It | Ph | Hi | Ut] | None, optional
      The content of the sub, by default an empty list

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If `sub` is not a `Sub` object.
  ValueError
      If `sub` is None and any of the required arguments are None.

  Examples
  --------
  >>> from PythonTmx.utils import add_sub
  >>> from PythonTmx.classes import Bpt
  >>> bpt = Bpt(i="1", x="1", type="bpt", content=["This is a bpt"])
  >>> add_sub(bpt, type="sub", datatype="PlainText", content=["This is a sub"])
  >>> print(bpt.content)
  ['This is a bpt', Sub(type='sub', datatype='PlainText', content=['This is a sub'])]
  """
  if not isinstance(obj, SupportsSub):
    raise TypeError("'obj' must be one of Bpt, Ept, It, Ph, Ut")
  if not isinstance(sub, Sub) and sub is not None:
    raise TypeError("'sub' must be a Sub object")
  if sub is not None:
    new_sub = Sub(
      type=type if type is not None else sub.type,
      datatype=datatype if datatype is not None else sub.datatype,
      content=list(content) if content is not None else sub.content,
    )
  else:
    if any(
      arg is None
      for arg in (
        type,
        datatype,
      )
    ):
      raise TypeError(
        "Either 'sub' or all of the required arguments must be provided to create a new sub"
      )
    new_sub = Sub(
      type=type, datatype=datatype, content=list(content) if content is not None else []
    )
  if isinstance(obj, Tuv):
    obj.segment.append(new_sub)
  else:
    obj.content.append(new_sub)


def add_subs(obj: SupportsSub, subs: Iterable[Sub]) -> None:
  """
  Appends subs to the object.

  Parameters
  ----------
  obj : SupportsSub
      A class that supports subs, namely Tuv, Hi, Sub.
  subs : Iterable[Sub]
      An Iterable of `Sub` objects.

  Raises
  ------
  TypeError
      If `obj` is not a `Bpt` object.
  TypeError
      If any of the `subs` are not `Sub` objects.

  Examples
  --------
  >>> from PythonTmx.utils import add_subs
  >>> from PythonTmx.classes import Sub, Bpt
  >>> bpt = Bpt(i="1", x="1", type="bpt", content=["This is a bpt"])
  >>> add_subs(
  ...   bpt,
  ...   [
  ...     Sub(type="sub", datatype="PlainText", content=["This is a sub"]),
  ...     Sub(type="sub", datatype="PlainText", content=["This is another sub"]),
  ...   ],
  ... )
  >>> print(bpt.content)
  ['This is a bpt', Sub(type='sub', datatype='PlainText', content=['This is a sub']), Sub(type='sub', datatype='PlainText', content=['This is another sub'])]
  """
  if not isinstance(obj, SupportsSub):
    raise TypeError("'obj' must be one of Tuv, Hi, Sub")
  for sub in subs:
    if not isinstance(sub, Sub):
      raise TypeError(
        "'subs' must be an iterable of Sub objects but found a " f"{type(sub)} object"
      )
    add_sub(obj, sub)
