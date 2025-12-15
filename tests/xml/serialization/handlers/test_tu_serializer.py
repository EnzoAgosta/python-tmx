import logging
from datetime import UTC, datetime

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm

singleton = object()


class TestTuSerializer[T]:
  handler: hm.TuSerializer
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.SerializationPolicy()
    self.mocker = mocker
    self.handler = hm.TuSerializer(backend=self.backend, policy=self.policy, logger=self.logger)

    def test_emit(obj: hm.BaseElement) -> T | None:
      if isinstance(obj, hm.Prop):
        return self.backend.make_elem("prop")
      elif isinstance(obj, hm.Note):
        return self.backend.make_elem("note")
      elif isinstance(obj, hm.Tuv):
        return self.backend.make_elem("tuv")
      elif obj is singleton:
        return None
      raise TypeError(f"Invalid object type {type(obj)}")

    self.handler._set_emit(test_emit)

  def make_tu_object(self) -> hm.Tu:
    return hm.Tu(
      tuid="tu001",
      o_encoding="UTF-8",
      datatype="plaintext",
      usagecount=1,
      lastusagedate=datetime(2025, 3, 1, 12, 0, 0, tzinfo=UTC),
      creationtool="pytest",
      creationtoolversion="v1",
      creationdate=datetime(2025, 1, 1, 14, 30, 0, tzinfo=UTC),
      creationid="User1",
      changedate=datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC),
      changeid="User2",
      segtype=hm.Segtype.SENTENCE,
      o_tmf="TestTMF",
      srclang="en-US",
      props=[hm.Prop(text="Prop", type="x-test", lang="en-US", o_encoding="UTF-8")],
      notes=[hm.Note(text="Note", lang="en-US", o_encoding="UTF-8")],
      variants=[
        hm.Tuv(lang="en-US", content=["Hello World"]),
        hm.Tuv(lang="fr-FR", content=["Bonjour le monde"]),
      ],
    )

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")
    self.handler._set_emit(lambda x: None)
    tu = self.make_tu_object()

    self.handler._serialize(tu)

    assert spy_make_elem.call_count == 1
    spy_make_elem.assert_any_call("tu")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")

    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert spy_set_attribute.call_count == 9
    # optional attributes
    spy_set_attribute.assert_any_call(elem, tu.tuid, "tuid", False)
    spy_set_attribute.assert_any_call(elem, tu.o_encoding, "o-encoding", False)
    spy_set_attribute.assert_any_call(elem, tu.datatype, "datatype", False)
    spy_set_attribute.assert_any_call(elem, tu.creationtool, "creationtool", False)
    spy_set_attribute.assert_any_call(elem, tu.creationtoolversion, "creationtoolversion", False)
    spy_set_attribute.assert_any_call(elem, tu.creationid, "creationid", False)
    spy_set_attribute.assert_any_call(elem, tu.changeid, "changeid", False)
    spy_set_attribute.assert_any_call(elem, tu.o_tmf, "o-tmf", False)
    spy_set_attribute.assert_any_call(elem, tu.srclang, "srclang", False)

  def test_calls_set_dt_attribute(self):
    spy_set_dt_attribute = self.mocker.spy(self.handler, "_set_dt_attribute")
    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert spy_set_dt_attribute.call_count == 3
    spy_set_dt_attribute.assert_any_call(elem, tu.creationdate, "creationdate", False)
    spy_set_dt_attribute.assert_any_call(elem, tu.changedate, "changedate", False)
    spy_set_dt_attribute.assert_any_call(elem, tu.lastusagedate, "lastusagedate", False)

  def test_calls_set_int_attribute(self):
    spy_set_int_attribute = self.mocker.spy(self.handler, "_set_int_attribute")
    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert elem is not None
    spy_set_int_attribute.assert_called_once_with(elem, tu.usagecount, "usagecount", False)

  def test_calls_set_enum_attribute(self):
    spy_set_enum_attribute = self.mocker.spy(self.handler, "_set_enum_attribute")
    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert elem is not None
    spy_set_enum_attribute.assert_called_once_with(elem, tu.segtype, "segtype", hm.Segtype, False)

  def test_returns_None_if_not_Tu_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'TuSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert elem is not None
    assert spy_emit.call_count == 4
    spy_emit.assert_any_call(tu.props[0])
    spy_emit.assert_any_call(tu.notes[0])
    spy_emit.assert_any_call(tu.variants[0])
    spy_emit.assert_any_call(tu.variants[1])

  def test_calls_backend_to_append_children_elements(self):
    spy_append = self.mocker.spy(self.backend, "append")

    tu = self.make_tu_object()

    elem = self.handler._serialize(tu)

    assert elem is not None
    assert spy_append.call_count == 4
    for i in self.backend.iter_children(elem):
      if self.backend.get_tag(i) == "prop":
        spy_append.assert_any_call(elem, i)
      elif self.backend.get_tag(i) == "note":
        spy_append.assert_any_call(elem, i)
      elif self.backend.get_tag(i) == "tuv":
        spy_append.assert_any_call(elem, i)
      else:
        raise ValueError(f"Invalid tag {self.backend.get_tag(i)}")

  def test_raises_if_invalid_child_in_props(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tu.props"
    tu = self.make_tu_object()
    tu.props.append(1)  # type: ignore[list-item]
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._serialize(tu)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_child_in_props(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tu = self.make_tu_object()
    tu.props = [singleton]  # type: ignore[list-item]

    self.handler._serialize(tu)

    expected_log = (
      self.logger.name,
      log_level,
      "Invalid child element 'object' in Tu.props",
    )
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_in_notes(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tu.notes"
    tu = self.make_tu_object()
    tu.notes.append(1)  # type: ignore[list-item]
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._serialize(tu)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_child_in_notes(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tu = self.make_tu_object()
    tu.notes = [singleton]  # type: ignore[list-item]

    self.handler._serialize(tu)

    expected_log = (
      self.logger.name,
      log_level,
      "Invalid child element 'object' in Tu.notes",
    )
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_in_variants(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tu.variants"
    tu = self.make_tu_object()
    tu.variants.append(1)  # type: ignore[list-item]
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._serialize(tu)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_child_in_variants(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tu = self.make_tu_object()
    tu.variants = [singleton]  # type: ignore[list-item]

    self.handler._serialize(tu)

    expected_log = (
      self.logger.name,
      log_level,
      "Invalid child element 'object' in Tu.variants",
    )
    assert caplog.record_tuples == [expected_log]
