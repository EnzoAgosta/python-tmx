from hypomnema.base import XmlDeserializationError
from dataclasses import fields
from hypomnema.xml.deserialization import (
  PropDeserializer,
  NoteDeserializer,
  HeaderDeserializer,
  BptDeserializer,
  EptDeserializer,
  ItDeserializer,
  PhDeserializer,
  SubDeserializer,
  HiDeserializer,
  TuvDeserializer,
  TuDeserializer,
  TmxDeserializer,
)
from hypomnema.xml.deserialization.base import BaseElementDeserializer
from hypomnema.xml.constants import XML_NS
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue
import logging
from typing import Any, Literal
import pytest
from pytest_mock import MockerFixture
from datetime import datetime, UTC
import hypomnema as hm


DESERIALIZERS: tuple[
  tuple[
    type[BaseElementDeserializer],  # Handler class
    str,  # XML tag
    dict[str, tuple[str, str, Any]],  # required attrs {xmlAttr: (helper, objField, testValue)}
    dict[str, tuple[str, str, Any]],  # optional attrs {xmlAttr: (helper, objField, testValue)}
    dict[str, int],  # content helpers {"handler": callCount}
  ],
  ...,
] = (
  (
    PropDeserializer,
    "prop",
    {"type": ("_parse_attribute_as_str", "type", "x-mt")},
    {
      f"{XML_NS}lang": ("_parse_attribute_as_str", "lang", "en-us"),
      "o-encoding": ("_parse_attribute_as_str", "o_encoding", "utf-8"),
    },
    {"get_text": 1},
  ),
  (
    NoteDeserializer,
    "note",
    {},
    {
      f"{XML_NS}lang": ("_parse_attribute_as_str", "lang", "en-us"),
      "o-encoding": ("_parse_attribute_as_str", "o_encoding", "utf-8"),
    },
    {"get_text": 1},
  ),
  (
    HeaderDeserializer,
    "header",
    {
      "creationtool": ("_parse_attribute_as_str", "creationtool", "tool"),
      "creationtoolversion": ("_parse_attribute_as_str", "creationtoolversion", "1.0"),
      "segtype": ("_parse_attribute_as_enum", "segtype", hm.Segtype.BLOCK),
      "adminlang": ("_parse_attribute_as_str", "adminlang", "en"),
      "srclang": ("_parse_attribute_as_str", "srclang", "en"),
      "datatype": ("_parse_attribute_as_str", "datatype", "xml"),
      "o-tmf": ("_parse_attribute_as_str", "o_tmf", "tmf"),
    },
    {
      "creationdate": (
        "_parse_attribute_as_datetime",
        "creationdate",
        datetime.now(UTC).isoformat(),
      ),
      "creationid": ("_parse_attribute_as_str", "creationid", "user"),
      "changedate": ("_parse_attribute_as_datetime", "changedate", datetime.now(UTC).isoformat()),
      "changeid": ("_parse_attribute_as_str", "changeid", "editor"),
      "o-encoding": ("_parse_attribute_as_str", "o_encoding", "utf-8"),
    },
    {},  # Handles its own children logic via iter_children
  ),
  (
    BptDeserializer,
    "bpt",
    {"i": ("_parse_attribute_as_int", "i", "1")},
    {
      "x": ("_parse_attribute_as_int", "x", "99"),
      "type": ("_parse_attribute_as_str", "type", "fmt"),
    },
    {"_deserialize_content": 1},
  ),
  (
    EptDeserializer,
    "ept",
    {"i": ("_parse_attribute_as_int", "i", "1")},
    {},
    {"_deserialize_content": 1},
  ),
  (
    ItDeserializer,
    "it",
    {"pos": ("_parse_attribute_as_enum", "pos", hm.Pos.BEGIN)},
    {
      "x": ("_parse_attribute_as_int", "x", "99"),
      "type": ("_parse_attribute_as_str", "type", "fmt"),
    },
    {"_deserialize_content": 1},
  ),
  (
    PhDeserializer,
    "ph",
    {},
    {
      "x": ("_parse_attribute_as_int", "x", "99"),
      "assoc": ("_parse_attribute_as_enum", "assoc", hm.Assoc.P),
      "type": ("_parse_attribute_as_str", "type", "fmt"),
    },
    {"_deserialize_content": 1},
  ),
  (
    SubDeserializer,
    "sub",
    {},
    {
      "datatype": ("_parse_attribute_as_str", "datatype", "xml"),
      "type": ("_parse_attribute_as_str", "type", "fmt"),
    },
    {"_deserialize_content": 1},
  ),
  (
    HiDeserializer,
    "hi",
    {},
    {
      "x": ("_parse_attribute_as_int", "x", "99"),
      "type": ("_parse_attribute_as_str", "type", "bold"),
    },
    {"_deserialize_content": 1},
  ),
  (
    TuvDeserializer,
    "tuv",
    {f"{XML_NS}lang": ("_parse_attribute_as_str", "lang", "en-us")},
    {
      "o-encoding": ("_parse_attribute_as_str", "o_encoding", "utf-8"),
      "datatype": ("_parse_attribute_as_str", "datatype", "xml"),
      "usagecount": ("_parse_attribute_as_int", "usagecount", "42"),
      "lastusagedate": (
        "_parse_attribute_as_datetime",
        "lastusagedate",
        datetime.now(UTC).isoformat(),
      ),
      "creationtool": ("_parse_attribute_as_str", "creationtool", "tool"),
      "creationtoolversion": ("_parse_attribute_as_str", "creationtoolversion", "1.0"),
      "creationdate": (
        "_parse_attribute_as_datetime",
        "creationdate",
        datetime.now(UTC).isoformat(),
      ),
      "creationid": ("_parse_attribute_as_str", "creationid", "user"),
      "changedate": ("_parse_attribute_as_datetime", "changedate", datetime.now(UTC).isoformat()),
      "changeid": ("_parse_attribute_as_str", "changeid", "editor"),
      "o-tmf": ("_parse_attribute_as_str", "o_tmf", "tmf"),
    },
    {},  # Handles its own children logic via iter_children
  ),
  (
    TuDeserializer,
    "tu",
    {},
    {
      "tuid": ("_parse_attribute_as_str", "tuid", "tu1"),
      "o-encoding": ("_parse_attribute_as_str", "o_encoding", "utf-8"),
      "datatype": ("_parse_attribute_as_str", "datatype", "xml"),
      "usagecount": ("_parse_attribute_as_int", "usagecount", "99"),
      "lastusagedate": (
        "_parse_attribute_as_datetime",
        "lastusagedate",
        datetime.now(UTC).isoformat(),
      ),
      "creationtool": ("_parse_attribute_as_str", "creationtool", "tool"),
      "creationtoolversion": ("_parse_attribute_as_str", "creationtoolversion", "1.0"),
      "creationdate": (
        "_parse_attribute_as_datetime",
        "creationdate",
        datetime.now(UTC).isoformat(),
      ),
      "creationid": ("_parse_attribute_as_str", "creationid", "user"),
      "changedate": ("_parse_attribute_as_datetime", "changedate", datetime.now(UTC).isoformat()),
      "segtype": ("_parse_attribute_as_enum", "segtype", hm.Segtype.BLOCK),
      "changeid": ("_parse_attribute_as_str", "changeid", "editor"),
      "o-tmf": ("_parse_attribute_as_str", "o_tmf", "tmf"),
      "srclang": ("_parse_attribute_as_str", "srclang", "en"),
    },
    {},  # Handles its own children logic via iter_children
  ),
  (
    TmxDeserializer,
    "tmx",
    {"version": ("_parse_attribute_as_str", "version", "1.4")},
    {},
    {},  # Handles its own children logic via iter_children
  ),
)


