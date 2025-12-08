import logging
from datetime import UTC, datetime

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class FakeBaseElementDeserializer[T](
  hm.BaseElementDeserializer[T], hm.InlineContentDeserializerMixin[T]
):
  def _deserialize(self, element: T) -> hm.BaseElement | None:
    raise NotImplementedError


class TestBaseElementDeserializer[T]:
  handler: FakeBaseElementDeserializer
  backend: hm.XMLBackend[T]
  logger: logging.Logger
  policy: hm.DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.DeserializationPolicy()
    self.mocker = mocker

    self.handler = FakeBaseElementDeserializer(
      backend=self.backend, policy=self.policy, logger=self.logger
    )

  def test_set_emit(self):
    fake_emit = lambda x: None  # noqa: E731
    self.handler._set_emit(fake_emit)
    assert self.handler._emit is fake_emit

  def test_emit_raise_if_not_set(self):
    with pytest.raises(AssertionError, match=r"emit\(\) called before set_emit\(\) was called"):
      self.handler.emit(None)

  def test_check_tag_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("wrong")

    self.policy.invalid_tag.behavior = "raise"
    self.policy.invalid_tag.log_level = log_level

    with pytest.raises(hm.InvalidTagError, match="Incorrect tag: expected right, got wrong"):
      self.handler._check_tag(elem, "right")

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected right, got wrong")
    assert caplog.record_tuples == [expected_log]

  def test_check_tag_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.backend.make_elem("wrong")

    self.policy.invalid_tag.behavior = "ignore"
    self.policy.invalid_tag.log_level = log_level

    self.handler._check_tag(elem, "right")

    expected_log = (self.logger.name, log_level, "Incorrect tag: expected right, got wrong")
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_int_raise_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Missing required attribute 'missing' on element <elem>"

    with pytest.raises(hm.XmlDeserializationError, match=log_message):
      self.handler._parse_attribute_as_int(elem, "missing", True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_int_ignore_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    val = self.handler._parse_attribute_as_int(elem, "missing", True)
    assert val is None

    log_message = "Missing required attribute 'missing' on element <elem>"
    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_int_returns_int(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "1")

    val = self.handler._parse_attribute_as_int(elem, "attr", True)
    assert val == 1

  def test_parse_attribute_as_int_raise_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "raise"
    self.policy.invalid_attribute_value.log_level = log_level

    log_msg = "Cannot convert 'invalid' to an int for attribute attr"
    with pytest.raises(hm.XmlDeserializationError, match=log_msg):
      self.handler._parse_attribute_as_int(elem, "attr", True)

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_int_ignore_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    val = self.handler._parse_attribute_as_int(elem, "attr", True)
    assert val is None

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to an int for attribute attr",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_enum_raise_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Missing required attribute 'missing' on element <elem>"

    with pytest.raises(hm.XmlDeserializationError, match=log_message):
      self.handler._parse_attribute_as_enum(elem, "missing", hm.Segtype, True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_enum_ignore_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    val = self.handler._parse_attribute_as_enum(elem, "missing", hm.Segtype, True)
    assert val is None

    log_message = "Missing required attribute 'missing' on element <elem>"
    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_enum_returns_enum(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "block")

    val = self.handler._parse_attribute_as_enum(elem, "attr", hm.Segtype, True)
    assert val == hm.Segtype.BLOCK

  def test_parse_attribute_as_enum_raise_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "raise"
    self.policy.invalid_attribute_value.log_level = log_level

    log_msg = "Value 'invalid' is not a valid enum value for attribute attr"
    with pytest.raises(hm.XmlDeserializationError, match=log_msg):
      self.handler._parse_attribute_as_enum(elem, "attr", hm.Segtype, True)

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_enum_ignore_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    val = self.handler._parse_attribute_as_enum(elem, "attr", hm.Segtype, True)
    assert val is None

    expected_log = (
      self.logger.name,
      log_level,
      "Value 'invalid' is not a valid enum value for attribute attr",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_dt_raise_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Missing required attribute 'missing' on element <elem>"

    with pytest.raises(hm.XmlDeserializationError, match=log_message):
      self.handler._parse_attribute_as_dt(elem, "missing", True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_dt_ignore_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    val = self.handler._parse_attribute_as_dt(elem, "missing", True)
    assert val is None

    log_message = "Missing required attribute 'missing' on element <elem>"
    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_as_dt_returns_dt(self):
    elem = self.backend.make_elem("elem")
    dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    self.backend.set_attr(elem, "attr", dt.isoformat())

    val = self.handler._parse_attribute_as_dt(elem, "attr", True)
    assert val == dt

  def test_parse_attribute_as_dt_raise_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "raise"
    self.policy.invalid_attribute_value.log_level = log_level

    log_msg = "Cannot convert 'invalid' to a datetime object for attribute attr"
    with pytest.raises(hm.XmlDeserializationError, match=log_msg):
      self.handler._parse_attribute_as_dt(elem, "attr", True)

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_as_dt_ignore_if_invalid(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "invalid")

    self.policy.invalid_attribute_value.behavior = "ignore"
    self.policy.invalid_attribute_value.log_level = log_level

    val = self.handler._parse_attribute_as_dt(elem, "attr", True)
    assert val is None

    expected_log = (
      self.logger.name,
      log_level,
      "Cannot convert 'invalid' to a datetime object for attribute attr",
    )
    assert caplog.record_tuples == [expected_log]

  def test_parse_attribute_raise_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Missing required attribute 'missing' on element <elem>"

    with pytest.raises(hm.XmlDeserializationError, match=log_message):
      self.handler._parse_attribute(elem, "missing", True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_ignore_if_required_and_missing(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    val = self.handler._parse_attribute(elem, "missing", True)
    assert val is None

    log_message = "Missing required attribute 'missing' on element <elem>"
    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_parse_attribute_returns_value(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "attr", "value")

    val = self.handler._parse_attribute(elem, "attr", True)
    assert val == "value"

  def test_deserialize_content_raises_if_invalid_child_element(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    child = self.backend.make_elem("wrong")
    self.backend.set_text(child, "Invalid")
    self.backend.append(elem, child)
    log_message = "Incorrect child element in elem: expected one of child, got wrong"

    self.policy.invalid_child_element.behavior = "raise"
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(hm.XmlDeserializationError, match=log_message):
      self.handler.deserialize_content(elem, ("child",))

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_deserialize_content_ignores_invalid_child_element(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "Valid")
    child = self.backend.make_elem("wrong")
    self.backend.set_text(child, "Invalid")
    self.backend.append(elem, child)
    log_message = "Incorrect child element in elem: expected one of child, got wrong"

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    val = self.handler.deserialize_content(elem, ("child",))
    assert val == ["Valid"]

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_calls_emeit(self):
    mock_emit = self.mocker.Mock()
    self.handler._set_emit(mock_emit)
    elem = self.backend.make_elem("elem")
    child = self.backend.make_elem("child")
    self.backend.set_text(child, "Valid")
    self.backend.append(elem, child)

    self.handler.deserialize_content(elem, ("child",))

    mock_emit.assert_called_once_with(child)

  def test_returns_content_in_order(self):
    mock_emit = self.mocker.Mock(side_effect=lambda x: self.backend.get_text(x))
    self.handler._set_emit(mock_emit)

    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "first")
    child1 = self.backend.make_elem("child1")
    self.backend.set_text(child1, "child1 text")
    self.backend.set_tail(child1, "in between")
    self.backend.append(elem, child1)
    child2 = self.backend.make_elem("child2")
    self.backend.set_text(child2, "child2 text")
    self.backend.set_tail(child2, "last")
    self.backend.append(elem, child2)

    val = self.handler.deserialize_content(elem, ("child1", "child2"))
    assert val == ["first", "child1 text", "in between", "child2 text", "last"]

  def test_deserialize_content_raises_if_empty_content(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    mock_emit = self.mocker.Mock(side_effect=lambda x: self.backend.get_text(x))
    self.handler._set_emit(mock_emit)
    elem = self.backend.make_elem("elem")
    self.backend.append(elem, self.backend.make_elem("child"))

    self.policy.empty_content.behavior = "raise"
    self.policy.empty_content.log_level = log_level

    with pytest.raises(hm.XmlDeserializationError, match="Element <elem> is empty"):
      self.handler.deserialize_content(elem, ("child",))

    expected_log = (self.logger.name, log_level, "Element <elem> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_deserialize_content_ignores_empty_content(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    mock_emit = self.mocker.Mock(side_effect=lambda x: self.backend.get_text(x))
    self.handler._set_emit(mock_emit)
    elem = self.backend.make_elem("elem")
    self.backend.append(elem, self.backend.make_elem("child"))

    self.policy.empty_content.behavior = "ignore"
    self.policy.empty_content.log_level = log_level

    val = self.handler.deserialize_content(elem, ("child",))
    assert val == []

    expected_log = (self.logger.name, log_level, "Element <elem> is empty")
    assert caplog.record_tuples == [expected_log]

  def test_deserialize_content_raises_add_empty_string_if_empty_content(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    mock_emit = self.mocker.Mock(side_effect=lambda x: self.backend.get_text(x))
    self.handler._set_emit(mock_emit)
    elem = self.backend.make_elem("elem")
    self.backend.append(elem, self.backend.make_elem("child"))

    self.policy.empty_content.behavior = "empty"
    self.policy.empty_content.log_level = log_level

    val = self.handler.deserialize_content(elem, ("child",))
    assert val == [""]

    expected_logs = [
      (self.logger.name, log_level, "Element <elem> is empty"),
      (self.logger.name, log_level, "Falling back to an empty string"),
    ]
    assert caplog.record_tuples == expected_logs
