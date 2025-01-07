from __future__ import annotations

import datetime as dt
from collections.abc import MutableSequence
from dataclasses import dataclass, field
from enum import Enum
from functools import partial

from PythonTmx.utils import _try_parse_dt


def add_map(target: Ude, _map: Map) -> None:
  """
  Adds the give :class:`Map` object to the target :class:`Ude` object.

  The :class:`Map` is appended to the :attr:`~Ude.maps` attribute.

  If the target is not a :class:`Ude` object or :param:`_map` is not a
  :class:`Map`, a TypeError will be raised.

  Parameters
  ----------
  target : Ude
      The :class:`Ude` to add the :class:`Map` to.
  _map : Map
      The :class:`Map` to add to the target.

  Raises
  ------
  TypeError
      If the :param:`target` is not a :class:`Ude` object or :param:`_map` is
      not a :class:`Map` object.

  """
  if not isinstance(target, Ude):
    raise TypeError(f"target must be a Ude object, not {type(target)}")
  if not isinstance(_map, Map):
    raise TypeError(f"_map must be a Map object, not {type(_map)}")
  target.maps.append(_map)


class SEGTYPE(Enum):
  BLOCK: str = "block"
  PARAGRAPH: str = "paragraph"
  SENTENCE: str = "sentence"
  PHRASE: str = "phrase"


class POS(Enum):
  BEGIN: str = "begin"
  END: str = "end"


class ASSOC(Enum):
  P: str = "p"
  F: str = "f"
  B: str = "b"


@dataclass
class Note:
  text: str
  lang: str | None = None
  encoding: str | None = None


@dataclass
class Prop:
  text: str
  type: str
  lang: str | None = None
  encoding: str | None = None


@dataclass
class Map:
  unicode: str
  code: str | None = None
  ent: str | None = None
  subst: str | None = None


@dataclass
class Ude:
  name: str
  base: str | None = None
  maps: MutableSequence[Map] = field(default_factory=list)

  def __post_init__(self):
    self.add_map = partial(add_map, target=self)
    self.add_map.__doc__ = (
      "Partial application of :func:`add_map` with the target set to self.\n"
      + add_map.__doc__
    )


@dataclass
class Header:
  creationtool: str
  creationtoolversion: str
  segtype: SEGTYPE
  tmf: str
  adminlang: str
  srclang: str
  datatype: str
  encoding: str | None = None
  creationdate: str | dt.datetime | None = None
  creationid: str | None = None
  changedate: str | dt.datetime | None = None
  changeid: str | None = None
  notes: MutableSequence[Note] = field(default_factory=list)
  props: MutableSequence[Prop] = field(default_factory=list)
  udes: MutableSequence[Ude] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.creationdate, str):
      self.creationdate = _try_parse_dt(self.creationdate)
    if isinstance(self.changedate, str):
      self.changedate = _try_parse_dt(self.changedate)


@dataclass
class Tuv:
  lang: str
  segment: MutableSequence[str] = field(default_factory=list)
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: str | dt.datetime | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | dt.datetime | None = None
  creationid: str | None = None
  changedate: str | dt.datetime | None = None
  tmf: str | None = None
  changeid: str | None = None
  notes: MutableSequence[str] = field(default_factory=list)
  props: MutableSequence[str] = field(default_factory=list)

  def __post_init__(self):
    if isinstance(self.creationdate, str):
      self.creationdate = _try_parse_dt(self.creationdate)
    if isinstance(self.changedate, str):
      self.changedate = _try_parse_dt(self.changedate)
    if isinstance(self.lastusagedate, str):
      self.lastusagedate = _try_parse_dt(self.lastusagedate)


@dataclass
class Tu:
  tuvs: MutableSequence[Tuv] = field(default_factory=list)
  notes: MutableSequence[Note] = field(default_factory=list)
  props: MutableSequence[Prop] = field(default_factory=list)
  tuid: str | None = None
  encoding: str | None = None
  datatype: str | None = None
  usagecount: str | None = None
  lastusagedate: str | None = None
  creationtool: str | None = None
  creationtoolversion: str | None = None
  creationdate: str | None = None
  creationid: str | None = None
  changedate: str | None = None
  segtype: SEGTYPE | None = None
  changeid: str | None = None
  tmf: str | None = None
  srclang: str | None = None


@dataclass
class Tmx:
  header: Header
  tus: MutableSequence[Tu] = field(default_factory=list)


@dataclass
class Sub:
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list
  )
  type: str | None = None
  datatype: str | None = None


@dataclass
class Bpt:
  i: int
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  type: str | None = None


@dataclass
class Ept:
  i: int
  content: MutableSequence[str | Sub] = field(default_factory=list)


@dataclass
class It:
  pos: POS
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  type: str | None = None


@dataclass
class Ph:
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
  assoc: ASSOC | None = None
  type: str | None = None


@dataclass
class Hi:
  content: MutableSequence[str | Bpt | Ept | It | Ph | Hi | Ut] = field(
    default_factory=list
  )
  x: int | None = None
  type: str | None = None


@dataclass
class Ut:
  content: MutableSequence[str | Sub] = field(default_factory=list)
  x: int | None = None
