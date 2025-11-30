from datetime import UTC, datetime
import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import XmlDeserializationError
from python_tmx.base.types import Note, Prop, Segtype, Tu, Tuv
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TuDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTuDeserializer[T_XmlElement]:
  handler: TuDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = TuDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tu_elem(
    self,
    *,
    tag: str = "tu",
    tuid: str | None = "tu001",
    o_encoding: str | None = "UTF-8",
    datatype: str | None = "plaintext",
    usagecount: int | None = 1,
    lastusagedate: datetime | None = datetime(2025, 3, 1, 0, 0, 0, tzinfo=UTC),
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    creationdate: datetime | None = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2025, 2, 1, 0, 0, 0, tzinfo=UTC),
    segtype: Segtype | None = Segtype.SENTENCE,
    changeid: str | None = "User2",
    o_tmf: str | None = "TestTMF",
    srclang: str | None = "en-US",
    props: int = 0,
    notes: int = 0,
    variants: int = 0,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)

    if tuid is not None:
      self.backend.set_attr(elem, "tuid", tuid)
    if o_encoding is not None:
      self.backend.set_attr(elem, "o-encoding", o_encoding)
    if datatype is not None:
      self.backend.set_attr(elem, "datatype", datatype)
    if usagecount is not None:
      self.backend.set_attr(elem, "usagecount", str(usagecount))
    if lastusagedate is not None:
      self.backend.set_attr(elem, "lastusagedate", lastusagedate.isoformat())
    if creationtool is not None:
      self.backend.set_attr(elem, "creationtool", creationtool)
    if creationtoolversion is not None:
      self.backend.set_attr(elem, "creationtoolversion", creationtoolversion)
    if creationdate is not None:
      self.backend.set_attr(elem, "creationdate", creationdate.isoformat())
    if creationid is not None:
      self.backend.set_attr(elem, "creationid", creationid)
    if changedate is not None:
      self.backend.set_attr(elem, "changedate", changedate.isoformat())
    if segtype is not None:
      self.backend.set_attr(elem, "segtype", segtype.value)
    if changeid is not None:
      self.backend.set_attr(elem, "changeid", changeid)
    if o_tmf is not None:
      self.backend.set_attr(elem, "o-tmf", o_tmf)
    if srclang is not None:
      self.backend.set_attr(elem, "srclang", srclang)

    for _ in range(props):
      self.backend.append(elem, self.backend.make_elem("prop"))
    for _ in range(notes):
      self.backend.append(elem, self.backend.make_elem("note"))
    for _ in range(variants):
      self.backend.append(elem, self.backend.make_elem("tuv"))

    return elem

  def test_basic_usage(self, caplog: pytest.LogCaptureFixture):
    elem = self.make_tu_elem(props=1, notes=1, variants=2)

    mock_prop = Prop(text="P", type="T")
    mock_note = Note(text="N")
    mock_tuv1 = Tuv(lang="en", content=["Hello"])
    mock_tuv2 = Tuv(lang="fr", content=["Bonjour"])

    tuv_iter = iter([mock_tuv1, mock_tuv2])

    def side_effect(child):
      tag = self.backend.get_tag(child)
      if tag == "prop":
        return mock_prop
      if tag == "note":
        return mock_note
      if tag == "tuv":
        return next(tuv_iter)
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    tu = self.handler._deserialize(elem)

    assert isinstance(tu, Tu)
    assert tu.tuid == "tu001"
    assert tu.o_encoding == "UTF-8"
    assert tu.datatype == "plaintext"
    assert tu.usagecount == 1
    assert tu.lastusagedate == datetime(2025, 3, 1, 0, 0, 0, tzinfo=UTC)
    assert tu.creationtool == "pytest"
    assert tu.creationtoolversion == "v1"
    assert tu.creationdate == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    assert tu.creationid == "User1"
    assert tu.changedate == datetime(2025, 2, 1, 0, 0, 0, tzinfo=UTC)
    assert tu.segtype == Segtype.SENTENCE
    assert tu.changeid == "User2"
    assert tu.o_tmf == "TestTMF"
    assert tu.srclang == "en-US"

    assert tu.props == [mock_prop]
    assert tu.notes == [mock_note]
    assert tu.variants == [mock_tuv1, mock_tuv2]

    assert mock_emit.call_count == 4
    for i in self.backend.iter_children(elem):
      mock_emit.assert_any_call(i)

    assert caplog.records == []

  def test_extra_text_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.set_text(elem, "Garbage Data")

    self.policy.extra_text.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.extra_text.log_level = log_level

    with pytest.raises(
      XmlDeserializationError, match="Element <tu> has extra text content 'Garbage Data'"
    ):
      self.handler._deserialize(elem)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tu> has extra text content 'Garbage Data'",
    )
    assert caplog.record_tuples == [expected_log]

  def test_extra_text_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.set_text(elem, "Garbage Data")

    self.policy.extra_text.behavior = "ignore"
    self.policy.extra_text.log_level = log_level

    tu = self.handler._deserialize(elem)
    assert isinstance(tu, Tu)

    expected_log = (
      self.logger.name,
      log_level,
      "Element <tu> has extra text content 'Garbage Data'",
    )
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = (
      "raise"  # Default but setting it explicitly for testing purposes
    )
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Invalid child element <wrong> in <tu>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tu>")
    assert caplog.record_tuples == [expected_log]

  def test_inavlid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tu_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tu = self.handler._deserialize(elem)
    assert isinstance(tu, Tu)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tu>")
    assert caplog.record_tuples == [expected_log]
