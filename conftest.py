import random
import string
from pathlib import Path

import lxml.etree as et
import pytest
from faker import Faker

from tests.utils.generate_fake_elements import (
  generate_fake_header_lxml_element,
  generate_fake_note_lxml_elements,
  generate_fake_prop_lxml_elements,
  generate_fake_seg_lxml_element,
  generate_fake_tmx_lxml_element,
  generate_fake_tu_lxml_element,
  generate_fake_tuv_lxml_element,
)

GLOBAL_SEED = "".join(random.choices(string.hexdigits, k=25))
GLOBAL_SEED = int(GLOBAL_SEED, 16) if random.randint(0, 1) else GLOBAL_SEED


@pytest.fixture(scope="session", autouse=True)
def faker_seed():
  return GLOBAL_SEED


def pytest_configure(config):
  global GLOBAL_SEED
  seed = config.getoption("--faker-seed")
  if seed is not None:
    GLOBAL_SEED = seed
  config._faker_seed = GLOBAL_SEED


def pytest_report_header(config):
  return f"seed: {config._faker_seed}\ntype: {config._faker_seed.__class__.__name__}"


def pytest_addoption(parser):
  parser.addoption("--faker-seed", action="store", type=str, help="Set Faker seed")


@pytest.fixture()
def fake_tmx_file(tmp_path, faker: Faker) -> Path:
  tmp_file = tmp_path / "temp.tmx"
  tmp_file.touch()
  tmx = generate_fake_tmx_lxml_element(faker=faker)
  et.ElementTree(tmx).write(tmp_file, encoding="utf-8", xml_declaration=True, pretty_print=True)
  return tmp_file


@pytest.fixture
def full_header_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_header_lxml_element(faker=faker)


@pytest.fixture
def minimal_header_lxml_elem(faker: Faker) -> et._Element:
  header_elem = generate_fake_header_lxml_element(faker=faker)
  del header_elem.attrib["o-encoding"]
  del header_elem.attrib["creationdate"]
  del header_elem.attrib["creationid"]
  del header_elem.attrib["changedate"]
  del header_elem.attrib["changeid"]
  return header_elem


@pytest.fixture
def full_prop_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_prop_lxml_elements(amount=1, faker=faker)[0]


@pytest.fixture
def minimal_prop_lxml_elem(faker: Faker) -> et._Element:
  prop_elem = generate_fake_prop_lxml_elements(amount=1, faker=faker)[0]
  del prop_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  del prop_elem.attrib["o-encoding"]
  return prop_elem


@pytest.fixture
def full_note_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_note_lxml_elements(amount=1, faker=faker)[0]


@pytest.fixture
def minimal_note_lxml_elem(faker: Faker) -> et._Element:
  note_elem = generate_fake_note_lxml_elements(amount=1, faker=faker)[0]
  del note_elem.attrib["{http://www.w3.org/XML/1998/namespace}lang"]
  del note_elem.attrib["o-encoding"]
  return note_elem


@pytest.fixture
def seg_with_children_1_level_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_seg_lxml_element(length=faker.random_int(3, 8), faker=faker)


@pytest.fixture
def text_only_seg_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_seg_lxml_element(length=0, faker=faker)


@pytest.fixture
def full_tuv_lxml_elem(faker: Faker) -> et._Element:
  tuv = generate_fake_tuv_lxml_element(faker=faker)
  tuv.append(generate_fake_seg_lxml_element(length=faker.random_int(3, 9), faker=faker))
  return tuv


@pytest.fixture
def minimal_tuv_lxml_elem(faker: Faker) -> et._Element:
  tuv = generate_fake_tuv_lxml_element(faker=faker)
  for k in tuv.attrib:
    if not k == "{http://www.w3.org/XML/1998/namespace}lang":
      del tuv.attrib[k]
  tuv.append(generate_fake_seg_lxml_element(length=0, faker=faker))
  return tuv


@pytest.fixture
def full_tu_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_tu_lxml_element(faker=faker)


@pytest.fixture
def minimal_tu_lxml_elem(faker: Faker) -> et._Element:
  tu = generate_fake_tu_lxml_element(faker=faker)
  for k in tu.attrib:
    del tu.attrib[k]
  return tu


@pytest.fixture
def tmx_lxml_elem(faker: Faker) -> et._Element:
  return generate_fake_tmx_lxml_element(faker=faker)
