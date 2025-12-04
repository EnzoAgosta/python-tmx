import logging
from datetime import UTC, datetime

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class FakeBaseElementSerializer(
  hm.BaseElementSerializer[hm.T_XmlElement], hm.InlineContentSerializerMixin[hm.T_XmlElement]
):
  def _serialize(self, obj: hm.BaseElement) -> hm.T_XmlElement | None:
    raise NotImplementedError


class TestBaseElementSerializer[T_XmlElement]:
  handler: FakeBaseElementSerializer
  backend: hm.XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: hm.SerializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(
    self, backend: hm.XMLBackend[T_XmlElement], test_logger: logging.Logger, mocker: MockerFixture
  ):
    self.backend = backend
    self.logger = test_logger
    self.policy = hm.SerializationPolicy()
    self.mocker = mocker

    self.handler = FakeBaseElementSerializer(
      backend=self.backend, policy=self.policy, logger=self.logger
    )

  def test_set_emit(self):
    fake_emit = lambda x: None  # noqa: E731
    self.handler._set_emit(fake_emit)
    assert self.handler._emit is fake_emit

  def test_emit_raise_if_not_set(self):
    with pytest.raises(AssertionError, match=r"emit\(\) called before set_emit\(\) was called"):
      self.handler.emit(None)  # type: ignore

  def test_check_obj_type_returns_true(self):
    assert self.handler._check_obj_type(hm.Bpt(i=1), hm.Bpt) is True

  def test_check_obj_type_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_object_type.behavior = "raise"
    self.policy.invalid_object_type.log_level = log_level

    log_message = (
      "Cannot serialize object of type 'int' to xml element using 'FakeBaseElementSerializer'"
    )
    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._check_obj_type(1, hm.Bpt)  # type: ignore

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_check_obj_type_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    log_message = (
      "Cannot serialize object of type 'int' to xml element using 'FakeBaseElementSerializer'"
    )

    self.policy.invalid_object_type.behavior = "ignore"
    self.policy.invalid_object_type.log_level = log_level

    assert self.handler._check_obj_type(1, hm.Bpt) is False  # type: ignore

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_set_dt_attribute_works(self):
    elem = self.backend.make_elem("elem")
    dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
    self.handler._set_dt_attribute(elem, dt, "date", False)
    assert self.backend.get_attr(elem, "date") == dt.isoformat()

  def test_set_dt_attribute_raises_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    dt = "wrong"

    self.policy.invalid_attribute_type.behavior = "raise"
    self.policy.invalid_attribute_type.log_level = log_level

    log_msg = "Attribute 'date' is not a datetime object"
    with pytest.raises(hm.XmlSerializationError, match=log_msg):
      self.handler._set_dt_attribute(elem, dt, "date", False)  # type: ignore

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_set_dt_attribute_ignores_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")
    dt = "wrong"

    self.policy.invalid_attribute_type.behavior = "ignore"
    self.policy.invalid_attribute_type.log_level = log_level

    self.handler._set_dt_attribute(elem, dt, "date", False)  # type: ignore
    assert self.backend.get_attr(elem, "date") is None

    expected_log = (self.logger.name, log_level, "Attribute 'date' is not a datetime object")
    assert caplog.record_tuples == [expected_log]

  def test_set_dt_attribute_raises_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_msg = "Required attribute 'date' is None"

    with pytest.raises(hm.XmlSerializationError, match=log_msg):
      self.handler._set_dt_attribute(elem, None, "date", True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_msg)]

  def test_set_dt_attribute_ignores_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Required attribute 'date' is None"

    self.handler._set_dt_attribute(elem, None, "date", True)
    assert self.backend.get_attr(elem, "date") is None

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_set_int_attribute_works(self):
    elem = self.backend.make_elem("elem")
    self.handler._set_int_attribute(elem, 1, "attr", False)
    assert self.backend.get_attr(elem, "attr") == "1"

  def test_set_int_attribute_raises_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "raise"
    self.policy.invalid_attribute_type.log_level = log_level

    log_msg = "Attribute 'attr' is not an int"
    with pytest.raises(hm.XmlSerializationError, match=log_msg):
      self.handler._set_int_attribute(elem, "invalid", "attr", False)  # type: ignore

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_set_int_attribute_ignores_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "ignore"
    self.policy.invalid_attribute_type.log_level = log_level

    self.handler._set_int_attribute(elem, "invalid", "attr", False)  # type: ignore
    assert self.backend.get_attr(elem, "attr") is None

    expected_log = (self.logger.name, log_level, "Attribute 'attr' is not an int")
    assert caplog.record_tuples == [expected_log]

  def test_set_int_attribute_raises_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_msg = "Required attribute 'attr' is None"

    with pytest.raises(hm.XmlSerializationError, match=log_msg):
      self.handler._set_int_attribute(elem, None, "attr", True)

    assert caplog.record_tuples == [(self.logger.name, log_level, log_msg)]

  def test_set_int_attribute_ignores_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Required attribute 'attr' is None"

    self.handler._set_int_attribute(elem, None, "attr", True)
    assert self.backend.get_attr(elem, "attr") is None

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_set_enum_attribute_works(self):
    elem = self.backend.make_elem("elem")
    self.handler._set_enum_attribute(elem, hm.Segtype.BLOCK, "attr", hm.Segtype, False)
    assert self.backend.get_attr(elem, "attr") == "block"

  def test_set_enum_attribute_raises_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "raise"
    self.policy.invalid_attribute_type.log_level = log_level

    log_msg = "Attribute 'attr' is not a <enum 'Segtype'>"

    with pytest.raises(hm.XmlSerializationError, match=log_msg):
      self.handler._set_enum_attribute(elem, "invalid", "attr", hm.Segtype, False)  # type: ignore

    expected_log = (self.logger.name, log_level, log_msg)
    assert caplog.record_tuples == [expected_log]

  def test_set_enum_attribute_ignores_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "ignore"
    self.policy.invalid_attribute_type.log_level = log_level

    self.handler._set_enum_attribute(elem, "invalid", "attr", hm.Segtype, False)  # type: ignore
    assert self.backend.get_attr(elem, "attr") is None

    log_message = "Attribute 'attr' is not a <enum 'Segtype'>"

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_set_enum_attribute_raises_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_messsage = "Required attribute 'attr' is None"

    with pytest.raises(hm.XmlSerializationError, match=log_messsage):
      self.handler._set_enum_attribute(elem, None, "attr", hm.Segtype, True)  # type: ignore

    assert caplog.record_tuples == [(self.logger.name, log_level, log_messsage)]

  def test_set_enum_attribute_ignores_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    self.handler._set_enum_attribute(elem, None, "attr", hm.Segtype, True)  # type: ignore
    assert self.backend.get_attr(elem, "attr") is None

    assert caplog.record_tuples == [
      (self.logger.name, log_level, "Required attribute 'attr' is None")
    ]

  def test_set_attribute_works(self):
    elem = self.backend.make_elem("elem")
    self.handler._set_attribute(elem, "value", "attr", False)
    assert self.backend.get_attr(elem, "attr") == "value"

  def test_set_attribute_raises_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "raise"
    self.policy.invalid_attribute_type.log_level = log_level

    log_messsage = "Attribute 'attr' is not a string"

    with pytest.raises(hm.XmlSerializationError, match=log_messsage):
      self.handler._set_attribute(elem, 1, "attr", False)  # type: ignore

    expected_log = (self.logger.name, log_level, log_messsage)
    assert caplog.record_tuples == [expected_log]

  def test_set_attribute_ignores_if_invalid_type(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_attribute_type.behavior = "ignore"
    self.policy.invalid_attribute_type.log_level = log_level

    self.handler._set_attribute(elem, 1, "attr", False)  # type: ignore
    assert self.backend.get_attr(elem, "attr") is None

    expected_log = (self.logger.name, log_level, "Attribute 'attr' is not a string")
    assert caplog.record_tuples == [expected_log]

  def test_set_attribute_raises_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "raise"
    self.policy.required_attribute_missing.log_level = log_level

    log_message = "Required attribute 'attr' is None"

    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler._set_attribute(elem, None, "attr", True)  # type: ignore

    assert caplog.record_tuples == [(self.logger.name, log_level, log_message)]

  def test_set_attribute_ignores_if_None_and_required(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    self.handler._set_attribute(elem, None, "attr", True)  # type: ignore
    assert self.backend.get_attr(elem, "attr") is None

    expected_log = (self.logger.name, log_level, "Required attribute 'attr' is None")
    assert caplog.record_tuples == [expected_log]

  def test_serialize_content_raises_if_disallowed_child_element(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_content_type.behavior = "raise"
    self.policy.invalid_content_type.log_level = log_level

    log_message = "Incorrect child element in Bpt: expected one of Sub, got int"

    with pytest.raises(hm.XmlSerializationError, match=log_message):
      self.handler.serialize_content(hm.Bpt(i=1, content=[1]), elem, (hm.Sub,))  # type: ignore

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_serialize_content_ignores_disallowed_child_element(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    elem = self.backend.make_elem("elem")

    self.policy.invalid_content_type.behavior = "ignore"
    self.policy.invalid_content_type.log_level = log_level

    log_message = "Incorrect child element in Bpt: expected one of Sub, got int"

    self.handler.serialize_content(hm.Bpt(i=1, content=["Hello", 1]), elem, (hm.Sub,))  # type: ignore
    assert self.backend.get_text(elem) == "Hello"

    expected_log = (self.logger.name, log_level, log_message)
    assert caplog.record_tuples == [expected_log]

  def test_serialize_content_serializes_in_order(
    self, caplog: pytest.LogCaptureFixture, log_level: int
  ):
    self.handler._set_emit(lambda x: self.backend.make_elem("sub"))
    elem = self.backend.make_elem("elem")

    self.handler.serialize_content(
      hm.Bpt(i=1, content=["elem text", hm.Sub(), "bpt Tail"]),
      elem,
      (hm.Sub,),
    )
    assert self.backend.get_text(elem) == "elem text"
    for child in self.backend.iter_children(elem):
      assert self.backend.get_tag(child) == "sub"
      assert self.backend.get_tail(child) == "bpt Tail"
