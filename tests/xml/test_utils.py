import xml.etree.ElementTree as et

import lxml.etree as lx
import pytest

import hypomnema as hm


@pytest.mark.parametrize(
  "val,ret",
  [
    ("tag", "tag"),
    (b"tag", "tag"),
    (bytearray(b"tag"), "tag"),
    ("{ns}tag", "tag"),
    (b"{ns}tag", "tag"),
    (bytearray(b"{ns}tag"), "tag"),
    (et.QName("ns", "tag"), "tag"),
    (lx.QName("ns", "tag"), "tag"),
  ],
)
def test_normalize_tag(val, ret):
  assert hm.normalize_tag(val) == ret


def test_normalize_tag_raises_on_unknown_type():
  with pytest.raises(TypeError, match="Unexpected tag type"):
    hm.normalize_tag(1)


@pytest.mark.parametrize(
  "val,ret",
  [
    (None, "utf-8"),
    ("unicode", "utf-8"),
    ("utf-8", "utf-8"),
    ("UTF-8", "utf-8"),
    ("utf8", "utf-8"),
  ],
  ids=["None", "unicode", "utf-8", "UTF-8", "utf8"],
)
def test_normalize_encoding(val, ret):
  assert hm.normalize_encoding(val) == ret


def test_normalize_encoding_raises_on_unknown_type():
  with pytest.raises(ValueError, match="Unknown encoding: error"):
    hm.normalize_encoding("error")


@pytest.mark.parametrize(
  "val,ret",
  [
    (None, None),
    ("tag", {"tag"}),
    (["tag"], {"tag"}),
    (("tag", "tag2"), {"tag", "tag2"}),
    (("{ns}tag", "{ns}tag2"), {"tag", "tag2"}),
  ],
)
def test_prep_tag_set(val, ret):
  assert hm.prep_tag_set(val) == ret


def test_prep_tag_set_raises_on_unknown_type():
  with pytest.raises(TypeError, match="Unexpected tag type"):
    hm.prep_tag_set(1)  # type: ignore
