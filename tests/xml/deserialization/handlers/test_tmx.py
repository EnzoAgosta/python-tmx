import logging
from unittest.mock import Mock

import pytest
from python_tmx.base.errors import AttributeDeserializationError, XmlDeserializationError
from python_tmx.base.types import Header, Segtype, Tmx, Tu
from python_tmx.xml.backends.base import XMLBackend
from python_tmx.xml.deserialization._handlers import TmxDeserializer
from python_tmx.xml.policy import DeserializationPolicy


class TestTmxDeserializer[T_XmlElement]:
  handler: TmxDeserializer
  backend: XMLBackend[T_XmlElement]
  logger: logging.Logger
  policy: DeserializationPolicy

  @pytest.fixture(autouse=True)
  def setup_method_fixture(self, backend: XMLBackend[T_XmlElement], test_logger: logging.Logger):
    self.backend = backend
    self.logger = test_logger
    self.policy = DeserializationPolicy()

    self.handler = TmxDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tmx_elem(
    self,
    tag: str = "tmx",
    version: str | None = "1.4",
    header: int = 1,
    tus: int = 1,
  ) -> T_XmlElement:
    elem = self.backend.make_elem(tag)
    if version:
      self.backend.set_attr(elem, "version", version)
    if header is not None:
      for _ in range(header):
        self.backend.append(elem, self.backend.make_elem("header"))
    body = self.backend.make_elem("body")
    if tus is not None:
      for _ in range(tus):
        self.backend.append(body, self.backend.make_elem("tu"))
    self.backend.append(elem, body)
    return elem

  def test_valid_basic_usage(self, caplog: pytest.LogCaptureFixture):
    mock_header = Header(
      creationtool="t",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="t",
      adminlang="e",
      srclang="e",
      datatype="t",
    )
    mock_tu = Tu(tuid="1")

    def side_effect(child):
      tag = self.backend.get_tag(child)
      if tag == "header":
        return mock_header
      if tag == "tu":
        return mock_tu
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem()
    tmx = self.handler._deserialize(elem)

    assert tmx.version == "1.4"
    assert isinstance(tmx.header, Header)
    assert len(tmx.body) == 1
    assert isinstance(tmx.body[0], Tu)

    assert mock_emit.call_count == 2
    mock_emit.assert_any_call(self.backend.find(elem, "header"))
    body = self.backend.find(elem, "body")
    assert body is not None
    for i in self.backend.iter_children(body):
      mock_emit.assert_any_call(i)

  def test_missing_version_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(version=None)

    self.policy.required_attribute_missing.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.required_attribute_missing.log_level = log_level

    with pytest.raises(AttributeDeserializationError, match="Missing required attribute 'version' on element <tmx>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Missing required attribute 'version' on element <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_missing_version_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(version=None)

    self.policy.required_attribute_missing.behavior = "ignore"
    self.policy.required_attribute_missing.log_level = log_level

    tmx = self.handler._deserialize(elem)
    assert isinstance(tmx, Tmx)
    assert tmx.version is None

    expected_log = (self.logger.name, log_level, "Missing required attribute 'version' on element <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_headers_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=2)

    self.policy.multiple_headers.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.multiple_headers.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Multiple <header> elements in <tmx>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_headers_keep_first(self, caplog: pytest.LogCaptureFixture, log_level: int):
    header1 = Header(
      creationtool="H1",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="H1",
      adminlang="H1",
      srclang="H1",
      datatype="H1",
    )
    header2 = Header(
      creationtool="H2",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="H2",
      adminlang="H2",
      srclang="H2",
      datatype="H2",
    )

    iter_mock = iter([header1, header2])

    def side_effect(child):
      tag = self.backend.get_tag(child)
      if tag == "header":
        return next(iter_mock)
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem(header=2)

    self.policy.multiple_headers.behavior = "keep_first"
    self.policy.multiple_headers.log_level = log_level

    tmx = self.handler._deserialize(elem)

    assert tmx.header == header1

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_multiple_headers_keep_last(self, caplog: pytest.LogCaptureFixture, log_level: int):
    header1 = Header(
      creationtool="H1",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="H1",
      adminlang="H1",
      srclang="H1",
      datatype="H1",
    )
    header2 = Header(
      creationtool="H2",
      creationtoolversion="1",
      segtype=Segtype.BLOCK,
      o_tmf="H2",
      adminlang="H2",
      srclang="H2",
      datatype="H2",
    )

    iter_mock = iter([header1, header2])

    def side_effect(child):
      tag = self.backend.get_tag(child)
      if tag == "header":
        return next(iter_mock)
      return None

    mock_emit = Mock(side_effect=side_effect)
    self.handler._set_emit(mock_emit)

    elem = self.make_tmx_elem(header=2)

    self.policy.multiple_headers.behavior = "keep_last"
    self.policy.multiple_headers.log_level = log_level

    tmx = self.handler._deserialize(elem)

    assert tmx.header == header2

    expected_log = (self.logger.name, log_level, "Multiple <header> elements in <tmx>")
    assert caplog.record_tuples == [expected_log]
  
  def test_missing_header_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=0)

    self.policy.missing_header.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.missing_header.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Element <tmx> is missing a <header> child element."):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Element <tmx> is missing a <header> child element.")
    assert caplog.record_tuples == [expected_log]
  
  def test_missing_header_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem(header=0)

    self.policy.missing_header.behavior = "ignore"
    self.policy.missing_header.log_level = log_level

    tmx = self.handler._deserialize(elem)
    assert isinstance(tmx, Tmx)

    expected_log = (self.logger.name, log_level, "Element <tmx> is missing a <header> child element.")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_raise(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "raise"  # Default but setting it explicitly for testing purposes
    self.policy.invalid_child_element.log_level = log_level

    with pytest.raises(XmlDeserializationError, match="Invalid child element <wrong> in <tmx>"):
      self.handler._deserialize(elem)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tmx>")
    assert caplog.record_tuples == [expected_log]

  def test_invalid_child_element_ignore(self, caplog: pytest.LogCaptureFixture, log_level: int):
    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("wrong"))

    self.policy.invalid_child_element.behavior = "ignore"
    self.policy.invalid_child_element.log_level = log_level

    tmx = self.handler._deserialize(elem)
    assert isinstance(tmx, Tmx)

    expected_log = (self.logger.name, log_level, "Invalid child element <wrong> in <tmx>")
    assert caplog.record_tuples == [expected_log]