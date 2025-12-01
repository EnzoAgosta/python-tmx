from datetime import UTC, datetime
import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import XmlSerializationError
from python_tmx.base.types import Header, Note, Prop, Segtype
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.policy import SerializationPolicy
from python_tmx.xml.serialization._handlers import HeaderSerializer


class TestHeaderSerializer[T_XmlElement]:
  handler: HeaderSerializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()

    self.handler = HeaderSerializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_header_object(
    self,
    *,
    creationtool: str | None = "pytest",
    creationtoolversion: str | None = "v1",
    segtype: Segtype | None = Segtype.SENTENCE,
    o_tmf: str | None = "TestTMF",
    adminlang: str | None = "en-US",
    srclang: str | None = "en-US",
    datatype: str | None = "plaintext",
    o_encoding: str | None = "UTF-8",
    creationdate: datetime | None = datetime(2025, 1, 1, 12, 0, 0, tzinfo=UTC),
    creationid: str | None = "User1",
    changedate: datetime | None = datetime(2025, 2, 1, 14, 30, 0, tzinfo=UTC),
    changeid: str | None = "User2",
    props: int = 1,
    notes: int = 1,
  ) -> Header:
    return Header(
      creationtool=creationtool,  # type: ignore[arg-type]
      creationtoolversion=creationtoolversion,  # type: ignore[arg-type]
      segtype=segtype,  # type: ignore[arg-type]
      o_tmf=o_tmf,  # type: ignore[arg-type]
      adminlang=adminlang,  # type: ignore[arg-type]
      srclang=srclang,  # type: ignore[arg-type]
      datatype=datatype,  # type: ignore[arg-type]
      o_encoding=o_encoding,
      creationdate=creationdate,
      creationid=creationid,
      changedate=changedate,
      changeid=changeid,
      props=[Prop(text=f"Prop{i}", type="x-test") for i in range(props)],
      notes=[Note(text=f"Note{i}") for i in range(notes)],
    )

  def test_calls_backend_make_elem(self, caplog: pytest.LogCaptureFixture, log_level: int):
    original = self.backend.make_elem
    mock_make_elem = Mock(side_effect=lambda x: original(x))
    self.backend.make_elem = mock_make_elem

    header = self.make_header_object()
    self.handler._serialize(header)

    mock_make_elem.assert_called_once_with("header")

  def test_calls_set_attribute(self):
    mock_set_attribute = Mock()
    mock_set_dt_attribute = Mock()
    mock_set_enum_attribute = Mock()
    self.handler._set_attribute = mock_set_attribute
    self.handler._set_dt_attribute = mock_set_dt_attribute
    self.handler._set_enum_attribute = mock_set_enum_attribute

    header = self.make_header_object()
    elem = self.handler._serialize(header)

    assert mock_set_attribute.call_count == 9
    mock_set_attribute.assert_any_call(elem, header.creationtool, "creationtool", True)
    mock_set_attribute.assert_any_call(
      elem, header.creationtoolversion, "creationtoolversion", True
    )
    mock_set_attribute.assert_any_call(elem, header.o_tmf, "o-tmf", False)
    mock_set_attribute.assert_any_call(elem, header.adminlang, "adminlang", True)
    mock_set_attribute.assert_any_call(elem, header.srclang, "srclang", True)
    mock_set_attribute.assert_any_call(elem, header.datatype, "datatype", True)
    mock_set_attribute.assert_any_call(elem, header.o_encoding, "o-encoding", False)
    mock_set_attribute.assert_any_call(elem, header.creationid, "creationid", False)
    mock_set_attribute.assert_any_call(elem, header.changeid, "changeid", False)

    assert mock_set_dt_attribute.call_count == 2
    mock_set_dt_attribute.assert_any_call(elem, header.creationdate, "creationdate", False)
    mock_set_dt_attribute.assert_any_call(elem, header.changedate, "changedate", False)

    mock_set_enum_attribute.assert_called_once_with(elem, header.segtype, "segtype", Segtype, True)

  def test_calls_emits(self):
    mock_emit = Mock(side_effect=lambda x: self.backend.make_elem(x.text))
    self.handler._set_emit(mock_emit)

    header = self.make_header_object()
    self.handler._serialize(header)

    assert mock_emit.call_count == 2
    mock_emit.assert_any_call(header.props[0])
    mock_emit.assert_any_call(header.notes[0])

  def test_raises_if_invalid_object_type(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_object_type.behavior = "raise"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'HeaderSerializer'"

    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(1)  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_object_type(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    log_message = "Cannot serialize object of type 'int' to xml element using 'HeaderSerializer'"

    assert self.handler._serialize(1) is None  # type: ignore[arg-type]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_raises_if_invalid_child_element(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Header"

    header = self.make_header_object()
    header.props.append(1)  # type: ignore[list-item]

    with pytest.raises(XmlSerializationError, match=log_message):
      self.handler._serialize(header)

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_ignores_if_invalid_child_element(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    log_message = "Invalid child element 'int' in Header"

    header = self.make_header_object(props=0, notes=0)
    header.props.append(1)  # type: ignore[list-item]

    elem = self.handler._serialize(header)

    assert elem is not None
    assert [c for c in self.backend.iter_children(elem)] == []

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]
