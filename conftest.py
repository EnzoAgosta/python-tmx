import random
import string

import pytest
from faker import Faker

from tests.base.faker_provider import BaseElementsProvider

GLOBAL_SEED: int | str

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

@pytest.fixture(scope="session")
def faker() -> Faker:
    fake = Faker()
    fake.add_provider(BaseElementsProvider)
    return fake
