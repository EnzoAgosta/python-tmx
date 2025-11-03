import os
import pytest
import string
import random
from faker import Faker

from tests.providers.attribute_provider import ExtraProvider
from tests.providers.base_provider import BaseElementProvider
from tests.providers.xml_provider import XmlElementProvider
import lxml.etree as LET
import xml.etree.ElementTree as ET


def _random_seed() -> str:
  chars = string.ascii_letters + string.digits + string.punctuation
  return "".join(random.choices(chars, k=30))


def pytest_addoption(parser):
  parser.addoption(
    "--faker-seed",
    action="store",
    default=os.getenv("FAKER_SEED", _random_seed()),
    help="Seed for Faker RNG (30-char random ASCII by default).",
  )
  parser.addoption(
    "--max-depth",
    action="store",
    default=os.getenv("MAX_DEPTH", random.randint(1, 3)),
    help="Defines the maximum depth for inline elements.",
  )


def pytest_configure(config):
  seed = config.getoption("--faker-seed")
  config._faker_seed = seed
  max_depth = config.getoption("--max-depth")
  config._max_depth = max_depth


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
  max_depth = getattr(config, "_max_depth", None)
  return f"Faker seed: {seed or '(not initialized)'}", f"Max depth: {max_depth or '(not initialized)'}"


@pytest.fixture(
  scope="class",
  params=[
    pytest.param(LET.Element, id="lxml"),
    pytest.param(ET.Element, id="Stdlib"),
  ],
)
def element_provider(faker_instance, request):
  xml_provider = [p for p in faker_instance.providers if isinstance(p, XmlElementProvider)][0]
  base_provider = [p for p in faker_instance.providers if isinstance(p, BaseElementProvider)][0]
  xml_provider.backend = request.param
  max_depth = int(request.config._max_depth)
  xml_provider.max_depth = max_depth
  base_provider.max_depth = max_depth
  faker_instance.backend = request.param
  yield faker_instance
