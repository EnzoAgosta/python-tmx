import pytest
import string
import random
from faker import Faker

from tests.providers.attribute_provider import ExtraProvider
from tests.providers.base_provider import BaseElementProvider
from tests.providers.xml_provider import XmlElementProvider
import lxml.etree as LET
import xml.etree.ElementTree as ET

FAKER_SEED_KEY = pytest.StashKey[str]()


def _random_seed() -> str:
  chars = string.ascii_letters + string.digits + string.punctuation
  return "".join(random.choices(chars, k=20))


def pytest_addoption(parser):
  parser.addoption(
    "--faker-seed",
    action="store",
    default=None,
    help="Seed for Faker RNG (20-char random ASCII by default).",
  )


def pytest_configure(config):
  cli_seed = config.getoption("--faker-seed")
  seed = cli_seed or _random_seed()
  config._faker_seed = seed


@pytest.fixture(scope="session")
def faker_instance(request):
  seed = getattr(request.config, "_faker_seed", None)
  Faker.seed(seed)
  fake = Faker()
  fake.seed_instance(seed)
  fake.add_provider(ExtraProvider)
  fake.add_provider(BaseElementProvider)
  fake.add_provider(XmlElementProvider)
  return fake


def pytest_report_header(config):
  seed = getattr(config, "_faker_seed", None)
  return f"Faker seed: {seed or '(not initialized)'}"


@pytest.fixture(
  scope="class",
  params=[
    pytest.param(LET.Element, id="lxml"),
    pytest.param(ET.Element, id="Stdlib"),
  ],
  autouse=True,
)
def xml_provider(faker_instance, request):
  provider = [p for p in faker_instance.providers if isinstance(p, XmlElementProvider)][0]
  provider.backend = request.param
  yield faker_instance
