import pytest
import logging
from hypomnema.base.types import (
  Prop,
  Note,
  Header,
  Tuv,
  Tu,
  Tmx,
  Bpt,
  Ept,
  It,
  Ph,
  Sub,
  Hi,
  Pos,
  Assoc,
)
from hypomnema.xml.deserialization.deserializer import Deserializer
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue
from hypomnema.base.errors import AttributeDeserializationError, XmlDeserializationError


class BaseDeserializationTest:
  @pytest.fixture(autouse=True)
  def setup(self, mocker, backend):
    self.mocker = mocker
    self.backend = backend
    self.deserializer = Deserializer(backend, policy=DeserializationPolicy())

    self.deserializer.policy.empty_content = PolicyValue("ignore", logging.DEBUG)

  def create_elem(self, tag, text=None, tail=None, **attrs):
    elem = self.backend.create_element(tag)
    for k, v in attrs.items():
      self.backend.set_attribute(elem, k, v)

    if text is not None:
      self.backend.set_text(elem, text)
    if tail is not None:
      self.backend.set_tail(elem, tail)
    return elem

  def create_child(self, parent, tag, text=None, tail=None, **attrs):
    child = self.create_elem(tag, text, tail, **attrs)
    self.backend.append_child(parent, child)
    return child


class TestPropDeserializerHappy(BaseDeserializationTest):
  def test_deserialize_prop_all_fields(self):
    elem = self.create_elem(
      "prop", text="val", type="x-key", **{"xml:lang": "en", "o-encoding": "utf-8"}
    )
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Prop)
    assert obj.text == "val"
    assert obj.type == "x-key"
    assert obj.lang == "en"
    assert obj.o_encoding == "utf-8"


class TestPropDeserializerError(BaseDeserializationTest):
  def test_missing_type(self):
    elem = self.create_elem("prop", text="val")
    with pytest.raises(AttributeDeserializationError, match="Required attribute 'type' is None"):
      self.deserializer.deserialize(elem)

  def test_empty_content_raise(self):
    self.deserializer.policy.empty_content = PolicyValue("raise", logging.DEBUG)
    elem = self.create_elem("prop", type="x-key")
    with pytest.raises(
      XmlDeserializationError, match="Element <prop> does not have any text content"
    ):
      self.deserializer.deserialize(elem)

  def test_invalid_child(self):
    elem = self.create_elem("prop", text="val", type="k")
    self.create_child(elem, "bad")
    with pytest.raises(XmlDeserializationError, match="Invalid child element <bad> in <prop>"):
      self.deserializer.deserialize(elem)


class TestNoteDeserializerHappy(BaseDeserializationTest):
  def test_deserialize_note(self):
    elem = self.create_elem("note", text="note text", **{"xml:lang": "fr"})
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Note)
    assert obj.text == "note text"
    assert obj.lang == "fr"


class TestNoteDeserializerError(BaseDeserializationTest):
  def test_empty_content(self):
    self.deserializer.policy.empty_content = PolicyValue("raise", logging.DEBUG)
    elem = self.create_elem("note")
    with pytest.raises(XmlDeserializationError):
      self.deserializer.deserialize(elem)


class TestHeaderDeserializerHappy(BaseDeserializationTest):
  def test_deserialize_header(self):
    elem = self.create_elem(
      "header",
      creationtool="tool",
      creationtoolversion="1.0",
      segtype="block",
      **{"o-tmf": "fmt", "adminlang": "en", "srclang": "en", "datatype": "txt"},
    )
    self.create_child(elem, "prop", text="p", type="t")
    self.create_child(elem, "note", text="n")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Header)
    assert obj.creationtool == "tool"
    assert len(obj.props) == 1
    assert len(obj.notes) == 1


class TestHeaderDeserializerError(BaseDeserializationTest):
  def test_extra_text(self):
    elem = self.create_elem(
      "header",
      text="unexpected",
      creationtool="t",
      creationtoolversion="v",
      segtype="block",
      **{"o-tmf": "f", "adminlang": "l", "srclang": "l", "datatype": "d"},
    )
    with pytest.raises(XmlDeserializationError, match="extra text"):
      self.deserializer.deserialize(elem)

  def test_invalid_enum(self):
    elem = self.create_elem(
      "header",
      creationtool="t",
      creationtoolversion="v",
      segtype="invalid",
      **{"o-tmf": "f", "adminlang": "l", "srclang": "l", "datatype": "d"},
    )
    with pytest.raises(AttributeDeserializationError, match="not a valid enum"):
      self.deserializer.deserialize(elem)


