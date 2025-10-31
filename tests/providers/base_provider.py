from collections import OrderedDict
from typing import Literal, overload
from faker.providers import BaseProvider

from python_tmx.base.types import Bpt, Ept, Header, Hi, It, Note, Ph, Prop, Sub, Tmx, Tu, Tuv


class BaseElementProvider(BaseProvider):
  def note(self) -> Note:
    return Note(
      text=self.generator.sentence(self.generator.random_number(2, False)),
      lang=self.generator.language_code() if self.generator.pybool() else None,
      o_encoding=self.generator.encoding() if self.generator.pybool() else None,
    )

  def prop(self) -> Prop:
    return Prop(
      text=self.generator.sentence(self.generator.random_number(2, False)),
      type=self.generator.word(),
      lang=self.generator.language_code() if self.generator.pybool() else None,
      o_encoding=self.generator.encoding() if self.generator.pybool() else None,
    )

  def tuv(self) -> Tuv:
    return Tuv(
      lang=self.generator.language_code(),
      o_encoding=self.generator.encoding() if self.generator.pybool() else None,
      datatype=self.generator.datatype() if self.generator.pybool() else None,
      usagecount=self.generator.random_number(3, False) if self.generator.pybool() else None,
      lastusagedate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      creationtool=self.generator.word() if self.generator.pybool() else None,
      creationtoolversion=self.generator.version() if self.generator.pybool() else None,
      creationdate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      creationid=self.generator.user_name() if self.generator.pybool() else None,
      changedate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      changeid=self.generator.user_name() if self.generator.pybool() else None,
      o_tmf=self.generator.word() if self.generator.pybool() else None,
      props=[self.prop() for _ in range(self.generator.random_number(2, False))],
      notes=[self.note() for _ in range(self.generator.random_number(2, False))],
      content=[self.content(False) for _ in range(self.generator.random_number(2, False))],
    )

  def tu(self) -> Tu:
    return Tu(
      tuid=str(self.generator.uuid4()) if self.generator.pybool() else None,
      o_encoding=self.generator.encoding() if self.generator.pybool() else None,
      datatype=self.generator.datatype() if self.generator.pybool() else None,
      usagecount=self.generator.random_number(3, False) if self.generator.pybool() else None,
      lastusagedate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      creationtool=self.generator.word() if self.generator.pybool() else None,
      creationtoolversion=self.generator.version() if self.generator.pybool() else None,
      creationdate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      creationid=self.generator.user_name() if self.generator.pybool() else None,
      changedate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      segtype=self.generator.segtype() if self.generator.pybool() else None,
      changeid=self.generator.user_name() if self.generator.pybool() else None,
      o_tmf=self.generator.word() if self.generator.pybool() else None,
      srclang=self.generator.language_code() if self.generator.pybool() else None,
      props=[self.prop() for _ in range(self.generator.random_number(2, False))],
      notes=[self.note() for _ in range(self.generator.random_number(2, False))],
      variants=[self.tuv() for _ in range(2)],
    )

  def header(self) -> Header:
    return Header(
      creationtool=self.generator.word(),
      creationtoolversion=self.generator.version(),
      segtype=self.generator.segtype(),
      o_tmf=self.generator.word(),
      adminlang=self.generator.language_code(),
      srclang=self.generator.language_code(),
      datatype=self.generator.datatype(),
      o_encoding=self.generator.encoding() if self.generator.pybool() else None,
      creationdate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      creationid=self.generator.user_name() if self.generator.pybool() else None,
      changedate=self.generator.date_time_this_century() if self.generator.pybool() else None,
      changeid=self.generator.user_name() if self.generator.pybool() else None,
      props=[self.prop() for _ in range(self.generator.random_number(2, False))],
      notes=[self.note() for _ in range(self.generator.random_number(2, False))],
    )

  def tmx(self) -> Tmx:
    return Tmx(
      version="1.4",
      header=self.header(),
      body=[self.tu() for _ in range(self.generator.random_number(2, False))],
    )

  @overload
  def content(self, sub_only: Literal[False]) -> str | Bpt | Ept | It | Ph | Hi: ...
  @overload
  def content(self, sub_only: Literal[True]) -> str | Sub: ...
  def content(self, sub_only: bool) -> str | Sub | Bpt | Ept | It | Ph | Hi:
    if sub_only:
      return (
        Sub(
          content=[self.generator.content(False) for _ in range(self.generator.random_number(1, True))],
          datatype=self.generator.datatype() if self.generator.pybool() else None,
          type=self.generator.word() if self.generator.pybool() else None,
        )
        if self.generator.random_int(0, 1)
        else self.generator.sentence(self.generator.random_number(2, False))
      )
    item_type = self.generator.random_element(
      OrderedDict({"str": 0.6, "bpt": 0.1, "ept": 0.1, "it": 0.05, "ph": 0.1, "hi": 0.05})
    )
    match item_type:
      case "str":
        return self.generator.sentence(self.generator.random_number(2, False))
      case "bpt":
        return self.bpt()
      case "ept":
        return self.ept()
      case "it":
        return self.it()
      case "ph":
        return self.ph()
      case "hi":
        return self.hi()
      case _:
        raise RuntimeError(f"Unexpected item type: {item_type!r}")

  def bpt(self) -> Bpt:
    return Bpt(
      content=[self.content(True) for _ in range(self.generator.random_number(1, True))],
      i=self.generator.random_number(1, False),
      x=self.generator.random_number(1, False) if self.generator.pybool() else None,
      type=self.generator.word() if self.generator.pybool() else None,
    )

  def ept(self) -> Ept:
    return Ept(
      content=[self.content(True) for _ in range(self.generator.random_number(1, True))],
      i=self.generator.random_number(1, False),
    )

  def it(self) -> It:
    return It(
      content=[self.content(True) for _ in range(self.generator.random_number(1, True))],
      pos=self.generator.pos(),
      x=self.generator.random_number(1, False) if self.generator.pybool() else None,
      type=self.generator.word() if self.generator.pybool() else None,
    )

  def ph(self) -> Ph:
    return Ph(
      content=[self.content(True) for _ in range(self.generator.random_number(1, True))],
      x=self.generator.random_number(1, False) if self.generator.pybool() else None,
      type=self.generator.word() if self.generator.pybool() else None,
      assoc=self.generator.assoc() if self.generator.pybool() else None,
    )

  def hi(self) -> Hi:
    return Hi(
      content=[self.content(False) for _ in range(self.generator.random_number(1, True))],
      x=self.generator.random_number(1, False) if self.generator.pybool() else None,
      type=self.generator.word() if self.generator.pybool() else None,
    )
