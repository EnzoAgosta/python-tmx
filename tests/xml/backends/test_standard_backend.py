from pathlib import Path

from pytest_mock import MockerFixture
import hypomnema as hm
import xml.etree.ElementTree as et


class TestStandardBackend:
  backend = hm.StandardBackend()

  def test_make_elem_returns_etree_element(self, mocker: MockerFixture):
    assert isinstance(self.backend.make_elem("node"), et.Element)

  def test_set_attr_sets_attribute(self, mocker: MockerFixture):
    elem = self.backend.make_elem("node")
    self.backend.set_attr(elem, "a", "1")
    assert elem.attrib["a"] == "1"

  def test_parse_return_root_via_etree_parse(self, tmp_path: Path, mocker: MockerFixture):
    tmp_file = tmp_path / "test.xml"
    tmp_file.write_text("<root/>")

    spy_parse = mocker.spy(et, "parse")
    spy_getroot = mocker.spy(et.ElementTree, "getroot")

    self.backend.parse(tmp_file)

    spy_parse.assert_called_once_with(tmp_file)
    spy_getroot.assert_called_once()

  def test_write_calls_etree(self, tmp_path: Path, mocker: MockerFixture):
    tmp_file = tmp_path / "test.xml"
    root = et.Element("root")

    spy_ElementTree = mocker.spy(et, "ElementTree")

    self.backend.write(root, tmp_file)

    spy_ElementTree.assert_called_once_with(root)

  def test_write_calls_write_with_defaults(self, tmp_path: Path, mocker: MockerFixture):
    tmp_file = tmp_path / "test.xml"
    root = et.Element("root")

    fake_tree = mocker.Mock(spec=et.ElementTree)
    mocker.patch.object(et, "ElementTree", return_value=fake_tree)

    self.backend.write(root, tmp_file)

    fake_tree.write.assert_called_once_with(
      tmp_file,
      "utf-8",
      xml_declaration=True,
      short_empty_elements=False,
    )