class TestInlineDeserializersHappy(BaseDeserializationTest):
  def test_bpt(self):
    elem = self.create_elem("bpt", text="text", i="1", x="2", type="b")
    self.create_child(elem, "sub", text="s", datatype="html")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Bpt)
    assert obj.i == 1
    assert len(obj.content) == 2
    assert isinstance(obj.content[1], Sub)

  def test_ept(self):
    elem = self.create_elem("ept", i="1")
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Ept)
    assert obj.i == 1

  def test_it(self):
    elem = self.create_elem("it", pos="begin", x="9")
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, It)
    assert obj.pos == Pos.BEGIN
    assert obj.x == 9

  def test_ph(self):
    elem = self.create_elem("ph", x="1", assoc="p")
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Ph)
    assert obj.assoc == Assoc.P

  def test_hi(self):
    elem = self.create_elem("hi", text="bold")
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Hi)
    assert obj.content == ["bold"]

  def test_sub(self):
    elem = self.create_elem("sub", text="s")
    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Sub)


class TestInlineDeserializersError(BaseDeserializationTest):
  def test_bpt_missing_i(self):
    elem = self.create_elem("bpt")
    with pytest.raises(AttributeDeserializationError):
      self.deserializer.deserialize(elem)


class TestTuvDeserializerHappy(BaseDeserializationTest):
  def test_tuv(self):
    elem = self.create_elem("tuv", **{"xml:lang": "en"})
    seg = self.create_child(elem, "seg", text="Hello ")
    self.create_child(seg, "ph", x="1", tail=" World")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Tuv)
    assert obj.lang == "en"
    assert len(obj.content) == 3
    assert obj.content[0] == "Hello "
    assert isinstance(obj.content[1], Ph)
    assert obj.content[2] == " World"


class TestTuvDeserializerError(BaseDeserializationTest):
  def test_missing_seg(self):
    elem = self.create_elem("tuv", **{"xml:lang": "en"})
    with pytest.raises(XmlDeserializationError, match="missing a <seg>"):
      self.deserializer.deserialize(elem)

  def test_multiple_seg(self):
    elem = self.create_elem("tuv", **{"xml:lang": "en"})
    self.create_child(elem, "seg", text="1")
    self.create_child(elem, "seg", text="2")
    with pytest.raises(XmlDeserializationError, match="Multiple <seg>"):
      self.deserializer.deserialize(elem)


class TestTuDeserializerHappy(BaseDeserializationTest):
  def test_tu(self):
    elem = self.create_elem("tu", tuid="1")

    tuv = self.create_child(elem, "tuv", **{"xml:lang": "en"})
    self.create_child(tuv, "seg", text="content")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Tu)
    assert obj.tuid == "1"
    assert len(obj.variants) == 1


class TestTuDeserializerError(BaseDeserializationTest):
  def test_tu_invalid_child(self):
    elem = self.create_elem("tu")
    self.create_child(elem, "bad")
    with pytest.raises(XmlDeserializationError):
      self.deserializer.deserialize(elem)


class TestTmxDeserializerHappy(BaseDeserializationTest):
  def test_tmx(self):
    elem = self.create_elem("tmx", version="1.4")

    self.create_child(
      elem,
      "header",
      creationtool="t",
      creationtoolversion="v",
      segtype="block",
      **{"o-tmf": "f", "adminlang": "l", "srclang": "l", "datatype": "d"},
    )

    body = self.create_child(elem, "body")
    tu = self.create_child(body, "tu")
    tuv = self.create_child(tu, "tuv", **{"xml:lang": "en"})
    self.create_child(tuv, "seg", text="content")

    obj = self.deserializer.deserialize(elem)
    assert isinstance(obj, Tmx)
    assert obj.version == "1.4"
    assert obj.header.creationtool == "t"
    assert len(obj.body) == 1


class TestTmxDeserializerError(BaseDeserializationTest):
  def test_missing_header(self):
    elem = self.create_elem("tmx", version="1.4")
    with pytest.raises(XmlDeserializationError, match="missing a <header>"):
      self.deserializer.deserialize(elem)
