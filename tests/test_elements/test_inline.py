# type: ignore
import pytest

from PythonTmx.elements.inline import Bpt, Ept, Hi, It, Ph, Sub, Ut
from PythonTmx.enums import ASSOC, BPTITTYPE, DATATYPE, POS
from PythonTmx.errors import (
  DeserializationError,
  NotMappingLikeError,
  SerializationError,
  ValidationError,
  WrongTagError,
)


def test_create_minimal_sub():
  sub = Sub()
  assert sub.datatype is DATATYPE.UNKNOWN
  assert sub.type is None
  assert sub._children == []


def test_create_full_sub():
  sub = Sub(datatype="xhtml", type="bold", children=["Hello", "world"])
  assert sub.datatype == "xhtml"
  assert sub.type == "bold"
  assert sub._children == ["Hello", "world"]


def test_sub_from_minimal_xml(ElementFactory):
  element = ElementFactory("sub", {})
  sub = Sub.from_xml(element)
  assert sub.datatype is DATATYPE.UNKNOWN
  assert sub.type is None
  assert sub._children == []


def test_sub_from_full_xml(ElementFactory):
  element = ElementFactory("sub", {"datatype": "xhtml", "type": "bold"})
  element.text = "Hello"
  sub = Sub.from_xml(element)
  assert sub.datatype == "xhtml"
  assert sub.type == "bold"
  assert sub._children == ["Hello"]


def test_sub_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {})
  with pytest.raises(SerializationError) as exc_info:
    Sub.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_sub_to_xml_minimal(ElementFactory):
  sub = Sub()
  element = sub.to_xml(ElementFactory)
  assert element.tag == "sub"
  assert element.attrib == {"datatype": "unknown"}


def test_sub_to_xml_full(ElementFactory):
  sub = Sub(datatype="xhtml", type="bold", children=["Hello", "world"])
  element = sub.to_xml(ElementFactory)
  assert element.tag == "sub"
  assert element.attrib == {"datatype": "xhtml", "type": "bold"}
  assert element.text == "Helloworld"


def test_create_minimal_ph():
  ph = Ph(x=1)
  assert ph.x == 1
  assert ph.assoc is None
  assert ph.type is None
  assert ph._children == []


def test_create_full_ph():
  ph = Ph(x=1, assoc=ASSOC.P, type="variable", children=["placeholder"])
  assert ph.x == 1
  assert ph.assoc == ASSOC.P
  assert ph.type == "variable"
  assert ph._children == ["placeholder"]


def test_ph_from_minimal_xml(ElementFactory):
  element = ElementFactory("ph", {"x": "1"})
  ph = Ph.from_xml(element)
  assert ph.x == 1
  assert ph.assoc is None
  assert ph.type is None


def test_ph_from_full_xml(ElementFactory):
  element = ElementFactory("ph", {"x": "1", "assoc": "p", "type": "variable"})
  element.text = "placeholder"
  ph = Ph.from_xml(element)
  assert ph.x == 1
  assert ph.assoc == ASSOC.P
  assert ph.type == "variable"
  assert ph._children == ["placeholder"]


def test_ph_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {"x": "1"})
  with pytest.raises(SerializationError) as exc_info:
    Ph.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_ph_from_xml_missing_x(ElementFactory):
  element = ElementFactory("ph", {})
  with pytest.raises(SerializationError) as exc_info:
    Ph.from_xml(element)
  assert isinstance(exc_info.value.__cause__, KeyError)


def test_ph_to_xml_minimal(ElementFactory):
  ph = Ph(x=1)
  element = ph.to_xml(ElementFactory)
  assert element.tag == "ph"
  assert element.attrib == {"x": "1"}


def test_ph_to_xml_full(ElementFactory):
  ph = Ph(x=1, assoc=ASSOC.P, type="variable", children=["placeholder"])
  element = ph.to_xml(ElementFactory)
  assert element.tag == "ph"
  assert element.attrib == {"x": "1", "assoc": "p", "type": "variable"}
  assert element.text == "placeholder"


def test_create_minimal_bpt():
  bpt = Bpt(i=1)
  assert bpt.i == 1
  assert bpt.x is None
  assert bpt.type is None
  assert bpt._children == []


