import logging
from datetime import UTC, datetime

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestHeaderSerializer[T]:
  handler: hm.HeaderSerializer
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
    self.handler = hm.HeaderSerializer(backend=self.backend, policy=self.policy, logger=self.logger)

    def test_emit(obj: hm.BaseElement) -> T | None:
      if isinstance(obj, hm.Prop):
        return self.backend.make_elem("prop")
      elif isinstance(obj, hm.Note):
        return self.backend.make_elem("note")
      raise TypeError(f"Invalid object type {type(obj)}")

    self.handler._set_emit(test_emit)

  def make_header_object(self) -> hm.Header:
    return hm.Header(
      creationtool="pytest",
      creationtoolversion="v1",
      segtype=hm.Segtype.SENTENCE,
      o_tmf="TestTMF",
      adminlang="en-US",
      srclang="en-US",
      datatype="plaintext",
      o_encoding="UTF-8",
      creationdate=datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
      creationid="User1",
      changedate=datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC),
      changeid="User2",
      props=[hm.Prop(text="Prop", type="x-test", lang="en-US", o_encoding="UTF-8")],
      notes=[hm.Note(text="Note", lang="en-US", o_encoding="UTF-8")],
    )

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")
    self.handler._set_emit(lambda x: None)
    header = self.make_header_object()

    self.handler._serialize(header)

    spy_make_elem.assert_called_once_with("header")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")

    header = self.make_header_object()

    elem = self.handler._serialize(header)

    assert spy_set_attribute.call_count == 9
    # required attributes
    spy_set_attribute.assert_any_call(elem, header.creationtool, "creationtool", True)
    spy_set_attribute.assert_any_call(elem, header.creationtoolversion, "creationtoolversion", True)
    spy_set_attribute.assert_any_call(elem, header.o_tmf, "o-tmf", False)
    spy_set_attribute.assert_any_call(elem, header.adminlang, "adminlang", True)
    spy_set_attribute.assert_any_call(elem, header.srclang, "srclang", True)
    spy_set_attribute.assert_any_call(elem, header.datatype, "datatype", True)

    # optional attributes
    spy_set_attribute.assert_any_call(elem, header.o_encoding, "o-encoding", False)
    spy_set_attribute.assert_any_call(elem, header.creationid, "creationid", False)
    spy_set_attribute.assert_any_call(elem, header.changeid, "changeid", False)

  def test_calls_set_dt_attribute(self):
    spy_set_dt_attribute = self.mocker.spy(self.handler, "_set_dt_attribute")
    header = self.make_header_object()

    elem = self.handler._serialize(header)

    assert spy_set_dt_attribute.call_count == 2
    spy_set_dt_attribute.assert_any_call(elem, header.creationdate, "creationdate", False)
    spy_set_dt_attribute.assert_any_call(elem, header.changedate, "changedate", False)

  def test_calls_set_enum_attribute(self):
    spy_set_enum_attribute = self.mocker.spy(self.handler, "_set_enum_attribute")
    header = self.make_header_object()

    elem = self.handler._serialize(header)

    spy_set_enum_attribute.assert_called_once_with(
      elem, header.segtype, "segtype", hm.Segtype, True
    )

  def test_returns_None_if_not_Header_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'HeaderSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    header = self.make_header_object()

    elem = self.handler._serialize(header)

    assert elem is not None
    assert spy_emit.call_count == 2
    spy_emit.assert_any_call(header.props[0])
    spy_emit.assert_any_call(header.notes[0])

  def test_calls_backend_to_append_children_elements(self):
    spy_append = self.mocker.spy(self.backend, "append")

    header = self.make_header_object()

    elem = self.handler._serialize(header)

    assert elem is not None
    assert spy_append.call_count == 2
    for i in self.backend.iter_children(elem):
      spy_append.assert_any_call(elem, i)

  def test_raises_if_invalid_child_in_props(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Header.props"
    header = self.make_header_object()
    header.props.append(1)  # type: ignore[list-item]
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._serialize(header)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_in_notes(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Header.notes"
    header = self.make_header_object()
    header.notes.append(1)  # type: ignore[list-item]
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._serialize(header)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
