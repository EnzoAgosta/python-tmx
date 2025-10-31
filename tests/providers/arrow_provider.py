from collections import OrderedDict
from typing import Any

from faker import Faker
import orjson
import pyarrow as pa
from faker.providers import BaseProvider

from python_tmx.arrow.dicts import (
  BptArrowDict,
  EptArrowDict,
  HiArrowDict,
  ItArrowDict,
  NoteArrowDict,
  PhArrowDict,
  PropArrowDict,
  SubArrowDict,
  TuArrowDict,
  TuvArrowDict,
)
from python_tmx.arrow.structs import (
  STRUCT_FROM_DATACLASS,
)
from python_tmx.base.types import (
  BaseElementAlias,
  Prop,
  Note,
  Header,
  Bpt,
  Ept,
  Hi,
  It,
  Ph,
  Sub,
  Tuv,
  Tu,
  Tmx,
)


class ArrowProvider(BaseProvider):
  generator: Faker

  def prop_dict(self) -> PropArrowDict:
    return {
      "text": self.generator.sentence(),
      "type": self.generator.word(),
      "lang": self.generator.language_code(),
      "o_encoding": self.generator.encoding(),
    }

  def note_dict(self) -> NoteArrowDict:
    return {
      "text": self.generator.sentence(),
      "lang": self.generator.language_code(),
      "o_encoding": self.generator.encoding(),
    }

  def inline_content(self, sub_only: bool = False) -> bytes:
    parts: list[str | SubArrowDict | BptArrowDict | EptArrowDict | ItArrowDict | PhArrowDict | HiArrowDict] = []
    n = self.generator.random_number(1, True)
    for _ in range(n):
      if sub_only:
        if self.generator.random_int(0, 10) < 7:
          parts.append(self.generator.word())
        else:
          parts.append(self.sub_dict())
      else:
        tag = self.generator.random_element(
          OrderedDict({"str": 0.6, "bpt": 0.1, "ept": 0.1, "it": 0.05, "ph": 0.1, "hi": 0.05})
        )
        match tag:
          case "str":
            parts.append(self.generator.sentence(self.generator.random_number(2, False)))
          case "bpt":
            parts.append(self.bpt_dict())
          case "ept":
            parts.append(self.ept_dict())
          case "it":
            parts.append(self.it_dict())
          case "ph":
            parts.append(self.ph_dict())
          case "hi":
            parts.append(self.hi_dict())
    return orjson.dumps(parts)

  def bpt_dict(self) -> BptArrowDict:
    return {
      "tag": "bpt",
      "content": self.inline_content(sub_only=True),
      "i": self.generator.random_number(1, True),
      "x": self.generator.random_number(1, True),
      "type": self.generator.word(),
    }

  def ept_dict(self) -> EptArrowDict:
    return {
      "tag": "ept",
      "content": self.inline_content(sub_only=True),
      "i": self.generator.random_number(1, True),
    }

  def it_dict(self) -> ItArrowDict:
    return {
      "tag": "it",
      "content": self.inline_content(sub_only=True),
      "pos": self.generator.pos().value,
      "x": self.generator.random_number(1, True),
      "type": self.generator.word(),
    }

  def ph_dict(self) -> PhArrowDict:
    return {
      "tag": "ph",
      "content": self.inline_content(sub_only=True),
      "x": self.generator.random_number(1, True),
      "type": self.generator.word(),
      "assoc": self.generator.assoc().value,
    }

  def hi_dict(self) -> HiArrowDict:
    return {
      "tag": "hi",
      "content": self.inline_content(sub_only=False),
      "x": self.generator.random_number(1, True),
      "type": self.generator.word(),
    }

  def sub_dict(self) -> SubArrowDict:
    return {
      "tag": "sub",
      "content": self.inline_content(sub_only=False),
      "type": self.generator.word(),
      "datatype": self.generator.datatype(),
    }

  def tuv_dict(self) -> TuvArrowDict:
    return {
      "lang": self.generator.language_code(),
      "o_encoding": self.generator.encoding(),
      "datatype": self.generator.datatype(),
      "usagecount": self.generator.random_number(3, False),
      "lastusagedate": self.generator.date_time_this_century(),
      "creationtool": self.generator.word(),
      "creationtoolversion": self.generator.version(),
      "creationdate": self.generator.date_time_this_century(),
      "creationid": self.generator.user_name(),
      "changedate": self.generator.date_time_this_century(),
      "changeid": self.generator.user_name(),
      "o_tmf": self.generator.word(),
      "props": [self.prop_dict() for _ in range(self.generator.random_number(1, True))],
      "notes": [self.note_dict() for _ in range(self.generator.random_number(1, True))],
      "content": self.inline_content(sub_only=False),
    }

  def tu_dict(self) -> TuArrowDict:
    return {
      "tuid": str(self.generator.uuid4()),
      "o_encoding": self.generator.encoding(),
      "datatype": self.generator.datatype(),
      "usagecount": self.generator.random_number(3, False),
      "lastusagedate": self.generator.date_time_this_century(),
      "creationtool": self.generator.word(),
      "creationtoolversion": self.generator.version(),
      "creationdate": self.generator.date_time_this_century(),
      "creationid": self.generator.user_name(),
      "changedate": self.generator.date_time_this_century(),
      "segtype": self.generator.segtype().value,
      "changeid": self.generator.user_name(),
      "o_tmf": self.generator.word(),
      "srclang": self.generator.language_code(),
      "props": [self.prop_dict() for _ in range(self.generator.random_number(1, True))],
      "notes": [self.note_dict() for _ in range(self.generator.random_number(1, True))],
      "variants": [self.tuv_dict() for _ in range(2)],
    }

  def header_dict(self) -> dict[str, Any]:
    return {
      "creationtool": self.generator.word(),
      "creationtoolversion": self.generator.version(),
      "segtype": self.generator.segtype().value,
      "o_tmf": self.generator.word(),
      "adminlang": self.generator.language_code(),
      "srclang": self.generator.language_code(),
      "datatype": self.generator.datatype(),
      "o_encoding": self.generator.encoding(),
      "creationdate": self.generator.date_time_this_century(),
      "creationid": self.generator.user_name(),
      "changedate": self.generator.date_time_this_century(),
      "changeid": self.generator.user_name(),
      "props": [self.prop_dict() for _ in range(self.generator.random_number(1, True))],
      "notes": [self.note_dict() for _ in range(self.generator.random_number(1, True))],
    }

  def tmx_dict(self) -> dict[str, Any]:
    return {
      "version": "1.4",
      "header": self.header_dict(),
      "body": [self.tu_dict() for _ in range(self.generator.random_number(3, False))],
    }

  def scalar_for(self, obj_type: type[BaseElementAlias]) -> pa.Scalar:
    struct_type = STRUCT_FROM_DATACLASS[obj_type]
    data_method = getattr(self, f"{obj_type.__name__.lower()}_dict")
    data = data_method()
    return pa.scalar(data, type=struct_type)

  def prop_scalar(self) -> pa.Scalar:
    return self.scalar_for(Prop)

  def note_scalar(self) -> pa.Scalar:
    return self.scalar_for(Note)

  def header_scalar(self) -> pa.Scalar:
    return self.scalar_for(Header)

  def bpt_scalar(self) -> pa.Scalar:
    return self.scalar_for(Bpt)

  def ept_scalar(self) -> pa.Scalar:
    return self.scalar_for(Ept)

  def hi_scalar(self) -> pa.Scalar:
    return self.scalar_for(Hi)

  def it_scalar(self) -> pa.Scalar:
    return self.scalar_for(It)

  def ph_scalar(self) -> pa.Scalar:
    return self.scalar_for(Ph)

  def sub_scalar(self) -> pa.Scalar:
    return self.scalar_for(Sub)

  def tuv_scalar(self) -> pa.Scalar:
    return self.scalar_for(Tuv)

  def tu_scalar(self) -> pa.Scalar:
    return self.scalar_for(Tu)

  def tmx_scalar(self) -> pa.Scalar:
    return self.scalar_for(Tmx)