def test_create_full_bpt():
  bpt = Bpt(i=1, x=2, type="bold", children=["begin"])
  assert bpt.i == 1
  assert bpt.x == 2
  assert bpt.type == BPTITTYPE.BOLD
  assert bpt._children == ["begin"]


def test_bpt_from_minimal_xml(ElementFactory):
  element = ElementFactory("bpt", {"i": "1"})
  bpt = Bpt.from_xml(element)
  assert bpt.i == 1
  assert bpt.x is None
  assert bpt.type is None


def test_bpt_from_full_xml(ElementFactory):
  element = ElementFactory("bpt", {"i": "1", "x": "2", "type": "bold"})
  element.text = "begin"
  bpt = Bpt.from_xml(element)
  assert bpt.i == 1
  assert bpt.x == 2
  assert bpt.type == BPTITTYPE.BOLD
  assert bpt._children == ["begin"]


def test_bpt_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {"i": "1"})
  with pytest.raises(SerializationError) as exc_info:
    Bpt.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_bpt_from_xml_missing_i(ElementFactory):
  element = ElementFactory("bpt", {})
  with pytest.raises(SerializationError) as exc_info:
    Bpt.from_xml(element)
  assert isinstance(exc_info.value.__cause__, KeyError)


def test_bpt_to_xml_minimal(ElementFactory):
  bpt = Bpt(i=1)
  element = bpt.to_xml(ElementFactory)
  assert element.tag == "bpt"
  assert element.attrib == {"i": "1"}


def test_bpt_to_xml_full(ElementFactory):
  bpt = Bpt(i=1, x=2, type="bold", children=["begin"])
  element = bpt.to_xml(ElementFactory)
  assert element.tag == "bpt"
  assert element.attrib == {"i": "1", "x": "2", "type": "bold"}
  assert element.text == "begin"


def test_create_minimal_ept():
  ept = Ept(i=1)
  assert ept.i == 1
  assert ept._children == []


def test_create_full_ept():
  ept = Ept(i=1, children=["end"])
  assert ept.i == 1
  assert ept._children == ["end"]


def test_ept_from_minimal_xml(ElementFactory):
  element = ElementFactory("ept", {"i": "1"})
  ept = Ept.from_xml(element)
  assert ept.i == 1
  assert ept._children == []


def test_ept_from_full_xml(ElementFactory):
  element = ElementFactory("ept", {"i": "1"})
  element.text = "end"
  ept = Ept.from_xml(element)
  assert ept.i == 1
  assert ept._children == ["end"]


def test_ept_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {"i": "1"})
  with pytest.raises(SerializationError) as exc_info:
    Ept.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_ept_from_xml_missing_i(ElementFactory):
  element = ElementFactory("ept", {})
  with pytest.raises(SerializationError) as exc_info:
    Ept.from_xml(element)
  assert isinstance(exc_info.value.__cause__, KeyError)


def test_ept_to_xml_minimal(ElementFactory):
  ept = Ept(i=1)
  element = ept.to_xml(ElementFactory)
  assert element.tag == "ept"
  assert element.attrib == {"i": "1"}


def test_ept_to_xml_full(ElementFactory):
  ept = Ept(i=1, children=["end"])
  element = ept.to_xml(ElementFactory)
  assert element.tag == "ept"
  assert element.attrib == {"i": "1"}
  assert element.text == "end"


def test_create_minimal_it():
  it = It(pos=POS.BEGIN)
  assert it.pos == POS.BEGIN
  assert it.x is None
  assert it.type is None
  assert it._children == []


def test_create_full_it():
  it = It(pos=POS.END, x=1, type="italic", children=["isolated"])
  assert it.pos == POS.END
  assert it.x == 1
  assert it.type == BPTITTYPE.ITALIC
  assert it._children == ["isolated"]


def test_it_from_minimal_xml(ElementFactory):
  element = ElementFactory("it", {"pos": "begin"})
  it = It.from_xml(element)
  assert it.pos == POS.BEGIN
  assert it.x is None
  assert it.type is None


