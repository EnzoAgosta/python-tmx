import builtins
from copy import deepcopy
import importlib
from pathlib import Path
import sys

import pytest
from pytest_mock import MockerFixture

import hypomnema as hm
from strict_backend import StrictBackend


def make_test_xml(tag: str = "root", text: str | None = None, **attrs: str) -> str:
  attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
  opening = f"<{tag} {attr_str}>" if attr_str else f"<{tag}>"
  closing = f"</{tag}>"
  content = text or ""
  return f'<?xml version="1.0" encoding="utf-8"?>\n{opening}{content}{closing}'


def make_nested_xml() -> str:
  return """<?xml version="1.0" encoding="utf-8"?>
<root>
  <parent id="1">
    <child>text1</child>
    <child>text2</child>
  </parent>
  <parent id="2">
    <item>value</item>
  </parent>
</root>"""


def make_malformed_xml() -> str:
  return '<?xml version="1.0"?>\n<root><unclosed>'


def make_namespaced_xml() -> str:
  return """<?xml version="1.0" encoding="utf-8"?>
<root xmlns:ns="http://example.com">
  <ns:element>content</ns:element>
  <regular>data</regular>
</root>"""


def make_mixed_content_xml() -> str:
  return """<?xml version="1.0" encoding="utf-8"?>
<doc>
  <p>Hello <b>world</b> here</p>
  <empty/>
  <tail>text</tail>
</doc>"""


