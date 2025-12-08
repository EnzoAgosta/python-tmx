import logging

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm


class TestTmxDeserializer[T]:
  handler: hm.TmxDeserializer
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
    self.handler = hm.TmxDeserializer(backend=self.backend, policy=self.policy, logger=self.logger)
    self.handler._set_emit(lambda x: None)

  def make_tmx_elem(self) -> T:
    elem = self.backend.make_elem("tmx")
    self.backend.set_attr(elem, "version", "1.4b")
    header = self.backend.make_elem("header")
    self.backend.set_attr(header, "creationtool", "pytest")
    self.backend.set_attr(header, "creationtoolversion", "0.0.1")
    self.backend.set_attr(header, "segtype", "block")
    self.backend.set_attr(header, "o-tmf", "tmx")
    self.backend.set_attr(header, "adminlang", "en")
    self.backend.set_attr(header, "srclang", "en")
    self.backend.set_attr(header, "datatype", "text")
    self.backend.append(elem, header)
    body = self.backend.make_elem("body")
    tu = self.backend.make_elem("tu")
    self.backend.append(body, tu)
    self.backend.append(elem, body)
    return elem

  def test_returns_Tmx(self):
    elem = self.make_tmx_elem()
    tmx = self.handler._deserialize(elem)
    assert isinstance(tmx, hm.Tmx)

  def test_calls_check_tag(self):
    spy_check_tag = self.mocker.spy(self.handler, "_check_tag")
    tmx = self.make_tmx_elem()

    self.handler._deserialize(tmx)

    spy_check_tag.assert_called_once_with(tmx, "tmx")

  def test_calls_parse_attribute_correctly(self):
    spy_parse_attributes = self.mocker.spy(self.handler, "_parse_attribute")
    tmx = self.make_tmx_elem()
    self.handler._deserialize(tmx)

    spy_parse_attributes.assert_called_once_with(tmx, "version", True)

  def test_calls_emit_on_header_tu_only(self):
    spy_emit = self.mocker.spy(self.handler, "emit")
    elem = self.make_tmx_elem()
    self.handler._deserialize(elem)

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(elem):
      if self.backend.get_tag(i) == "header":
        spy_emit.assert_any_call(i)
      else:
        for j in self.backend.iter_children(i):
          spy_emit.assert_any_call(j)

  def test_appends_if_emit_does_not_return_none(self):
    self.handler._set_emit(
      lambda x: hm.Header(
        creationtool="pytest",
        creationtoolversion="0.0.1",
        segtype=hm.Segtype.BLOCK,
        o_tmf="tmx",
        adminlang="en",
        srclang="en",
        datatype="text",
      )
      if self.backend.get_tag(x) == "header"
      else hm.Tu()
      if self.backend.get_tag(x) == "tu"
      else None
    )
    spy_emit = self.mocker.spy(self.handler, "emit")
    elem = self.make_tmx_elem()

    tmx = self.handler._deserialize(elem)

    assert tmx.header == hm.Header(
      creationtool="pytest",
      creationtoolversion="0.0.1",
      segtype=hm.Segtype.BLOCK,
      o_tmf="tmx",
      adminlang="en",
      srclang="en",
      datatype="text",
    )
    assert tmx.body == [hm.Tu()]

    assert spy_emit.call_count == 2
    for i in self.backend.iter_children(elem, ("prop", "note")):
      spy_emit.assert_any_call(i)

  def test_does_not_append_if_emit_returns_none(self):
    elem = self.make_tmx_elem()
    tmx = self.handler._deserialize(elem)

    assert tmx.header is None
    assert tmx.body == []

  def test_raise_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "raise"

    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tmx>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_invalid_child(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.invalid_child_element.log_level = log_level
    self.policy.invalid_child_element.behavior = "ignore"

    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("invalid"))

    self.handler._deserialize(elem)

    log_message = "Invalid child element <invalid> in <tmx>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "raise"

    elem = self.make_tmx_elem()
    self.backend.set_text(elem, "foo")

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <tmx> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_text_is_not_none(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.extra_text.log_level = log_level
    self.policy.extra_text.behavior = "ignore"

    elem = self.make_tmx_elem()
    self.backend.set_text(elem, "foo")

    self.handler._deserialize(elem)

    log_message = "Element <tmx> has extra text content 'foo'"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_raise_if_multiple_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.multiple_headers.log_level = log_level
    self.policy.multiple_headers.behavior = "raise"

    elem = self.make_tmx_elem()
    self.backend.append(elem, self.backend.make_elem("header"))

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Multiple <header> elements in <tmx>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_keep_first_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    def test_emit(x: T) -> hm.Header | None:
      if self.backend.get_tag(x) == "header":
        if self.backend.get_attr(x, "creationtool") == "pytest":
          return hm.Header(
            creationtool="pytest",
            creationtoolversion="0.0.1",
            segtype=hm.Segtype.BLOCK,
            o_tmf="tmx",
            adminlang="en",
            srclang="en",
            datatype="text",
          )
        else:
          return None
      else:
        return None

    self.handler._set_emit(test_emit)
    self.policy.multiple_headers.log_level = log_level
    self.policy.multiple_headers.behavior = "keep_first"

    elem = self.make_tmx_elem()
    header2 = self.backend.make_elem("header")
    self.backend.append(elem, header2)

    tmx = self.handler._deserialize(elem)

    assert tmx.header == hm.Header(
      creationtool="pytest",
      creationtoolversion="0.0.1",
      segtype=hm.Segtype.BLOCK,
      o_tmf="tmx",
      adminlang="en",
      srclang="en",
      datatype="text",
    )

    log_message = "Multiple <header> elements in <tmx>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_keep_last_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    def test_emit(x: T) -> hm.Header | None:
      if self.backend.get_tag(x) == "header":
        if self.backend.get_attr(x, "creationtool") == "pytest2":
          return hm.Header(
            creationtool="pytest",
            creationtoolversion="0.0.1",
            segtype=hm.Segtype.BLOCK,
            o_tmf="tmx",
            adminlang="en",
            srclang="en",
            datatype="text",
          )
        else:
          return None
      else:
        return None

    self.handler._set_emit(test_emit)
    self.policy.multiple_headers.log_level = log_level
    self.policy.multiple_headers.behavior = "keep_last"

    elem = self.make_tmx_elem()
    header2 = self.backend.make_elem("header")
    self.backend.set_attr(header2, "creationtool", "pytest2")
    self.backend.append(elem, header2)

    tmx = self.handler._deserialize(elem)
    assert tmx.header == hm.Header(
      creationtool="pytest",
      creationtoolversion="0.0.1",
      segtype=hm.Segtype.BLOCK,
      o_tmf="tmx",
      adminlang="en",
      srclang="en",
      datatype="text",
    )

    log_message = "Multiple <header> elements in <tmx>"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_raise_if_no_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.missing_header.log_level = log_level
    self.policy.missing_header.behavior = "raise"

    elem = self.backend.make_elem("tmx")
    self.backend.set_attr(elem, "version", "1.4b")
    body = self.backend.make_elem("body")
    tu = self.backend.make_elem("tu")
    self.backend.append(body, tu)
    self.backend.append(elem, body)

    with pytest.raises(hm.XmlDeserializationError):
      self.handler._deserialize(elem)

    log_message = "Element <tmx> is missing a <header> child element"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]

  def test_ignore_if_no_header(self, caplog: pytest.LogCaptureFixture, log_level: int):
    self.policy.missing_header.log_level = log_level
    self.policy.missing_header.behavior = "ignore"

    elem = self.backend.make_elem("tmx")
    self.backend.set_attr(elem, "version", "1.4b")
    body = self.backend.make_elem("body")
    tu = self.backend.make_elem("tu")
    self.backend.append(body, tu)
    self.backend.append(elem, body)

    tmx = self.handler._deserialize(elem)
    assert tmx.header is None

    log_message = "Element <tmx> is missing a <header> child element"
    expected_log = (self.logger.name, log_level, log_message)

    assert caplog.record_tuples == [expected_log]
