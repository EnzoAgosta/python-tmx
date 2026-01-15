from datetime import datetime, timezone
from hypomnema import Tmx, Header, Bpt, Sub, Pos, Assoc, Segtype
from hypomnema.api.helpers import (
  create_tmx,
  create_header,
  create_tu,
  create_tuv,
  create_note,
  create_prop,
  create_bpt,
  create_ept,
  create_it,
  create_ph,
  create_hi,
  create_sub,
)


class TestCreateHelpersHappy:
  def test_create_tmx_minimal(self):
    tmx = create_tmx()
    assert isinstance(tmx, Tmx)
    assert tmx.header.creationtool == "hypomnema"
    assert tmx.body == []
    assert tmx.version == "1.4"

  def test_create_tmx_with_header_and_body(self):
    header = create_header(creationtool="tool", srclang="en", datatype="txt")
    tu = create_tu(tuid="1")
    tmx = create_tmx(header=header, body=[tu])

    assert isinstance(tmx, Tmx)
    assert tmx.header.creationtool == "tool"
    assert len(tmx.body) == 1
    assert tmx.body[0].tuid == "1"

  def test_create_tmx_with_body_as_generator(self):
    def tus():
      yield create_tu(tuid="1")
      yield create_tu(tuid="2")

    tmx = create_tmx(body=tus())
    assert len(tmx.body) == 2

  def test_create_header_defaults(self):
    header = create_header()
    assert header.creationtool == "hypomnema"
    assert header.srclang == "en"
    assert header.adminlang == "en"
    assert header.datatype == "plaintext"
    assert header.segtype == Segtype.BLOCK
    assert header.o_tmf == "tmx"
    assert header.notes == []
    assert header.props == []

  def test_create_header_custom_values(self):
    header = create_header(
      creationtool="custom-tool",
      creationtoolversion="2.0",
      segtype="sentence",
      srclang="fr",
      datatype="xml",
      o_encoding="utf-8",
      creationdate=datetime(2023, 1, 1, tzinfo=timezone.utc),
      creationid="user1",
    )

    assert header.creationtool == "custom-tool"
    assert header.creationtoolversion == "2.0"
    assert header.segtype == Segtype.SENTENCE
    assert header.srclang == "fr"
    assert header.datatype == "xml"
    assert header.o_encoding == "utf-8"
    assert header.creationdate == datetime(2023, 1, 1, tzinfo=timezone.utc)
    assert header.creationid == "user1"

  def test_create_header_with_notes_and_props(self):
    header = create_header(
      notes=[create_note(text="note1"), create_note(text="note2")],
      props=[create_prop(text="prop1", type="type1")],
    )

    assert len(header.notes) == 2
    assert len(header.props) == 1
    assert header.notes[0].text == "note1"
    assert header.props[0].type == "type1"

  def test_create_header_segtype_string(self):
    header = create_header(segtype="paragraph")
    assert header.segtype == Segtype.PARAGRAPH

  def test_create_tu_minimal(self):
    tu = create_tu()
    assert tu.tuid is None
    assert tu.variants == []
    assert tu.notes == []
    assert tu.props == []

  def test_create_tu_with_variants(self):
    tuv1 = create_tuv(lang="en", content=["Hello"])
    tuv2 = create_tuv(lang="fr", content=["Bonjour"])
    tu = create_tu(tuid="test-tu", variants=[tuv1, tuv2])

    assert tu.tuid == "test-tu"
    assert len(tu.variants) == 2
    assert tu.variants[0].lang == "en"
    assert tu.variants[1].lang == "fr"

  def test_create_tu_with_notes_and_props(self):
    tu = create_tu(notes=[create_note(text="note")], props=[create_prop(text="prop", type="type")])
    assert len(tu.notes) == 1
    assert len(tu.props) == 1

  def test_create_tu_segtype_string(self):
    tu = create_tu(segtype="phrase")
    assert tu.segtype == Segtype.PHRASE

  def test_create_tuv_minimal(self):
    tuv = create_tuv(lang="en")
    assert tuv.lang == "en"
    assert tuv.content == []

  def test_create_tuv_with_content(self):
    tuv = create_tuv(lang="en", content=["Hello World"])
    assert tuv.content == ["Hello World"]

  def test_create_tuv_with_inline_elements(self):
    tuv = create_tuv(
      lang="en", content=["Click ", create_bpt(i=1, type="link", content=["<link>"]), " here"]
    )
    assert len(tuv.content) == 3
    assert isinstance(tuv.content[1], Bpt)
    assert tuv.content[1].i == 1

  def test_create_tuv_with_all_attributes(self):
    tuv = create_tuv(
      lang="en",
      datatype="xml",
      o_encoding="utf-8",
      usagecount=10,
      creationdate=datetime(2023, 1, 1, tzinfo=timezone.utc),
      creationid="user1",
    )

    assert tuv.lang == "en"
    assert tuv.datatype == "xml"
    assert tuv.o_encoding == "utf-8"
    assert tuv.usagecount == 10
    assert tuv.creationdate == datetime(2023, 1, 1, tzinfo=timezone.utc)
    assert tuv.creationid == "user1"

  def test_create_note_minimal(self):
    note = create_note(text="test note")
    assert note.text == "test note"
    assert note.lang is None
    assert note.o_encoding is None

  def test_create_note_with_attributes(self):
    note = create_note(text="test", lang="en", o_encoding="utf-8")
    assert note.text == "test"
    assert note.lang == "en"
    assert note.o_encoding == "utf-8"

  def test_create_prop_minimal(self):
    prop = create_prop(text="value", type="test-type")
    assert prop.text == "value"
    assert prop.type == "test-type"

  def test_create_prop_with_attributes(self):
    prop = create_prop(text="value", type="type", lang="fr", o_encoding="utf-8")
    assert prop.text == "value"
    assert prop.type == "type"
    assert prop.lang == "fr"

  def test_create_bpt_minimal(self):
    bpt = create_bpt(i=1)
    assert bpt.i == 1
    assert bpt.content == []
    assert bpt.x is None
    assert bpt.type is None

  def test_create_bpt_with_content(self):
    bpt = create_bpt(i=1, x=2, type="bold", content=["text"])
    assert bpt.i == 1
    assert bpt.x == 2
    assert bpt.type == "bold"
    assert bpt.content == ["text"]

  def test_create_bpt_with_sub(self):
    bpt = create_bpt(i=1, content=[create_sub(datatype="html")])
    assert isinstance(bpt.content[0], Sub)
    assert bpt.content[0].datatype == "html"

  def test_create_ept_minimal(self):
    ept = create_ept(i=1)
    assert ept.i == 1
    assert ept.content == []

  def test_create_ept_with_content(self):
    ept = create_ept(i=1, content=["text"])
    assert ept.i == 1
    assert ept.content == ["text"]

  def test_create_it_pos_enum(self):
    it = create_it(pos=Pos.BEGIN)
    assert it.pos == Pos.BEGIN

  def test_create_it_pos_string(self):
    it = create_it(pos="end")
    assert it.pos == Pos.END

  def test_create_it_with_content(self):
    it = create_it(pos=Pos.BEGIN, x=1, type="u", content=["text"])
    assert it.pos == Pos.BEGIN
    assert it.x == 1
    assert it.type == "u"
    assert it.content == ["text"]

  def test_create_ph_minimal(self):
    ph = create_ph()
    assert ph.x is None
    assert ph.assoc is None
    assert ph.type is None
    assert ph.content == []

  def test_create_ph_with_attributes(self):
    ph = create_ph(x=1, assoc=Assoc.P, type="img")
    assert ph.x == 1
    assert ph.assoc == Assoc.P
    assert ph.type == "img"

  def test_create_ph_assoc_string(self):
    ph = create_ph(assoc="p")
    assert ph.assoc == Assoc.P

  def test_create_ph_with_content(self):
    ph = create_ph(content=["image"])
    assert ph.content == ["image"]

  def test_create_hi_minimal(self):
    hi = create_hi()
    assert hi.x is None
    assert hi.type is None
    assert hi.content == []

  def test_create_hi_with_content(self):
    hi = create_hi(x=1, type="color", content=["highlighted"])
    assert hi.x == 1
    assert hi.type == "color"
    assert hi.content == ["highlighted"]

  def test_create_hi_with_inline_elements(self):
    hi = create_hi(content=[create_bpt(i=1, content=["bold"])])
    assert isinstance(hi.content[0], Bpt)

  def test_create_sub_minimal(self):
    sub = create_sub()
    assert sub.datatype is None
    assert sub.type is None
    assert sub.content == []

  def test_create_sub_with_attributes(self):
    sub = create_sub(datatype="html", type="link")
    assert sub.datatype == "html"
    assert sub.type == "link"

  def test_create_sub_with_content(self):
    sub = create_sub(content=["link text"])
    assert sub.content == ["link text"]


class TestCreateHelpersError:
  def test_create_tmx_none_header_creates_default(self):
    tmx = create_tmx(header=None)
    assert isinstance(tmx.header, Header)
    assert tmx.header.creationtool == "hypomnema"

  def test_create_tmx_none_body_creates_empty_list(self):
    tmx = create_tmx(body=None)
    assert tmx.body == []

  def test_create_tmx_version_none_uses_default(self):
    tmx = create_tmx(version=None)
    assert tmx.version == "1.4"

  def test_create_header_empty_iterables(self):
    header = create_header(notes=[], props=[])
    assert header.notes == []
    assert header.props == []

  def test_create_tu_empty_iterables(self):
    tu = create_tu(notes=[], props=[], variants=[])
    assert tu.notes == []
    assert tu.props == []
    assert tu.variants == []

  def test_create_tuv_empty_iterables(self):
    tuv = create_tuv(lang="en", notes=[], props=[])
    assert tuv.notes == []
    assert tuv.props == []

  def test_create_note_empty_text(self):
    note = create_note(text="")
    assert note.text == ""

  def test_create_prop_empty_values(self):
    prop = create_prop(text="", type="")
    assert prop.text == ""
    assert prop.type == ""
