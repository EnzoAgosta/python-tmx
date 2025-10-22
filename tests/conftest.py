import random

import lxml.etree as et
import pytest
from faker import Faker

from python_tmx.tmx.models import SegType

# Global Faker instance
fake = Faker()


def pytest_configure(config):
  """Generate and apply a random seed for Faker once per test session."""
  seed = (
    "".join(
      random.choices(
        ("a", "b", "c", "d", "e", "f", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"),
        k=random.randint(1, 16),
      )
    ),
  )
  if random.randint(0, 1):
    seed = int(seed, 16)
  Faker.seed(seed)
  fake.seed_instance(seed)

  config._faker_seed = seed


def pytest_report_header(config):
  """Add the Faker seed to pytest's header output."""
  seed = getattr(config, "_faker_seed", None)
  if seed is not None:
    return f"Faker seed: {seed}\ntype: {type(seed).__class__.__name__}"
  return "Faker seed: (not set)"


def generate_fake_props(amount: int, fake: Faker) -> list[et._Element]:
  props: list[et._Element] = []
  for _ in range(amount):
    prop = et.Element(
      "prop",
      attrib={
        "xml:lang": fake.pystr(1, fake.random_int(1, 25)),
        "type": fake.pystr(1, fake.random_int(1, 25)),
        "o-encoding": fake.pystr(1, fake.random_int(1, 25)),
      },
    )
    prop.text = fake.sentence(fake.random_int(5, 20), True)
  return props


def generate_fake_notes(amount: int, fake: Faker) -> list[et._Element]:
  props: list[et._Element] = []
  for _ in range(amount):
    prop = et.Element(
      "note",
      attrib={
        "xml:lang": fake.pystr(1, fake.random_int(1, 25)),
        "o-encoding": fake.pystr(1, fake.random_int(1, 25)),
      },
    )
    prop.text = fake.sentence(fake.random_int(5, 20), True)
  return props


def generate_fake_header(fake: Faker) -> et._Element:
  header = et.Element(
    "header",
    attrib={
      "creationtool": fake.pystr(fake.random_int(1, 25)),
      "creationtoolversion": fake.pystr(fake.random_int(1, 25)),
      "segtype": fake.random_element([v.value for v in SegType]),
      "o-tmf": fake.pystr(fake.random_int(1, 25)),
      "adminlang": fake.pystr(fake.random_int(1, 25)),
      "srclang": fake.pystr(fake.random_int(1, 25)),
      "datatype": fake.pystr(fake.random_int(1, 25)),
      "o-encoding": fake.pystr(fake.random_int(1, 25)),
      "creationdate": fake.date_time().strftime("%Y%m%dT%H%M%SZ"),
      "creationid": fake.pystr(fake.random_int(1, 25)),
      "changedate": fake.date_time().strftime("%Y%m%dT%H%M%SZ"),
      "changeid": fake.pystr(fake.random_int(1, 25)),
    },
  )
  header.extend(generate_fake_props(fake.random_int(1, 10), fake))
  header.extend(generate_fake_notes(fake.random_int(1, 10), fake))
  return header


def generate_fake_tuv(fake: Faker) -> et._Element: ...


def generate_fake_tu(amount: int, fake: Faker) -> list[et._Element]:
  tus: list[et._Element] = []
  for _ in range(amount):
    tu = et.Element(
      "tu",
      attrib={
        "tuid": fake.pystr(fake.random_int(1, 25)),
        "o-encoding": fake.pystr(fake.random_int(1, 25)),
        "datatype": fake.pystr(fake.random_int(1, 25)),
        "usagecount": str(fake.random_int(1, 1000)),
        "lastusagedate": fake.date_time().strftime("%Y%m%dT%H%M%SZ"),
        "creationtool": fake.pystr(fake.random_int(1, 25)),
        "creationtoolversion": fake.pystr(fake.random_int(1, 25)),
        "creationdate": fake.date_time().strftime("%Y%m%dT%H%M%SZ"),
        "creationid": fake.pystr(fake.random_int(1, 25)),
        "changedate": fake.date_time().strftime("%Y%m%dT%H%M%SZ"),
        "segtype": fake.random_element([v.value for v in SegType]),
        "changeid": fake.pystr(fake.random_int(1, 25)),
        "o-tmf": fake.pystr(fake.random_int(1, 25)),
        "srclang": fake.pystr(fake.random_int(1, 25)),
      },
    )
    tuvs = []
  return tus


@pytest.fixture(scope="session")
def sample_tmx(tmp_path, fake: Faker):
  tmp_file = tmp_path / "temp.tmx"
