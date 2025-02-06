import unittest
import xml.etree.ElementTree as pyet

from PythonTmx import Note


def correct_elem_python():
  elem = pyet.Element("note")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  return elem


def correct_elem_lxml():
  elem = pyet.Element("note")
  elem.text = "test"
  elem.set("{http://www.w3.org/XML/1998/namespace}lang", "en")
  elem.set("o-encoding", "utf-8")
  return elem


class TestNote(unittest.TestCase):
  def setUp(self):
    self.correct_elem_python = correct_elem_python()
    self.correct_elem_lxml = correct_elem_lxml()

  def test_init(self):
    note = Note(text="test", lang="en", encoding="utf-8")
    self.assertEqual(note.text, "test")
    self.assertEqual(note.lang, "en")
    self.assertEqual(note.encoding, "utf-8")

  def test_empy_init(self):
    with self.assertRaises(TypeError):
      Note()

  def test_minimum_init(self):
    note = Note(text="test")
    self.assertEqual(note.text, "test")
    self.assertIsNone(note.lang)
    self.assertIsNone(note.encoding)

  def test_from_element_python(self):
    note = Note.from_element(self.correct_elem_python)
    self.assertEqual(note.text, "test")
    self.assertEqual(note.lang, "en")
    self.assertEqual(note.encoding, "utf-8")

  def test_from_element_lxml(self):
    note = Note.from_element(self.correct_elem_lxml)
    self.assertEqual(note.text, "test")
    self.assertEqual(note.lang, "en")
    self.assertEqual(note.encoding, "utf-8")

  def test_to_element_python(self):
    note = Note.from_element(self.correct_elem_python)
    note_elem = note.to_element("python")
    self.assertEqual(note_elem.tag, self.correct_elem_python.tag)
    self.assertEqual(note_elem.text, self.correct_elem_python.text)
    self.assertDictEqual(note_elem.attrib, self.correct_elem_python.attrib)

  def test_to_element_lxml(self):
    note = Note.from_element(self.correct_elem_lxml)
    note_elem = note.to_element("lxml")
    self.assertEqual(note_elem.tag, self.correct_elem_lxml.tag)
    self.assertEqual(note_elem.text, self.correct_elem_lxml.text)
    self.assertDictEqual(dict(note_elem.attrib), self.correct_elem_lxml.attrib)
    # lxml _Attrib behaves like a dict but isn't a dict Subclass so casting to dict is needed

  def test_from_element_invalid(self):
    with self.assertRaises(ValueError):
      Note.from_element(pyet.Element("test"))