class TestBackend:
  backend: hm.XMLBackend
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def setup(self, backend: hm.XMLBackend, mocker: MockerFixture):
    self.backend = backend
    self.mocker = mocker

  def test_parse_minimal_xml(self, tmp_path: Path):
    xml_file = tmp_path / "minimal.xml"
    xml_file.write_text(make_test_xml("root", "content"))
    root = self.backend.parse(xml_file)
    assert self.backend.get_tag(root) == "root"
    assert self.backend.get_text(root) == "content"

  def test_parse_with_attributes(self, tmp_path: Path):
    xml_file = tmp_path / "attrs.xml"
    xml_file.write_text(make_test_xml("data", attr1="val1", attr2="val2"))
    root = self.backend.parse(xml_file)
    assert self.backend.get_attr(root, "attr1") == "val1"
    assert self.backend.get_attr(root, "attr2") == "val2"

  def test_parse_malformed_xml_raises(self, tmp_path: Path):
    xml_file = tmp_path / "bad.xml"
    xml_file.write_text(make_malformed_xml())
    with pytest.raises(Exception):
      self.backend.parse(xml_file)

  def test_parse_pathlike(self, tmp_path: Path):
    xml_file = tmp_path / "pathlike.xml"
    xml_file.write_text(make_test_xml("root"))
    root = self.backend.parse(xml_file)
    assert self.backend.get_tag(root) == "root"

  def test_write_simple_element(self, tmp_path: Path):
    elem = self.backend.make_elem("test")
    self.backend.set_text(elem, "data")
    out_file = tmp_path / "out.xml"
    self.backend.write(elem, out_file)
    content = out_file.read_text()
    assert "<?xml version='1.0'" in content
    assert "<test>" in content
    assert "data" in content
    assert "</test>" in content

  def test_write_with_encoding(self, tmp_path: Path):
    elem = self.backend.make_elem("root")
    self.backend.set_text(elem, "café")
    out_file = tmp_path / "encoded.xml"
    self.backend.write(elem, out_file, encoding="utf-8")
    content = out_file.read_bytes()
    assert b"caf\xc3\xa9" in content
    root = self.backend.parse(out_file)
    assert self.backend.get_text(root) == "café"

  def test_write_force_short_empty_true(self, tmp_path: Path):
    parent = self.backend.make_elem("parent")
    empty = self.backend.make_elem("empty")
    self.backend.append(parent, empty)
    out_file = tmp_path / "short.xml"
    self.backend.write(parent, out_file)
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 1
    assert self.backend.get_text(children[0]) in (None, "")

  def test_write_force_short_empty_false(self, tmp_path: Path):
    if isinstance(self.backend, hm.StandardBackend):
      pytest.skip("force_short_empty_elements=False is not supported by the StandardBackend")
    parent = self.backend.make_elem("parent")
    empty = self.backend.make_elem("empty")
    self.backend.set_text(empty, None)
    self.backend.append(parent, empty)
    out_file = tmp_path / "long.xml"
    self.backend.write(parent, out_file, force_short_empty_elements=False)  # type: ignore
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 1

  def test_write_roundtrip(self, tmp_path: Path):
    root = self.backend.make_elem("root")
    self.backend.set_attr(root, "id", "123")
    child = self.backend.make_elem("child")
    self.backend.set_text(child, "text")
    self.backend.append(root, child)
    out_file = tmp_path / "roundtrip.xml"
    self.backend.write(root, out_file)
    parsed = self.backend.parse(out_file)
    assert self.backend.get_tag(parsed) == "root"
    assert self.backend.get_attr(parsed, "id") == "123"
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 1
    assert self.backend.get_text(children[0]) == "text"

  def test_iterparse_all_tags(self, tmp_path: Path):
    xml_file = tmp_path / "nested.xml"
    xml_file.write_text(make_nested_xml())
    elements = list(self.backend.iterparse(xml_file))
    tags = [self.backend.get_tag(e) for e in elements]
    assert "child" in tags
    assert "parent" in tags
    assert "root" in tags

  def test_iterparse_filtered_tags_string(self, tmp_path: Path):
    xml_file = tmp_path / "nested.xml"
    xml_file.write_text(make_nested_xml())
    elements = list(self.backend.iterparse(xml_file, tags="child"))
    tags = [self.backend.get_tag(e) for e in elements]
    assert all(t == "child" for t in tags)
    assert len(tags) == 2

  def test_iterparse_filtered_tags_collection(self, tmp_path: Path):
    xml_file = tmp_path / "nested.xml"
    xml_file.write_text(make_nested_xml())
    elements = list(self.backend.iterparse(xml_file, tags=["parent", "item"]))
    tags = [self.backend.get_tag(e) for e in elements]
    assert "parent" in tags
    assert "item" in tags
    assert "child" not in tags

  def test_iterparse_clears_elements(self, tmp_path: Path):
    xml_file = tmp_path / "nested.xml"
    xml_file.write_text(make_nested_xml())
    clear_spy = self.mocker.spy(self.backend, "clear")
    list(self.backend.iterparse(xml_file, tags="child"))
    assert clear_spy.call_count > 0

  def test_iterparse_namespaced_tags(self, tmp_path: Path):
    xml_file = tmp_path / "ns.xml"
    xml_file.write_text(make_namespaced_xml())
    elements = list(self.backend.iterparse(xml_file))
    tags = [self.backend.get_tag(e) for e in elements]
    assert len(tags) >= 2

  def test_iterparse_malformed_raises(self, tmp_path: Path):
    xml_file = tmp_path / "bad.xml"
    xml_file.write_text(make_malformed_xml())
    with pytest.raises(Exception):
      list(self.backend.iterparse(xml_file))

  def test_iterwrite_default_root(self, tmp_path: Path):
    elem1 = self.backend.make_elem("item")
    self.backend.set_text(elem1, "data1")
    elem2 = self.backend.make_elem("item")
    self.backend.set_text(elem2, "data2")
    out_file = tmp_path / "stream.xml"
    self.backend.iterwrite(out_file, [elem1, elem2])
    content = out_file.read_text()
    assert '<?xml version="1.0"' in content
    assert '<tmx version="1.4">' in content
    assert "data1" in content
    assert "data2" in content
    assert "</tmx>" in content

  def test_iterwrite_custom_root(self, tmp_path: Path):
    root = self.backend.make_elem("custom")
    self.backend.set_attr(root, "attr", "value")
    child = self.backend.make_elem("existing")
    self.backend.set_text(child, "pre")
    self.backend.append(root, child)
    elem = self.backend.make_elem("streamed")
    self.backend.set_text(elem, "new")
    out_file = tmp_path / "custom.xml"
    self.backend.iterwrite(out_file, [elem], root_elem=root)
    parsed = self.backend.parse(out_file)
    assert self.backend.get_tag(parsed) == "custom"
    assert self.backend.get_attr(parsed, "attr") == "value"
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 2
    texts = [self.backend.get_text(c) for c in children]
    assert "pre" in texts
    assert "new" in texts

  def test_iterwrite_chunking(self, tmp_path: Path):
    elements = [self.backend.make_elem(f"item{i}") for i in range(10)]
    for i, elem in enumerate(elements):
      self.backend.set_text(elem, f"text{i}")
    out_file = tmp_path / "chunked.xml"
    self.backend.iterwrite(out_file, elements, max_item_per_chunk=3)
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 10

  def test_iterwrite_encoding(self, tmp_path: Path):
    elem = self.backend.make_elem("data")
    self.backend.set_text(elem, "éléphant")
    out_file = tmp_path / "encoded.xml"
    self.backend.iterwrite(out_file, [elem], encoding="utf-8")
    content = out_file.read_bytes()
    assert b'encoding="utf-8"' in content
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert self.backend.get_text(children[0]) == "éléphant"

  def test_iterwrite_file_exists_raises(self, tmp_path: Path):
    out_file = tmp_path / "exists.xml"
    out_file.write_text("exists")
    elem = self.backend.make_elem("item")
    with pytest.raises(FileExistsError):
      self.backend.iterwrite(out_file, [elem])

  def test_iterwrite_invalid_chunk_size_raises(self, tmp_path: Path):
    out_file = tmp_path / "invalid.xml"
    elem = self.backend.make_elem("item")
    with pytest.raises(ValueError):
      self.backend.iterwrite(out_file, [elem], max_item_per_chunk=0)
    with pytest.raises(ValueError):
      self.backend.iterwrite(out_file, [elem], max_item_per_chunk=-1)

  def test_make_elem_basic(self):
    elem = self.backend.make_elem("test")
    assert self.backend.get_tag(elem) == "test"

  def test_set_get_attr(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "key", "value")
    assert self.backend.get_attr(elem, "key") == "value"

  def test_get_attr_default(self):
    elem = self.backend.make_elem("elem")
    assert self.backend.get_attr(elem, "missing") is None
    assert self.backend.get_attr(elem, "missing", "default") == "default"

  def test_set_get_text(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "content")
    assert self.backend.get_text(elem) == "content"

  def test_set_text_none(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "text")
    self.backend.set_text(elem, None)
    assert self.backend.get_text(elem) is None

  def test_set_get_tail(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_tail(elem, "tail_text")
    assert self.backend.get_tail(elem) == "tail_text"

  def test_append_child(self):
    parent = self.backend.make_elem("parent")
    child = self.backend.make_elem("child")
    self.backend.append(parent, child)
    children = list(self.backend.iter_children(parent))
    assert len(children) == 1
    assert self.backend.get_tag(children[0]) == "child"

  def test_iter_children_all(self):
    parent = self.backend.make_elem("parent")
    child1 = self.backend.make_elem("a")
    child2 = self.backend.make_elem("b")
    self.backend.append(parent, child1)
    self.backend.append(parent, child2)
    children = list(self.backend.iter_children(parent))
    assert len(children) == 2

  def test_iter_children_filtered_string(self):
    parent = self.backend.make_elem("parent")
    a = self.backend.make_elem("a")
    b = self.backend.make_elem("b")
    c = self.backend.make_elem("a")
    self.backend.append(parent, a)
    self.backend.append(parent, b)
    self.backend.append(parent, c)
    filtered = list(self.backend.iter_children(parent, tags="a"))
    assert len(filtered) == 2
    assert all(self.backend.get_tag(e) == "a" for e in filtered)

  def test_iter_children_filtered_collection(self):
    parent = self.backend.make_elem("parent")
    a = self.backend.make_elem("a")
    b = self.backend.make_elem("b")
    c = self.backend.make_elem("c")
    self.backend.append(parent, a)
    self.backend.append(parent, b)
    self.backend.append(parent, c)
    filtered = list(self.backend.iter_children(parent, tags=["a", "c"]))
    assert len(filtered) == 2
    tags = {self.backend.get_tag(e) for e in filtered}
    assert tags == {"a", "c"}

  def test_get_tag_normalization(self):
    elem = self.backend.make_elem("tag")
    assert self.backend.get_tag(elem) == "tag"

  def test_clear_element(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "text")
    child = self.backend.make_elem("child")
    self.backend.append(elem, child)
    self.backend.clear(elem)
    assert len(list(self.backend.iter_children(elem))) == 0

  def test_roundtrip_complex_document(self, tmp_path: Path):
    root = self.backend.make_elem("doc")
    self.backend.set_attr(root, "version", "1.0")
    p = self.backend.make_elem("p")
    self.backend.set_text(p, "Hello ")
    b = self.backend.make_elem("b")
    self.backend.set_text(b, "world")
    self.backend.set_tail(b, " here")
    self.backend.append(p, b)
    self.backend.append(root, p)
    empty = self.backend.make_elem("empty")
    self.backend.append(root, empty)
    file1 = tmp_path / "complex.xml"
    self.backend.write(root, file1)
    parsed = self.backend.parse(file1)
    assert self.backend.get_attr(parsed, "version") == "1.0"
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 2
    p_elem = children[0]
    assert self.backend.get_text(p_elem) == "Hello "
    b_elem = list(self.backend.iter_children(p_elem))[0]
    assert self.backend.get_text(b_elem) == "world"
    assert self.backend.get_tail(b_elem) == " here"

  def test_roundtrip_via_iterparse_iterwrite(self, tmp_path: Path):
    if isinstance(self.backend, StrictBackend):
      pytest.skip("Can't use StrictBackend for this test")
    root = self.backend.make_elem("root")
    for i in range(5):
      item = self.backend.make_elem("item")
      self.backend.set_attr(item, "id", str(i))
      self.backend.set_text(item, f"text{i}")
      self.backend.append(root, item)
    file1 = tmp_path / "orig.xml"
    self.backend.write(root, file1)
    # deepcopy since iterparse clears elements after iteration
    items = [deepcopy(e) for e in self.backend.iterparse(file1, tags="item")]
    file2 = tmp_path / "rewritten.xml"
    self.backend.iterwrite(file2, items)
    parsed = self.backend.parse(file2)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 5
    for i, child in enumerate(children):
      assert self.backend.get_attr(child, "id") == str(i)
      assert self.backend.get_text(child) == f"text{i}"

  def test_logging_compatibility_debug(self):
    elem = self.backend.make_elem("test")
    assert self.backend.get_tag(elem) == "test"

  def test_empty_elements_consistency(self, tmp_path: Path):
    parent = self.backend.make_elem("parent")
    empty1 = self.backend.make_elem("empty1")
    empty2 = self.backend.make_elem("empty2")
    self.backend.set_text(empty2, "")
    self.backend.append(parent, empty1)
    self.backend.append(parent, empty2)
    out_file = tmp_path / "empties.xml"
    self.backend.write(parent, out_file)
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 2

  def test_attribute_operations_idempotent(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "key", "val1")
    self.backend.set_attr(elem, "key", "val2")
    assert self.backend.get_attr(elem, "key") == "val2"

  def test_text_operations_idempotent(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_text(elem, "text1")
    self.backend.set_text(elem, "text2")
    assert self.backend.get_text(elem) == "text2"

  def test_tail_operations_idempotent(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_tail(elem, "tail1")
    self.backend.set_tail(elem, "tail2")
    assert self.backend.get_tail(elem) == "tail2"

  def test_iterparse_memory_bounded_large_file(self, tmp_path: Path):
    xml_file = tmp_path / "large.xml"
    with xml_file.open("w") as f:
      f.write('<?xml version="1.0"?>\n<root>\n')
      for i in range(100):
        f.write(f'  <item id="{i}">text{i}</item>\n')
      f.write("</root>")
    clear_spy = self.mocker.spy(self.backend, "clear")
    count = 0
    for elem in self.backend.iterparse(xml_file, tags="item"):
      count += 1
      assert self.backend.get_tag(elem) == "item"
    assert count == 100
    assert clear_spy.call_count >= 100

  def test_iterwrite_empty_elements_iterable(self, tmp_path: Path):
    out_file = tmp_path / "empty_stream.xml"
    self.backend.iterwrite(out_file, [])
    content = out_file.read_text()
    assert "<tmx version=" in content
    assert "</tmx>" in content

  def test_iterwrite_preserves_order(self, tmp_path: Path):
    elements = []
    for i in range(10):
      elem = self.backend.make_elem("item")
      self.backend.set_attr(elem, "order", str(i))
      elements.append(elem)
    out_file = tmp_path / "ordered.xml"
    self.backend.iterwrite(out_file, elements)
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    for i, child in enumerate(children):
      assert self.backend.get_attr(child, "order") == str(i)

  def test_write_pathlike_bytes(self, tmp_path: Path):
    elem = self.backend.make_elem("test")
    out_file = tmp_path / "bytes_path.xml"
    self.backend.write(elem, bytes(out_file))
    assert out_file.exists()

  def test_parse_preserves_structure(self, tmp_path: Path):
    xml_file = tmp_path / "structure.xml"
    xml_file.write_text(make_mixed_content_xml())
    root = self.backend.parse(xml_file)
    assert self.backend.get_tag(root) == "doc"
    children = list(self.backend.iter_children(root))
    assert len(children) >= 2

  def test_iter_children_empty_parent(self):
    parent = self.backend.make_elem("parent")
    children = list(self.backend.iter_children(parent))
    assert len(children) == 0

  def test_get_text_no_text(self):
    elem = self.backend.make_elem("elem")
    assert self.backend.get_text(elem) in (None, "")

  def test_get_tail_no_tail(self):
    elem = self.backend.make_elem("elem")
    assert self.backend.get_tail(elem) is None

  def test_iterparse_empty_tags_collection(self, tmp_path: Path):
    xml_file = tmp_path / "empty_tags.xml"
    xml_file.write_text(make_nested_xml())
    elements = list(self.backend.iterparse(xml_file, tags=[]))
    assert len(elements) > 0

  def test_multiple_attributes(self):
    elem = self.backend.make_elem("elem")
    self.backend.set_attr(elem, "a", "1")
    self.backend.set_attr(elem, "b", "2")
    self.backend.set_attr(elem, "c", "3")
    assert self.backend.get_attr(elem, "a") == "1"
    assert self.backend.get_attr(elem, "b") == "2"
    assert self.backend.get_attr(elem, "c") == "3"

  def test_nested_append(self):
    root = self.backend.make_elem("root")
    level1 = self.backend.make_elem("l1")
    level2 = self.backend.make_elem("l2")
    level3 = self.backend.make_elem("l3")
    self.backend.append(level2, level3)
    self.backend.append(level1, level2)
    self.backend.append(root, level1)
    children_l1 = list(self.backend.iter_children(root))
    assert len(children_l1) == 1
    children_l2 = list(self.backend.iter_children(children_l1[0]))
    assert len(children_l2) == 1
    children_l3 = list(self.backend.iter_children(children_l2[0]))
    assert len(children_l3) == 1

  def test_iterwrite_single_element(self, tmp_path: Path):
    elem = self.backend.make_elem("single")
    self.backend.set_text(elem, "data")
    out_file = tmp_path / "single.xml"
    self.backend.iterwrite(out_file, [elem])
    parsed = self.backend.parse(out_file)
    children = list(self.backend.iter_children(parsed))
    assert len(children) == 1
    assert self.backend.get_text(children[0]) == "data"

  def test_write_then_iterparse_filtered(self, tmp_path: Path):
    root = self.backend.make_elem("root")
    for tag in ["a", "b", "a", "c", "a"]:
      child = self.backend.make_elem(tag)
      self.backend.append(root, child)
    out_file = tmp_path / "filtered.xml"
    self.backend.write(root, out_file)
    elements = list(self.backend.iterparse(out_file, tags="a"))
    assert len(elements) == 3
    assert all(self.backend.get_tag(e) == "a" for e in elements)

  def test_iterwrite_raise_on_malformed_element_by_tostring(self, tmp_path: Path):
    self.mocker.patch(
      "hypomnema.xml.backends.lxml.et.tostring", side_effect=lambda *args, **kwargs: b"malformed"
    )
    self.mocker.patch(
      "hypomnema.xml.backends.standard.et.tostring",
      side_effect=lambda *args, **kwargs: b"malformed",
    )
    out_file = tmp_path / "malformed.xml"
    with pytest.raises(ValueError, match="Cannot find closing tag for root element: malformed"):
      self.backend.iterwrite(out_file, [])

  def test_warns_when_lxml_missing(self, monkeypatch: pytest.MonkeyPatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
      if name == "lxml.etree":
        raise ImportError("blocked for test")
      return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    sys.modules.pop("hypomnema.xml.backends", None)
    sys.modules.pop("hypomnema.xml.backends.lxml", None)

    with pytest.warns(UserWarning, match=r"lxml not installed"):
      importlib.import_module("hypomnema.xml.backends")
