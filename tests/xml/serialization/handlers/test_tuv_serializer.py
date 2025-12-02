from datetime import UTC, datetime
import logging

import pytest
from pytest_mock import MockerFixture
from python_tmx.base.errors import XmlSerializationError
from python_tmx.base.types import BaseElement, Bpt, Note, Prop, Tuv
from python_tmx.xml import XML_NS
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import TuvSerializer


class TestTuvSerializer[T_XmlElement]:
  handler: TuvSerializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.mocker = mocker
    self.handler = TuvSerializer(backend=self.backend, policy=self.policy, logger=self.logger)

    def test_emit(obj: BaseElement) -> T_XmlElement | None:
      if isinstance(obj, Prop):
        return self.backend.make_elem("prop")
      elif isinstance(obj, Note):
        return self.backend.make_elem("note")
      elif isinstance(obj, Bpt):
        return self.backend.make_elem("bpt")
      raise TypeError(f"Invalid object type {type(obj)}")

    self.handler._set_emit(test_emit)

  def make_tuv_object(self) -> Tuv:
    return Tuv(
      lang="en-US",
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
      o_tmf="TestTMF",
      props=[Prop(text="Prop", type="x-test", lang="en-US", o_encoding="UTF-8")],
      notes=[Note(text="Note", lang="en-US", o_encoding="UTF-8")],
      content=["First", Bpt(content=["Bpt content"], i=1, x=1, type="bpt"), "Second"],
    )

  def test_calls_backend_make_elem(self):
    spy_make_elem = self.mocker.spy(self.backend, "make_elem")
    self.handler._set_emit(lambda x: None)
    tuv = self.make_tuv_object()

    self.handler._serialize(tuv)

    assert spy_make_elem.call_count == 2
    spy_make_elem.assert_any_call("tuv")
    spy_make_elem.assert_any_call("seg")

  def test_calls_set_attribute(self):
    spy_set_attribute = self.mocker.spy(self.handler, "_set_attribute")

    tuv = self.make_tuv_object()

    elem = self.handler._serialize(tuv)

    assert spy_set_attribute.call_count == 8
    # required attribute
    spy_set_attribute.assert_any_call(elem, tuv.lang, f"{XML_NS}lang", True)

    # optional attributes
    spy_set_attribute.assert_any_call(elem, tuv.o_encoding, "o-encoding", False)
    spy_set_attribute.assert_any_call(elem, tuv.datatype, "datatype", False)
    spy_set_attribute.assert_any_call(elem, tuv.creationtool, "creationtool", False)
    spy_set_attribute.assert_any_call(elem, tuv.creationtoolversion, "creationtoolversion", False)
    spy_set_attribute.assert_any_call(elem, tuv.creationid, "creationid", False)
    spy_set_attribute.assert_any_call(elem, tuv.changeid, "changeid", False)
    spy_set_attribute.assert_any_call(elem, tuv.o_tmf, "o-tmf", False)

  def test_calls_set_dt_attribute(self):
    spy_set_dt_attribute = self.mocker.spy(self.handler, "_set_dt_attribute")
    tuv = self.make_tuv_object()

    elem = self.handler._serialize(tuv)

    assert spy_set_dt_attribute.call_count == 3
    spy_set_dt_attribute.assert_any_call(elem, tuv.creationdate, "creationdate", False)
    spy_set_dt_attribute.assert_any_call(elem, tuv.changedate, "changedate", False)
    spy_set_dt_attribute.assert_any_call(elem, tuv.lastusagedate, "lastusagedate", False)

  def test_calls_set_int_attribute(self):
    spy_set_int_attribute = self.mocker.spy(self.handler, "_set_int_attribute")
    tuv = self.make_tuv_object()

    elem = self.handler._serialize(tuv)

    assert elem is not None
    spy_set_int_attribute.assert_called_once_with(elem, tuv.usagecount, "usagecount", False)

  def test_returns_None_if_not_Tuv_if_policy_is_ignore(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'TuvSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_calls_emit(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    tuv = self.make_tuv_object()

    elem = self.handler._serialize(tuv)

    assert elem is not None
    assert spy_emit.call_count == 3
    spy_emit.assert_any_call(tuv.props[0])
    spy_emit.assert_any_call(tuv.notes[0])
    spy_emit.assert_any_call(tuv.content[1])

  def test_calls_backend_to_append_children_elements(self):
    spy_append = self.mocker.spy(self.backend, "append")

    tuv = self.make_tuv_object()

    elem = self.handler._serialize(tuv)

    assert elem is not None
    assert spy_append.call_count == 4
    for i in self.backend.iter_children(elem):
      if self.backend.get_tag(i) == "prop":
        spy_append.assert_any_call(elem, i)
      elif self.backend.get_tag(i) == "note":
        spy_append.assert_any_call(elem, i)
      elif self.backend.get_tag(i) == "seg":
        spy_append.assert_any_call(elem, i)
        for j in self.backend.iter_children(i):
          spy_append.assert_any_call(i, j)
      else:
        raise ValueError(f"Invalid tag {self.backend.get_tag(i)}")

  def test_raises_if_invalid_child_in_props(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tuv.props"
    tuv = self.make_tuv_object()
    tuv.props.append(1)  # type: ignore[list-item]
    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(tuv)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_in_notes(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Tuv.notes"
    tuv = self.make_tuv_object()
    tuv.notes.append(1)  # type: ignore[list-item]
    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(tuv)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
