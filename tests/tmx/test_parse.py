from python_tmx.tmx.models import Note, Prop, SegmentPart, SegmentPartType, Tu


def test_generate_tus_returns_tu_objects(parsed_tus):
  assert all(isinstance(tu, Tu) for tu in parsed_tus)
  assert parsed_tus, "No TUs parsed from TMX"


def test_tu_has_metadata(parsed_tus: list[Tu]):
  tu = parsed_tus[0]
  assert all(isinstance(m, Prop) for m in tu.props)
  assert all(isinstance(m, Note) for m in tu.notes)
  assert tu.props[0].type == "client"
  assert tu.props[0].content == "Acme"


def test_tu_contains_tuvs(parsed_tus: list[Tu]):
  tu = parsed_tus[0]
  assert len(tu.variants) == 2
  langs = {tuv.lang for tuv in tu.variants}
  assert langs == {"en", "fr"}


def test_tuv_contains_segment_parts(parsed_tus: list[Tu]):
  tuv = parsed_tus[0].variants[0]
  assert all(isinstance(part, SegmentPart) for part in tuv.segment)
  text_parts = [p.content for p in tuv.segment if p.type is SegmentPartType.STRING]
  assert "Click" in " ".join(text_parts)


def test_prop_and_note_extraction(parsed_tus: list[Tu]):
  tu = parsed_tus[0]
  prop = next(m for m in tu.props if isinstance(m, Prop))
  note = next(m for m in tu.notes if isinstance(m, Note))
  assert prop.type == "client"
  assert note.content == "Simple segment"


def test_segment_tags_preserved(parsed_tus: list[Tu]):
  tuv_en = next(tuv for tuv in parsed_tus[0].variants if tuv.lang == "en")
  bpt_tags = [p for p in tuv_en.segment if p.type is SegmentPartType.BPT]
  ept_tags = [p for p in tuv_en.segment if p.type is SegmentPartType.EPT]
  assert bpt_tags and ept_tags
  assert bpt_tags[0].attributes.get("i") == "1"
  assert "b" in bpt_tags[0].content.lower()
