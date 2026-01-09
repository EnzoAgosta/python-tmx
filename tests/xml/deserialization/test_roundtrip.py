import pytest
import logging
from hypomnema.xml.serialization.serializer import Serializer
from hypomnema.xml.deserialization.deserializer import Deserializer
from hypomnema.xml.policy import SerializationPolicy, DeserializationPolicy, PolicyValue


def assert_xml_equal(backend, elem1, elem2):
  """
  Recursively compare two XML elements using the backend API.
  """

  tag1 = backend.get_tag(elem1)
  tag2 = backend.get_tag(elem2)
  assert tag1 == tag2, f"Tags mismatch: {tag1} != {tag2}"

  attr1 = backend.get_attribute_map(elem1)
  attr2 = backend.get_attribute_map(elem2)
  assert attr1 == attr2, f"Attributes mismatch for <{tag1}>: {attr1} != {attr2}"

  text1 = backend.get_text(elem1) or ""
  text2 = backend.get_text(elem2) or ""
  assert text1 == text2, f"Text mismatch for <{tag1}>: {text1!r} != {text2!r}"

  tail1 = backend.get_tail(elem1) or ""
  tail2 = backend.get_tail(elem2) or ""
  assert tail1 == tail2, f"Tail mismatch for <{tag1}>: {tail1!r} != {tail2!r}"

  children1 = list(backend.iter_children(elem1))
  children2 = list(backend.iter_children(elem2))

  assert len(children1) == len(children2), (
    f"Children count mismatch for <{tag1}>: {len(children1)} != {len(children2)}"
  )

  for i, (c1, c2) in enumerate(zip(children1, children2)):
    try:
      assert_xml_equal(backend, c1, c2)
    except AssertionError as e:
      raise AssertionError(f"Child {i} mismatch in <{tag1}>") from e


class TestDeserializationRoundTrip:
  @pytest.fixture(autouse=True)
  def setup(self, backend):
    self.backend = backend

    de_policy = DeserializationPolicy()
    de_policy.empty_content = PolicyValue("ignore", logging.DEBUG)

    self.deserializer = Deserializer(backend, policy=de_policy)
    self.serializer = Serializer(backend, policy=SerializationPolicy())

  def create_elem(self, tag, text=None, tail=None, **attrs):
    elem = self.backend.create_element(tag)
    for k, v in attrs.items():
      self.backend.set_attribute(elem, k, v)

    if text is not None:
      self.backend.set_text(elem, text)
    if tail is not None:
      self.backend.set_tail(elem, tail)
    return elem

  def append_child(self, parent, child):
    self.backend.append_child(parent, child)
    return child

  def test_roundtrip_prop(self):
    original = self.create_elem("prop", text="value", type="x-test")

    tmx_obj = self.deserializer.deserialize(original)
    xml_result = self.serializer.serialize(tmx_obj)

    assert_xml_equal(self.backend, original, xml_result)

  def test_roundtrip_tuv_structure(self):
    tuv = self.create_elem("tuv", **{"xml:lang": "en"})
    seg = self.create_elem("seg", text="Hello ")
    ph = self.create_elem("ph", tail=" World", x="1")

    self.append_child(seg, ph)
    self.append_child(tuv, seg)

    tmx_obj = self.deserializer.deserialize(tuv)
    xml_result = self.serializer.serialize(tmx_obj)

    assert_xml_equal(self.backend, tuv, xml_result)

  def test_roundtrip_full_tmx_structure(self):
    tmx = self.create_elem("tmx", version="1.4")

    header = self.create_elem(
      "header",
      creationtool="TOOL",
      creationtoolversion="1.0",
      segtype="sentence",
      **{"o-tmf": "fmt", "adminlang": "en", "srclang": "en", "datatype": "txt"},
    )
    self.append_child(tmx, header)

    body = self.create_elem("body")
    self.append_child(tmx, body)

    tu = self.create_elem("tu", tuid="1")
    self.append_child(body, tu)

    tuv = self.create_elem("tuv", **{"xml:lang": "en"})
    seg = self.create_elem("seg", text="Hello")
    self.append_child(tuv, seg)
    self.append_child(tu, tuv)

    tmx_obj = self.deserializer.deserialize(tmx)
    xml_result = self.serializer.serialize(tmx_obj)

    assert_xml_equal(self.backend, tmx, xml_result)
