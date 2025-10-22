from datetime import UTC, datetime

import lxml.etree as et
from faker import Faker

from python_tmx.tmx.models import SegmentPartType, SegType


def generate_fake_prop_lxml_elements(amount: int, faker: Faker) -> list[et._Element]:
  props: list[et._Element] = []
  for _ in range(amount):
    prop = et.Element(
      "prop",
      attrib={
        "{http://www.w3.org/XML/1998/namespace}lang": faker.sentence(faker.random_int(5, 20), True),
        "type": faker.sentence(faker.random_int(5, 20), True),
        "o-encoding": faker.sentence(faker.random_int(5, 20), True),
      },
    )
    prop.text = faker.sentence(faker.random_int(5, 20), True)
    props.append(prop)
  return props


def generate_fake_note_lxml_elements(amount: int, faker: Faker) -> list[et._Element]:
  notes: list[et._Element] = []
  for _ in range(amount):
    note = et.Element(
      "note",
      attrib={
        "{http://www.w3.org/XML/1998/namespace}lang": faker.sentence(faker.random_int(5, 20), True),
        "o-encoding": faker.sentence(faker.random_int(5, 20), True),
      },
    )
    note.text = faker.sentence(faker.random_int(5, 20), True)
    notes.append(note)
  return notes


def generate_fake_header_lxml_element(faker: Faker) -> et._Element:
  header = et.Element(
    "header",
    attrib={
      "creationtool": faker.sentence(faker.random_int(5, 20), True),
      "creationtoolversion": faker.sentence(faker.random_int(5, 20), True),
      "segtype": faker.random_element([v.value for v in SegType]),
      "o-tmf": faker.sentence(faker.random_int(5, 20), True),
      "adminlang": faker.sentence(faker.random_int(5, 20), True),
      "srclang": faker.sentence(faker.random_int(5, 20), True),
      "datatype": faker.sentence(faker.random_int(5, 20), True),
      "o-encoding": faker.sentence(faker.random_int(5, 20), True),
      "creationdate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "creationid": faker.sentence(faker.random_int(5, 20), True),
      "changedate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "changeid": faker.sentence(faker.random_int(5, 20), True),
    },
  )
  header.extend(generate_fake_prop_lxml_elements(faker.random_int(1, 10), faker))
  header.extend(generate_fake_note_lxml_elements(faker.random_int(1, 10), faker))
  return header


def generate_fake_tuv_lxml_element(faker: Faker) -> et._Element:
  tuv = et.Element(
    "tuv",
    attrib={
      "{http://www.w3.org/XML/1998/namespace}lang": faker.sentence(faker.random_int(5, 20), True),
      "o-encoding": faker.sentence(faker.random_int(5, 20), True),
      "datatype": faker.sentence(faker.random_int(5, 20), True),
      "usagecount": str(faker.random_int(1, 1000)),
      "lastusagedate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "creationtool": faker.sentence(faker.random_int(5, 20), True),
      "creationtoolversion": faker.sentence(faker.random_int(5, 20), True),
      "creationdate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "creationid": faker.sentence(faker.random_int(5, 20), True),
      "changedate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "changeid": faker.sentence(faker.random_int(5, 20), True),
      "o-tmf": faker.sentence(faker.random_int(5, 20), True),
    },
  )
  tuv.extend(generate_fake_note_lxml_elements(faker.random_int(1, 5), faker=faker))
  tuv.extend(generate_fake_prop_lxml_elements(faker.random_int(1, 5), faker=faker))
  return tuv


def generate_fake_seg_lxml_element(length: int, faker: Faker) -> et._Element:
  seg = et.Element("seg")
  seg.text = faker.sentence(faker.random_int(5, 15), variable_nb_words=True)
  no_string = [e for e in SegmentPartType if e is not SegmentPartType.STRING]
  for _ in range(length):
    child_tag = faker.random_element(no_string).value
    child_attrib = {"i": str(faker.random_int(1, 15))} if faker.random_int(0, 1) else {}
    child = et.Element(child_tag, attrib=child_attrib)
    child.text = faker.sentence(faker.random_int(5, 20), True)
    child.tail = faker.sentence(faker.random_int(5, 20), True)
    seg.append(child)
  return seg


def generate_fake_tu_lxml_element(faker: Faker) -> et._Element:
  tu = et.Element(
    "tu",
    attrib={
      "tuid": faker.sentence(faker.random_int(5, 20), True),
      "o-encoding": faker.sentence(faker.random_int(5, 20), True),
      "datatype": faker.sentence(faker.random_int(5, 20), True),
      "usagecount": str(faker.random_int(1, 1000)),
      "lastusagedate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "creationtool": faker.sentence(faker.random_int(5, 20), True),
      "creationtoolversion": faker.sentence(faker.random_int(5, 20), True),
      "creationdate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "creationid": faker.sentence(faker.random_int(5, 20), True),
      "changedate": faker.date_time(tzinfo=UTC, end_datetime=datetime(2025, 10, 25, 12, 12, 12, 12, UTC)).strftime(
        "%Y%m%dT%H%M%SZ"
      ),
      "segtype": faker.random_element([v.value for v in SegType]),
      "changeid": faker.sentence(faker.random_int(5, 20), True),
      "o-tmf": faker.sentence(faker.random_int(5, 20), True),
      "srclang": faker.sentence(faker.random_int(5, 20), True),
    },
  )
  tu.extend(generate_fake_note_lxml_elements(faker.random_int(1, 7), faker=faker))
  tu.extend(generate_fake_prop_lxml_elements(faker.random_int(1, 7), faker=faker))
  source, target = generate_fake_tuv_lxml_element(faker=faker), generate_fake_tuv_lxml_element(faker=faker)
  seg_length = faker.random_int(1, 7)
  source.append(generate_fake_seg_lxml_element(length=seg_length, faker=faker))
  target.append(generate_fake_seg_lxml_element(length=seg_length, faker=faker))
  tu.append(source)
  tu.append(target)
  return tu


def generate_fake_tmx_lxml_element(faker: Faker) -> et._Element:
  tmx = et.Element("tmx", attrib={"version": "1.4"})
  tmx.append(generate_fake_header_lxml_element(faker=faker))
  body = et.Element("body")
  body.extend([generate_fake_tu_lxml_element(faker=faker) for _ in range(faker.random_int(25, 200))])
  tmx.append(body)
  return tmx
