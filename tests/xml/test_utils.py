import pytest
from pytest_mock import MockerFixture
from typing import Any, Literal

from hypomnema.base.errors import InvalidTagError, XmlSerializationError
from hypomnema.xml.policy import SerializationPolicy, DeserializationPolicy, PolicyValue
from hypomnema.xml.utils import (
  normalize_tag,
  normalize_encoding,
  prep_tag_set,
  assert_object_type,
  check_tag,
)

import hypomnema as hm


class TestUtils:
  @pytest.fixture
  def logger(self, mocker: MockerFixture) -> Any:
    return mocker.Mock()

  @pytest.mark.parametrize(
    "tag,expected",
    [
      ("tu", "tu"),
      ("{http://www.w3.org/1999/xhtml}span", "span"),
      (b"tuv", "tuv"),
      (bytearray(b"note"), "note"),
    ],
    ids=[
      'tag="tu"',
      'tag="{http://www.w3.org/1999/xhtml}span"',
      'tag=b"tuv"',
      'tag=bytearray(b"note")',
    ],
  )
  def test_normalize_tag_string(self, tag: Any, expected: str) -> None:
    assert normalize_tag(tag) == expected

  def test_normalize_tag_qname_like(self) -> None:
    fake = type("QName", (), {"localname": "header"})()
    assert normalize_tag(fake) == "header"

  def test_normalize_tag_text_attr(self) -> None:
    fake = type("Tag", (), {"text": "{ns}prop"})()
    assert normalize_tag(fake) == "prop"

  def test_normalize_tag_unknown(self) -> None:
    with pytest.raises(TypeError, match=r"Unexpected tag type"):
      normalize_tag(123)

  def test_normalize_encoding_none(self) -> None:
    assert normalize_encoding(None) == "utf-8"

  def test_normalize_encoding_unicode(self) -> None:
    assert normalize_encoding("unicode") == "utf-8"

  @pytest.mark.parametrize(
    "enc",
    ["utf-8", "UTF-8", "UTF_8", "utf_8"],
    ids=["enc=utf-8", "enc=UTF-8", "enc=UTF_8", "enc=utf_8"],
  )
  def test_normalize_encoding_alias(self, enc: str) -> None:
    assert normalize_encoding(enc) == "utf-8"

  def test_normalize_encoding_unknown(self) -> None:
    with pytest.raises(ValueError, match=r"Unknown encoding"):
      normalize_encoding("not-a-codec")

  @pytest.mark.parametrize(
    "inp,expected",
    [
      (None, None),
      ("", None),
      ("tu", {"tu"}),
      (["tu", "tuv"], {"tu", "tuv"}),
      ({"tu", "tuv"}, {"tu", "tuv"}),
      ({"{ns}tu"}, {"tu"}),
    ],
    ids=[
      "inp=None",
      "inp=''",
      "inp='tu'",
      "inp=['tu', 'tuv']",
      "inp={'tu', 'tuv'}",
      "inp={'{ns}tu'}",
    ],
  )
  def test_prep_tag_set(self, inp: Any, expected: set[str] | None) -> None:
    assert prep_tag_set(inp) == expected

  def test_prep_tag_set_bad_type(self) -> None:
    with pytest.raises(TypeError, match=r"Unexpected tag type"):
      prep_tag_set(123)  # type: ignore

  @pytest.mark.parametrize("behaviour", ["raise", "ignore"])
  def test_assert_object_type_policy(
    self, behaviour: Literal["raise", "ignore"], logger: Any, log_level: int
  ) -> None:
    policy = SerializationPolicy()
    policy.invalid_object_type = PolicyValue(behaviour, log_level)

    if behaviour == "raise":
      with pytest.raises(
        XmlSerializationError, match=r"object of type .* is not an instance of .*"
      ):
        assert_object_type("bad", hm.Note, logger=logger, policy=policy)
    else:
      ok = assert_object_type("bad", hm.Note, logger=logger, policy=policy)
      assert ok is False

    logger.log.assert_called_once_with(
      log_level, "object of type %r is not an instance of %r", "str", "Note"
    )

  def test_assert_object_type_ok(self, logger: Any) -> None:
    policy = SerializationPolicy()
    ok = assert_object_type(hm.Note("test"), hm.Note, logger=logger, policy=policy)
    assert ok is True
    logger.log.assert_not_called()

  @pytest.mark.parametrize("behaviour", ["raise", "ignore"])
  def test_check_tag_policy(
    self, behaviour: Literal["raise", "ignore"], logger: Any, log_level: int
  ) -> None:
    policy = DeserializationPolicy()
    policy.invalid_tag = PolicyValue(behaviour, log_level)

    if behaviour == "raise":
      with pytest.raises(InvalidTagError, match=r"Incorrect tag: expected tu, got header"):
        check_tag("header", "tu", logger=logger, policy=policy)
    else:
      check_tag("header", "tu", logger=logger, policy=policy)

    logger.log.assert_called_once_with(
      log_level, "Incorrect tag: expected %s, got %s", "tu", "header"
    )

  def test_check_tag_ok(self, logger: Any) -> None:
    policy = DeserializationPolicy()
    check_tag("tu", "tu", logger=logger, policy=policy)
    logger.log.assert_not_called()