def test_it_from_full_xml(ElementFactory):
  element = ElementFactory("it", {"pos": "end", "x": "1", "type": "italic"})
  element.text = "isolated"
  it = It.from_xml(element)
  assert it.pos == POS.END
  assert it.x == 1
  assert it.type == BPTITTYPE.ITALIC
  assert it._children == ["isolated"]


def test_it_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {"pos": "begin"})
  with pytest.raises(SerializationError) as exc_info:
    It.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_it_from_xml_missing_pos(ElementFactory):
  element = ElementFactory("it", {})
  with pytest.raises(SerializationError) as exc_info:
    It.from_xml(element)
  assert isinstance(exc_info.value.__cause__, KeyError)


def test_it_to_xml_minimal(ElementFactory):
  it = It(pos=POS.BEGIN)
  element = it.to_xml(ElementFactory)
  assert element.tag == "it"
  assert element.attrib == {"pos": "begin"}


def test_it_to_xml_full(ElementFactory):
  it = It(pos=POS.END, x=1, type="italic", children=["isolated"])
  element = it.to_xml(ElementFactory)
  assert element.tag == "it"
  assert element.attrib == {"pos": "end", "x": "1", "type": "italic"}
  assert element.text == "isolated"


def test_create_minimal_ut():
  ut = Ut(x=None)
  assert ut.x is None
  assert ut._children == []


def test_create_full_ut():
  ut = Ut(x=1, children=["unpaired"])
  assert ut.x == 1
  assert ut._children == ["unpaired"]


def test_ut_from_minimal_xml(ElementFactory):
  element = ElementFactory("ut", {})
  ut = Ut.from_xml(element)
  assert ut.x is None
  assert ut._children == []


def test_ut_from_full_xml(ElementFactory):
  element = ElementFactory("ut", {"x": "1"})
  element.text = "unpaired"
  ut = Ut.from_xml(element)
  assert ut.x == 1
  assert ut._children == ["unpaired"]


def test_ut_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {})
  with pytest.raises(SerializationError) as exc_info:
    Ut.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_ut_to_xml_minimal(ElementFactory):
  ut = Ut(x=None)
  element = ut.to_xml(ElementFactory)
  assert element.tag == "ut"
  assert element.attrib == {}


def test_ut_to_xml_full(ElementFactory):
  ut = Ut(x=1, children=["unpaired"])
  element = ut.to_xml(ElementFactory)
  assert element.tag == "ut"
  assert element.attrib == {"x": "1"}
  assert element.text == "unpaired"


def test_create_minimal_hi():
  hi = Hi()
  assert hi.x is None
  assert hi.type is None
  assert hi._children == []


def test_create_full_hi():
  hi = Hi(x=1, type="highlight", children=["highlighted"])
  assert hi.x == 1
  assert hi.type == "highlight"
  assert hi._children == ["highlighted"]


def test_hi_from_minimal_xml(ElementFactory):
  element = ElementFactory("hi", {})
  hi = Hi.from_xml(element)
  assert hi.x is None
  assert hi.type is None
  assert hi._children == []


def test_hi_from_full_xml(ElementFactory):
  element = ElementFactory("hi", {"x": "1", "type": "highlight"})
  element.text = "highlighted"
  hi = Hi.from_xml(element)
  assert hi.x == 1
  assert hi.type == "highlight"
  assert hi._children == ["highlighted"]


def test_hi_from_xml_wrong_tag(ElementFactory):
  element = ElementFactory("wrong", {})
  with pytest.raises(SerializationError) as exc_info:
    Hi.from_xml(element)
  assert isinstance(exc_info.value.__cause__, WrongTagError)


def test_hi_to_xml_minimal(ElementFactory):
  hi = Hi()
  element = hi.to_xml(ElementFactory)
  assert element.tag == "hi"
  assert element.attrib == {}


def test_hi_to_xml_full(ElementFactory):
  hi = Hi(x=1, type="highlight", children=["highlighted"])
  element = hi.to_xml(ElementFactory)
  assert element.tag == "hi"
  assert element.attrib == {"x": "1", "type": "highlight"}
  assert element.text == "highlighted"


