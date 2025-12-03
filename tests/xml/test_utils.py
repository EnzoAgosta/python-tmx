import pytest
from python_tmx.xml.utils import normalize_tag
import xml.etree.ElementTree as et
import lxml.etree as lx


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
  assert normalize_tag(val) == ret

def test_normalize_tag_raises_on_unknown_type():
  with pytest.raises(TypeError, match="Unexpected tag type"):
    normalize_tag(1)