class TestAllHandlersDeserialize:
  backend: hm.XmlBackend
  logger: logging.Logger
  policy: DeserializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    self.mocker = mocker

  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag", "required", "optional", "content_handlers"), DESERIALIZERS
  )
  def test_handler(
    self,
    handler_cls: type[BaseElementDeserializer],
    xml_tag: str,
    required: dict[str, tuple[str, str, Any]],
    optional: dict[str, tuple[str, str, Any]],
    content_handlers: dict[str, int],
  ) -> None:
    # Create real handler
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler._emit = self.mocker.Mock()
    # Setup spy objects
    check_tag_spy = self.mocker.spy(hm.xml.deserialization._handlers, "check_tag")
    backend_get_text_spy = self.mocker.spy(handler.backend, "get_text")
    _parse_attribute_as_datetime_spy = self.mocker.spy(handler, "_parse_attribute_as_datetime")
    _parse_attribute_as_int_spy = self.mocker.spy(handler, "_parse_attribute_as_int")
    _parse_attribute_as_enum_spy = self.mocker.spy(handler, "_parse_attribute_as_enum")
    _parse_attribute_as_str_spy = self.mocker.spy(handler, "_parse_attribute_as_str")

    _deserialize_content_int = (
      self.mocker.spy(handler, "_deserialize_content")
      if hasattr(handler, "_deserialize_content")
      else None
    )

    spy_map = {
      "_parse_attribute_as_datetime": _parse_attribute_as_datetime_spy,
      "_parse_attribute_as_int": _parse_attribute_as_int_spy,
      "_parse_attribute_as_enum": _parse_attribute_as_enum_spy,
      "_parse_attribute_as_str": _parse_attribute_as_str_spy,
      "_deserialize_content": _deserialize_content_int,
      "get_text": backend_get_text_spy,
    }

    # Create mock object
    elem = self.backend.make_elem(xml_tag)

    # Fill in attributes
    for xml_attr, (_, _, val) in {**required, **optional}.items():
      self.backend.set_attr(elem, xml_attr, val)
    self.backend.set_text(elem, "")
    if xml_tag == "tuv":
      seg = self.backend.make_elem("seg")
      self.backend.set_text(seg, "seg")
      self.backend.append(elem, seg)
    if xml_tag == "tmx":
      self.backend.append(elem, self.backend.make_elem("header"))
      self.backend.append(elem, self.backend.make_elem("body"))

    # Actually deserialize the element
    handler._deserialize(elem)

    # Assert object type was checked
    check_tag_spy.assert_called_once_with(xml_tag, xml_tag, logger=self.logger, policy=self.policy)

    # Assert required attributes were set correctly
    for xml_attr, (helper, _, val) in required.items():
      spy = spy_map[helper]
      if helper == "_parse_attribute_as_enum":
        spy.assert_any_call(elem, xml_attr, type(val), required=True)
      else:
        spy.assert_any_call(elem, xml_attr, required=True)

    # Assert optional attributes were set correctly
    for xml_attr, (helper, _, val) in optional.items():
      spy = spy_map[helper]
      if helper == "_parse_attribute_as_enum":
        spy.assert_any_call(elem, xml_attr, type(val), required=False)
      else:
        spy.assert_any_call(elem, xml_attr, required=False)

    for content_handler, call_count in content_handlers.items():
      content_handler_spy = spy_map[content_handler]
      assert content_handler_spy.call_count == call_count


