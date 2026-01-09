import pytest
import logging
from datetime import datetime, timezone
from hypomnema.base.types import (
  Prop,
  Note,
  Header,
  Segtype,
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
from hypomnema.xml.serialization.serializer import Serializer
from hypomnema.xml.policy import SerializationPolicy, PolicyValue
from hypomnema.base.errors import AttributeSerializationError, XmlSerializationError


class BaseSerializationTest:
  @pytest.fixture(autouse=True)
  def setup(self, mocker, backend):
    self.mocker = mocker
    self.backend = backend
    self.serializer = Serializer(backend, policy=SerializationPolicy())

  def assert_tag(self, element, expected_tag):
    assert self.backend.get_tag(element) == expected_tag

  def assert_attr(self, element, attr, expected_value):
    val = self.backend.get_attribute(element, attr)
    assert val == expected_value

  def assert_text(self, element, expected_text):
    assert self.backend.get_text(element) == expected_text

  def assert_child_count(self, element, expected_count, tag_filter=None):
    children = list(self.backend.iter_children(element, tag_filter=tag_filter))
    assert len(children) == expected_count
    return children


class TestPropSerializerHappy(BaseSerializationTest):
  def test_serialize_prop_all_fields(self):
    prop = Prop(text="some text", type="x-test", lang="en-US", o_encoding="utf-8")
    elem = self.serializer.serialize(prop)

    self.assert_tag(elem, "prop")
    self.assert_attr(elem, "type", "x-test")
    self.assert_attr(elem, "xml:lang", "en-US")
    self.assert_attr(elem, "o-encoding", "utf-8")
    self.assert_text(elem, "some text")

  def test_serialize_prop_minimal(self):
    prop = Prop(text="value", type="x-key")
    elem = self.serializer.serialize(prop)

    self.assert_tag(elem, "prop")
    self.assert_attr(elem, "type", "x-key")
    self.assert_attr(elem, "xml:lang", None)
    self.assert_text(elem, "value")


class TestPropSerializerError(BaseSerializationTest):
  def test_invalid_object_type(self):
    handler = self.serializer.handlers[Prop]
    with pytest.raises(XmlSerializationError, match="not an instance of 'Prop'"):
      handler._serialize(Note(text="n"))

  def test_missing_required_attribute(self):
    prop = Prop(text="val", type=None)
    with pytest.raises(AttributeSerializationError, match="Required attribute 'type' is missing"):
      self.serializer.serialize(prop)

  def test_missing_required_attribute_ignore(self):
    self.serializer.policy.required_attribute_missing = PolicyValue("ignore", logging.DEBUG)
    prop = Prop(text="val", type=None)
    elem = self.serializer.serialize(prop)
    self.assert_attr(elem, "type", None)

  def test_invalid_attribute_type(self):
    prop = Prop(text="val", type=123)
    with pytest.raises(AttributeSerializationError, match="not a string"):
      self.serializer.serialize(prop)


class TestNoteSerializerHappy(BaseSerializationTest):
  def test_serialize_note_all_fields(self):
    note = Note(text="note text", lang="fr", o_encoding="latin-1")
    elem = self.serializer.serialize(note)

    self.assert_tag(elem, "note")
    self.assert_attr(elem, "xml:lang", "fr")
    self.assert_attr(elem, "o-encoding", "latin-1")
    self.assert_text(elem, "note text")

  def test_serialize_note_minimal(self):
    note = Note(text="simple")
    elem = self.serializer.serialize(note)
    self.assert_tag(elem, "note")
    self.assert_text(elem, "simple")


class TestNoteSerializerError(BaseSerializationTest):
  def test_invalid_object_type(self):
    handler = self.serializer.handlers[Note]
    with pytest.raises(XmlSerializationError, match="not an instance of 'Note'"):
      handler._serialize(Prop(text="p", type="t"))

  def test_invalid_attribute_type(self):
    note = Note(text="t", lang=123)
    with pytest.raises(AttributeSerializationError, match="not a string"):
      self.serializer.serialize(note)


class TestHeaderSerializerHappy(BaseSerializationTest):
  def test_serialize_header_all_fields(self):
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    header = Header(
      creationtool="Tool",
      creationtoolversion="1.0",
      segtype=Segtype.SENTENCE,
      o_tmf="tmf",
      adminlang="en",
      srclang="en-US",
      datatype="plain",
      o_encoding="utf-8",
      creationdate=dt,
      creationid="user1",
      changedate=dt,
      changeid="user2",
      notes=[Note(text="n1")],
      props=[Prop(text="p1", type="t1")],
    )
    elem = self.serializer.serialize(header)

    self.assert_tag(elem, "header")
    self.assert_attr(elem, "creationtool", "Tool")
    self.assert_attr(elem, "segtype", "sentence")
    self.assert_attr(elem, "creationdate", dt.isoformat())
    self.assert_child_count(elem, 1, tag_filter="note")
    self.assert_child_count(elem, 1, tag_filter="prop")


class TestHeaderSerializerError(BaseSerializationTest):
  def test_missing_required_attribute(self):
    header = Header(
      creationtool=None,
      creationtoolversion="1.0",
      segtype=Segtype.BLOCK,
      o_tmf="fmt",
      adminlang="en",
      srclang="en",
      datatype="fmt",
    )
    with pytest.raises(
      AttributeSerializationError, match="Required attribute 'creationtool' is missing"
    ):
      self.serializer.serialize(header)

  def test_invalid_enum_attribute(self):
    header = Header(
      creationtool="t",
      creationtoolversion="v",
      segtype="invalid",
      o_tmf="f",
      adminlang="l",
      srclang="l",
      datatype="d",
    )
    with pytest.raises(AttributeSerializationError, match="not a member of"):
      self.serializer.serialize(header)

  def test_invalid_date_attribute(self):
    header = Header(
      creationtool="t",
      creationtoolversion="v",
      segtype=Segtype.BLOCK,
      o_tmf="f",
      adminlang="l",
      srclang="l",
      datatype="d",
      creationdate="not-a-date",
    )
    with pytest.raises(AttributeSerializationError, match="not a datetime object"):
      self.serializer.serialize(header)

  def test_invalid_child_element(self):
    header = Header(
      creationtool="t",
      creationtoolversion="v",
      segtype=Segtype.BLOCK,
      o_tmf="f",
      adminlang="l",
      srclang="l",
      datatype="d",
      notes=[Prop(text="p", type="t")],
    )
    with pytest.raises(XmlSerializationError, match="Invalid child element"):
      self.serializer.serialize(header)


class TestInlineSerializersHappy(BaseSerializationTest):
  def test_bpt(self):
    bpt = Bpt(i=1, x=2, type="bold", content=["text", Sub(content=["sub"])])
    elem = self.serializer.serialize(bpt)
    self.assert_tag(elem, "bpt")
    self.assert_attr(elem, "i", "1")
    self.assert_attr(elem, "x", "2")
    self.assert_attr(elem, "type", "bold")
    self.assert_text(elem, "text")
    self.assert_child_count(elem, 1, tag_filter="sub")

  def test_ept(self):
    ept = Ept(i=1, content=["foo"])
    elem = self.serializer.serialize(ept)
    self.assert_tag(elem, "ept")
    self.assert_attr(elem, "i", "1")
    self.assert_text(elem, "foo")

  def test_it(self):
    it = It(pos=Pos.BEGIN, x=1, type="foo")
    elem = self.serializer.serialize(it)
    self.assert_tag(elem, "it")
    self.assert_attr(elem, "pos", "begin")

  def test_ph(self):
    ph = Ph(x=1, type="img", assoc=Assoc.P)
    elem = self.serializer.serialize(ph)
    self.assert_tag(elem, "ph")
    self.assert_attr(elem, "assoc", "p")

  def test_hi(self):
    hi = Hi(x=1, type="b", content=["bold"])
    elem = self.serializer.serialize(hi)
    self.assert_tag(elem, "hi")
    self.assert_text(elem, "bold")

  def test_sub(self):
    sub = Sub(datatype="html", type="link", content=["click"])
    elem = self.serializer.serialize(sub)
    self.assert_tag(elem, "sub")
    self.assert_attr(elem, "datatype", "html")


class TestInlineSerializersError(BaseSerializationTest):
  def test_mixed_content_invalid_child(self):
    bpt = Bpt(i=1, content=[Note(text="bad")])
    with pytest.raises(XmlSerializationError, match="Incorrect child element"):
      self.serializer.serialize(bpt)

  def test_mixed_content_invalid_child_ignore(self):
    self.serializer.policy.invalid_content_type = PolicyValue("ignore", logging.DEBUG)
    bpt = Bpt(i=1, content=[Note(text="bad")])
    elem = self.serializer.serialize(bpt)
    self.assert_child_count(elem, 0)

  def test_bpt_missing_i(self):
    bpt = Bpt(i=None)
    with pytest.raises(AttributeSerializationError, match="Required attribute 'i' is missing"):
      self.serializer.serialize(bpt)

  def test_it_missing_pos(self):
    it = It(pos=None)
    with pytest.raises(AttributeSerializationError, match="Required attribute 'pos' is missing"):
      self.serializer.serialize(it)


class TestTuvSerializerHappy(BaseSerializationTest):
  def test_tuv_structure(self):
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    tuv = Tuv(
      lang="en",
      o_encoding="utf-8",
      datatype="plain",
      usagecount=1,
      lastusagedate=dt,
      creationtool="tool",
      creationtoolversion="v1",
      creationdate=dt,
      creationid="uid",
      changedate=dt,
      changeid="uid2",
      o_tmf="tmf",
      content=["Hello ", Ph(x=1), " World"],
      notes=[Note(text="n")],
      props=[Prop(text="p", type="t")],
    )
    elem = self.serializer.serialize(tuv)

    self.assert_tag(elem, "tuv")
    self.assert_attr(elem, "xml:lang", "en")
    self.assert_attr(elem, "usagecount", "1")
    self.assert_attr(elem, "creationdate", dt.isoformat())

    self.assert_child_count(elem, 1, tag_filter="note")
    self.assert_child_count(elem, 1, tag_filter="prop")
    segs = self.assert_child_count(elem, 1, tag_filter="seg")

    seg = segs[0]
    self.assert_text(seg, "Hello ")
    phs = self.assert_child_count(seg, 1, tag_filter="ph")
    assert self.backend.get_tail(phs[0]) == " World"


class TestTuvSerializerError(BaseSerializationTest):
  def test_missing_lang(self):
    tuv = Tuv(lang=None)
    with pytest.raises(
      AttributeSerializationError, match="Required attribute 'xml:lang' is missing"
    ):
      self.serializer.serialize(tuv)

  def test_invalid_content_in_seg(self):
    tuv = Tuv(lang="en", content=[Note(text="bad")])
    with pytest.raises(XmlSerializationError, match="Incorrect child element"):
      self.serializer.serialize(tuv)


class TestTuSerializerHappy(BaseSerializationTest):
  def test_tu_structure(self):
    dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    tu = Tu(
      tuid="tu1",
      o_encoding="utf-8",
      datatype="plain",
      usagecount=2,
      lastusagedate=dt,
      creationtool="tool",
      creationtoolversion="v1",
      creationdate=dt,
      creationid="uid",
      changedate=dt,
      segtype=Segtype.BLOCK,
      changeid="uid2",
      o_tmf="tmf",
      srclang="en",
      notes=[Note(text="n")],
      props=[Prop(text="p", type="t")],
      variants=[Tuv(lang="en"), Tuv(lang="fr")],
    )
    elem = self.serializer.serialize(tu)

    self.assert_tag(elem, "tu")
    self.assert_attr(elem, "tuid", "tu1")
    self.assert_attr(elem, "segtype", "block")

    self.assert_child_count(elem, 1, tag_filter="note")
    self.assert_child_count(elem, 1, tag_filter="prop")
    self.assert_child_count(elem, 2, tag_filter="tuv")


class TestTuSerializerError(BaseSerializationTest):
  def test_tu_invalid_child(self):
    tu = Tu(variants=[Prop(text="p", type="t")])
    with pytest.raises(XmlSerializationError, match="Invalid child element"):
      self.serializer.serialize(tu)


class TestTmxSerializerHappy(BaseSerializationTest):
  def test_tmx_structure(self):
    header = Header(
      creationtool="t",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="f",
      adminlang="en",
      srclang="en",
      datatype="d",
    )
    tmx = Tmx(header=header, body=[Tu(tuid="1"), Tu(tuid="2")])

    elem = self.serializer.serialize(tmx)
    self.assert_tag(elem, "tmx")
    self.assert_attr(elem, "version", "1.4")

    self.assert_child_count(elem, 1, tag_filter="header")
    body = self.assert_child_count(elem, 1, tag_filter="body")[0]
    self.assert_child_count(body, 2, tag_filter="tu")


class TestTmxSerializerError(BaseSerializationTest):
  def test_tmx_invalid_child(self):
    header = Header(
      creationtool="t",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="f",
      adminlang="en",
      srclang="en",
      datatype="d",
    )
    tmx = Tmx(header=header, body=[Note(text="bad")])

    with pytest.raises(XmlSerializationError, match="Invalid child element"):
      self.serializer.serialize(tmx)

  def test_tmx_missing_header(self):
    tmx = Tmx(header=None)
    with pytest.raises(XmlSerializationError, match="Invalid child element"):
      self.serializer.serialize(tmx)