def test_nested_inline_elements(ElementFactory):
  sub = Sub(
    datatype="xhtml",
    type="complex",
    children=[
      "Start ",
      Ph(x=1, type="variable", children=["placeholder"]),
      " middle ",
      Bpt(i=1, type="bold", children=["bold"]),
      " text ",
      Ept(i=1, children=["end"]),
      " end",
    ],
  )

  element = sub.to_xml(ElementFactory)
  assert element.tag == "sub"
  assert element.attrib == {"datatype": "xhtml", "type": "complex"}
  assert element.text == "Start "
  children = [c for c in element]
  assert len(children) == 3
  ph, bpt, ept = children[0], children[1], children[2]
  assert ph.tag == "ph"
  assert ph.attrib == {"x": "1", "type": "variable"}
  assert ph.text == "placeholder"
  assert ph.tail == " middle "
  assert bpt.tag == "bpt"
  assert bpt.attrib == {"i": "1", "type": "bold"}
  assert bpt.text == "bold"
  assert bpt.tail == " text "
  assert ept.tag == "ept"
  assert ept.attrib == {"i": "1"}
  assert ept.text == "end"
  assert ept.tail == " end"


def test_hi_with_nested_elements(ElementFactory):
  hi = Hi(
    x=1,
    type="highlight",
    children=[
      "Highlight ",
      Bpt(i=1, children=["bold"]),
      " and ",
      Ept(i=1, children=["end"]),
      " text",
    ],
  )

  element = hi.to_xml(ElementFactory)
  assert element.tag == "hi"
  assert element.attrib == {"x": "1", "type": "highlight"}
  assert element.text == "Highlight "
  children = [c for c in element]
  assert len(children) == 2
  bpt, ept = children[0], children[1]
  assert bpt.tag == "bpt"
  assert bpt.attrib == {"i": "1"}
  assert bpt.text == "bold"
  assert bpt.tail == " and "
  assert ept.tag == "ept"
  assert ept.attrib == {"i": "1"}
  assert ept.text == "end"
  assert ept.tail == " text"


def test_sub_validation_errors(ElementFactory):
  sub = Sub()
  sub.type = 123
  with pytest.raises(DeserializationError) as exc_info:
    sub.to_xml(ElementFactory)
  assert isinstance(exc_info.value.__cause__, ValidationError)


def test_ph_validation_errors(ElementFactory):
  ph = Ph(x=1)
  ph.x = "not_an_int"
  with pytest.raises(DeserializationError) as exc_info:
    ph.to_xml(ElementFactory)
  assert isinstance(exc_info.value.__cause__, ValidationError)


def test_bpt_validation_errors(ElementFactory):
  bpt = Bpt(i=1)
  bpt.i = "not_an_int"
  with pytest.raises(DeserializationError) as exc_info:
    bpt.to_xml(ElementFactory)
  assert isinstance(exc_info.value.__cause__, ValidationError)


def test_it_validation_errors(ElementFactory):
  it = It(pos=POS.BEGIN)
  it.pos = 13
  with pytest.raises(DeserializationError) as exc_info:
    it.to_xml(ElementFactory)
  assert isinstance(exc_info.value.__cause__, ValidationError)


def test_from_xml_unusable_attrib(CustomElementLike):
  element = CustomElementLike(tag="sub", attrib="not_a_dict", text="text")
  with pytest.raises(SerializationError) as exc_info:
    Sub.from_xml(element)
  assert isinstance(exc_info.value.__cause__, NotMappingLikeError)


def test_numeric_string_conversion():
  ph = Ph(x="123")
  assert ph.x == 123

  bpt = Bpt(i="456", x="789")
  assert bpt.i == 456
  assert bpt.x == 789

  it = It(pos="begin", x="999")
  assert it.pos == POS.BEGIN
  assert it.x == 999

  ut = Ut(x="111")
  assert ut.x == 111


def test_enum_conversion():
  ph = Ph(x=1, assoc="p")
  assert ph.assoc == ASSOC.P

  ph = Ph(x=1, assoc=ASSOC.F)
  assert ph.assoc == ASSOC.F

  it = It(pos="begin")
  assert it.pos == POS.BEGIN

  it = It(pos=POS.END)
  assert it.pos == POS.END