class TestSpecificHandlersPolicy:
  backend: hm.XmlBackend
  logger: logging.Logger
  policy: DeserializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()
    for field in fields(self.policy):
      setattr(self.policy, field.name, PolicyValue("ignore", logging.DEBUG))
    self.mocker = mocker

  @pytest.mark.parametrize("behavior", ("raise", "ignore", "empty"))
  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag"), ((NoteDeserializer, "note"), (PropDeserializer, "prop"))
  )
  def test_element_text_is_none(
    self,
    handler_cls: type[NoteDeserializer | PropDeserializer],
    xml_tag: str,
    behavior: Literal["raise", "ignore", "empty"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler.policy.empty_content = PolicyValue(behavior, log_level)
    message = f"Element <{xml_tag}> does not have any text content"

    elem = self.backend.make_elem(xml_tag)
    if behavior == "raise":
      with pytest.raises(hm.XmlDeserializationError, match=message):
        handler._deserialize(elem)
    elif behavior == "empty":
      out = handler._deserialize(elem)
      assert out.text == ""
    else:
      out = handler._deserialize(elem)
      assert out.text is None

    assert (self.logger.name, log_level, message) in caplog.record_tuples
    if behavior == "empty":
      assert (
        self.logger.name,
        log_level,
        "Falling back to an empty string",
      ) in caplog.record_tuples

  @pytest.mark.parametrize("behavior", ("raise", "ignore"))
  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag"),
    (
      (HeaderDeserializer, "header"),
      (TuDeserializer, "tu"),
      (TuvDeserializer, "tuv"),
      (TmxDeserializer, "tmx"),
    ),
  )
  def test_element_has_extra_text_content_policy(
    self,
    handler_cls: type[NoteDeserializer | PropDeserializer],
    xml_tag: str,
    behavior: Literal["raise", "ignore"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler.policy.extra_text = PolicyValue(behavior, log_level)
    message = f"Element <{xml_tag}> has extra text content 'text'"

    elem = self.backend.make_elem(xml_tag)
    self.backend.set_text(elem, "text")
    if behavior == "raise":
      with pytest.raises(hm.XmlDeserializationError, match=message):
        handler._deserialize(elem)
    else:
      handler._deserialize(elem)
    assert (self.logger.name, log_level, message) in caplog.record_tuples

  @pytest.mark.parametrize("behavior", ("raise", "ignore"))
  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag", "expected"),
    (
      (NoteDeserializer, "note", ()),
      (PropDeserializer, "prop", ()),
      (HeaderDeserializer, "header", ()),
      (BptDeserializer, "bpt", ("sub",)),
      (EptDeserializer, "ept", ("sub",)),
      (ItDeserializer, "it", ("sub",)),
      (PhDeserializer, "ph", ("sub",)),
      (SubDeserializer, "sub", ("bpt", "ept", "ph", "it", "hi")),
      (HiDeserializer, "hi", ("bpt", "ept", "ph", "it", "hi")),
      (TuvDeserializer, "tuv", ()),
      (TuDeserializer, "tu", ()),
      (TmxDeserializer, "tmx", ()),
    ),
  )
  def test_element_has_invalid_children_policy(
    self,
    handler_cls: type[BaseElementDeserializer],
    xml_tag: str,
    expected: tuple[str, ...],
    behavior: Literal["raise", "ignore"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler.policy.invalid_child_element = PolicyValue(behavior, log_level)

    elem = self.backend.make_elem(xml_tag)
    self.backend.append(elem, self.backend.make_elem("invalid_child"))
    if expected:
      message = f"Incorrect child element in {xml_tag}: expected one of {', '.join(expected)}, got invalid_child"
    else:
      message = f"Invalid child element <invalid_child> in <{xml_tag}>"

    if behavior == "raise":
      with pytest.raises(hm.XmlDeserializationError, match=message):
        handler._deserialize(elem)
    else:
      handler._deserialize(elem)

    assert (self.logger.name, log_level, message) in caplog.record_tuples

  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag"),
    ((HeaderDeserializer, "header"), (TuDeserializer, "tu"), (TuvDeserializer, "tuv")),
  )
  def test_handler_emits_note(
    self, handler_cls: type[BaseElementDeserializer], xml_tag: str
  ) -> None:
    handler = handler_cls(self.backend, self.policy, self.logger)

    def test_emit(x):
      return hm.Note(text="ok")

    handler._set_emit(test_emit)
    spy_emit = self.mocker.spy(handler, "emit")

    elem = self.backend.make_elem(xml_tag)
    note_elem = self.backend.make_elem("note")
    self.backend.append(elem, note_elem)

    out = handler._deserialize(elem)

    assert out.notes == [hm.Note(text="ok")]
    spy_emit.assert_called_once_with(note_elem)

  @pytest.mark.parametrize(
    ("handler_cls", "xml_tag"),
    ((HeaderDeserializer, "header"), (TuDeserializer, "tu"), (TuvDeserializer, "tuv")),
  )
  def test_handler_emits_prop(
    self, handler_cls: type[BaseElementDeserializer], xml_tag: str
  ) -> None:
    handler = handler_cls(self.backend, self.policy, self.logger)

    def test_emit(x):
      return hm.Prop(type="x", text="ok")

    handler._set_emit(test_emit)
    spy_emit = self.mocker.spy(handler, "emit")

    elem = self.backend.make_elem(xml_tag)
    note_elem = self.backend.make_elem("prop")
    self.backend.append(elem, note_elem)

    out = handler._deserialize(elem)

    assert out.props == [hm.Prop(type="x", text="ok")]
    spy_emit.assert_called_once_with(note_elem)

  def test_tu_handler_emits_variant(self) -> None:
    handler = TuDeserializer(self.backend, self.policy, self.logger)

    def test_emit(x):
      return hm.Tuv(lang="en")

    handler._set_emit(test_emit)
    spy_emit = self.mocker.spy(handler, "emit")

    elem = self.backend.make_elem("tu")
    tuv_elem = self.backend.make_elem("tuv")
    self.backend.append(elem, tuv_elem)

    out = handler._deserialize(elem)

    assert out.variants == [hm.Tuv(lang="en")]
    spy_emit.assert_called_once_with(tuv_elem)

  def test_tmx_handler_emits_tu(self) -> None:
    handler = TmxDeserializer(self.backend, self.policy, self.logger)

    def test_emit(x):
      return hm.Tu()

    handler._set_emit(test_emit)
    spy_emit = self.mocker.spy(handler, "emit")

    elem = self.backend.make_elem("tmx")
    body_elem = self.backend.make_elem("body")
    tu_elem = self.backend.make_elem("tu")
    self.backend.append(body_elem, tu_elem)
    self.backend.append(elem, body_elem)

    out = handler._deserialize(elem)

    assert out.body == [hm.Tu()]
    spy_emit.assert_called_once_with(tu_elem)

  @pytest.mark.parametrize(("behavior"), ("raise", "keep_first", "keep_last"))
  def test_tuv_handler_multiple_seg(
    self,
    behavior: Literal["raise", "keep_first", "keep_last"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = TuvDeserializer(self.backend, self.policy, self.logger)
    handler.policy.multiple_seg = PolicyValue(behavior, log_level)

    elem = self.backend.make_elem("tuv")
    seg1 = self.backend.make_elem("seg")
    self.backend.set_text(seg1, "seg1")
    self.backend.append(elem, seg1)
    seg2 = self.backend.make_elem("seg")
    self.backend.set_text(seg2, "seg2")
    self.backend.append(elem, seg2)
    seg3 = self.backend.make_elem("seg")
    self.backend.set_text(seg3, "seg3")
    self.backend.append(elem, seg3)

    message = "Multiple <seg> elements in <tuv>"

    if behavior == "raise":
      with pytest.raises(XmlDeserializationError, match=message):
        handler._deserialize(elem)
    elif behavior == "keep_first":
      tuv = handler._deserialize(elem)
      assert tuv.content == ["seg1"]
    else:
      tuv = handler._deserialize(elem)
      assert tuv.content == ["seg3"]

    assert (self.logger.name, log_level, message) in caplog.record_tuples

  @pytest.mark.parametrize(("behavior"), ("raise", "ignore", "empty"))
  def test_missing_seg_policy(
    self,
    behavior: Literal["raise", "ignore", "empty"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = TuvDeserializer(self.backend, self.policy, self.logger)
    handler.policy.missing_seg = PolicyValue(behavior, log_level)

    elem = self.backend.make_elem("tuv")

    message = "Element <tuv> is missing a <seg> child element"
    if behavior == "raise":
      with pytest.raises(XmlDeserializationError, match=message):
        handler._deserialize(elem)
    elif behavior == "ignore":
      tuv = handler._deserialize(elem)
      assert tuv.content == []
    else:
      tuv = handler._deserialize(elem)
      assert tuv.content == [""]

    assert (self.logger.name, log_level, message) in caplog.record_tuples
    if behavior == "empty":
      assert (
        self.logger.name,
        log_level,
        "Falling back to an empty string",
      ) in caplog.record_tuples

  @pytest.mark.parametrize(("behavior"), ("raise", "keep_first", "keep_last"))
  def test_multiple_header_policy(
    self,
    behavior: Literal["raise", "keep_first", "keep_last"],
    log_level: int,
    caplog: pytest.LogCaptureFixture,
  ) -> None:
    handler = TmxDeserializer(self.backend, self.policy, self.logger)
    handler.policy.multiple_headers = PolicyValue(behavior, log_level)

    elem = self.backend.make_elem("tmx")
    header1 = self.backend.make_elem("header")
    self.backend.set_attr(header1, "creationtool", "tool1")
    self.backend.append(elem, header1)
    header2 = self.backend.make_elem("header")
    self.backend.set_attr(header2, "creationtool", "tool2")
    self.backend.append(elem, header2)
    header3 = self.backend.make_elem("header")
    self.backend.set_attr(header3, "creationtool", "tool3")
    self.backend.append(elem, header3)

    def emit(x):
      return self.mocker.Mock(spec=hm.Header, creationtool=self.backend.get_attr(x, "creationtool"))

    handler._set_emit(emit)

    message = "Multiple <header> elements in <tmx>"

    if behavior == "raise":
      with pytest.raises(XmlDeserializationError, match=message):
        handler._deserialize(elem)
    elif behavior == "keep_first":
      tmx = handler._deserialize(elem)
      assert tmx.header.creationtool == "tool1"
    else:
      tmx = handler._deserialize(elem)
      assert tmx.header.creationtool == "tool3"

    assert (self.logger.name, log_level, message) in caplog.record_tuples

  @pytest.mark.parametrize(("behavior"), ("raise", "ignore"))
  def test_missing_header_policy(
    self, behavior: Literal["raise", "ignore"], log_level: int, caplog: pytest.LogCaptureFixture
  ) -> None:
    handler = TmxDeserializer(self.backend, self.policy, self.logger)
    handler.policy.missing_header = PolicyValue(behavior, log_level)

    elem = self.backend.make_elem("tmx")

    message = "Element <tmx> is missing a <header> child element"

    if behavior == "raise":
      with pytest.raises(XmlDeserializationError, match=message):
        handler._deserialize(elem)
    else:
      tmx = handler._deserialize(elem)
      assert tmx.header is None

    assert (self.logger.name, log_level, message) in caplog.record_tuples