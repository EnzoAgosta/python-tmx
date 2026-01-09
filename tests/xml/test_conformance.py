import pytest
from pathlib import Path
import logging
from hypomnema.xml.deserialization.deserializer import Deserializer
from hypomnema.xml.serialization.serializer import Serializer
from hypomnema.xml.policy import DeserializationPolicy, PolicyValue, SerializationPolicy
from hypomnema.base.types import Tmx


DATA_DIR = Path(__file__).parent.parent / "data"


class TestConformance:
  @pytest.fixture(autouse=True)
  def setup(self, backend):
    self.backend = backend

    de_policy = DeserializationPolicy()
    de_policy.empty_content = PolicyValue("ignore", logging.DEBUG)
    self.deserializer = Deserializer(backend, policy=de_policy)
    self.serializer = Serializer(backend, policy=SerializationPolicy())

  def test_parse_minimal(self):
    path = DATA_DIR / "minimal.tmx"
    assert path.exists(), f"Test file not found: {path}"

    root = self.backend.parse(str(path))
    tmx = self.deserializer.deserialize(root)

    assert isinstance(tmx, Tmx)
    assert tmx.header.creationtool == "hypomnema"
    assert len(tmx.body) == 0

  def test_parse_standard(self):
    path = DATA_DIR / "standard.tmx"
    assert path.exists(), f"Test file not found: {path}"

    root = self.backend.parse(str(path))
    tmx = self.deserializer.deserialize(root)

    assert isinstance(tmx, Tmx)
    assert len(tmx.header.notes) == 1
    assert tmx.header.props[0].text == "Computing"

    assert len(tmx.body) == 2
    tu1 = tmx.body[0]
    assert tu1.tuid == "tu1"
    assert len(tu1.variants) == 2

    tu2 = tmx.body[1]
    assert tu2.tuid == "tu2"

    en_variant = next(v for v in tu2.variants if v.lang == "en")
    assert len(en_variant.content) == 5

    from hypomnema.base.types import Bpt, Ept

    assert isinstance(en_variant.content[1], Bpt)
    assert isinstance(en_variant.content[3], Ept)

  def test_roundtrip_standard(self):
    """Read standard.tmx, deserialize, serialize, deserialise again, compare objects."""
    path = DATA_DIR / "standard.tmx"
    root = self.backend.parse(str(path))
    tmx_original = self.deserializer.deserialize(root)

    xml_elem = self.serializer.serialize(tmx_original)

    tmx_roundtrip = self.deserializer.deserialize(xml_elem)

    assert tmx_original == tmx_roundtrip

  def test_parse_namespaces(self):
    path = DATA_DIR / "namespaces.tmx"
    assert path.exists(), f"Test file not found: {path}"

    root = self.backend.parse(str(path))
    tmx = self.deserializer.deserialize(root)

    assert isinstance(tmx, Tmx)

    assert tmx.header.creationtool == "hypomnema"
    assert len(tmx.header.notes) == 1
    assert tmx.header.notes[0].text == "Note with namespace"
    assert tmx.header.notes[0].lang == "en"

    assert len(tmx.body) == 1
    tu = tmx.body[0]
    assert len(tu.variants) == 2
    fr_variant = next(v for v in tu.variants if v.lang == "fr")
    assert fr_variant.content == ["Texte en français"]
