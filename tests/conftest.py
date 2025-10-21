from pathlib import Path

import pytest

from python_tmx.tmx.models import Tu
from python_tmx.tmx.parse import generate_tus

TEST_DIR = Path(__file__).parent


@pytest.fixture
def sample_basic_tmx() -> Path:
  """Path to a small TMX file used in multiple tests."""
  return TEST_DIR / "fixtures" / "sample_basic.tmx"


@pytest.fixture
def parsed_tus(sample_basic_tmx) -> list[Tu]:
  """Parse the basic TMX and return list of Tu objects."""
  return list(generate_tus(sample_basic_tmx))
