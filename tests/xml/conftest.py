from collections.abc import Generator
import logging

from python_tmx.xml.backends.base import XMLBackend
import pytest

from python_tmx.xml.backends.lxml import LxmlBackend
from python_tmx.xml.backends.standard import StandardBackend
from test_lib.backend import StrictBackend


@pytest.fixture(params=["standard", "lxml", "strict"])
def backend(request: pytest.FixtureRequest) -> Generator[XMLBackend, None, None]:
  if request.param == "lxml":
    yield LxmlBackend()
  elif request.param == "standard":
    yield StandardBackend()
  elif request.param == "strict":
    yield StrictBackend()


@pytest.fixture
def test_logger() -> logging.Logger:
  """
  Returns a dedicated logger for testing.
  """
  return logging.getLogger("python_tmx.test")
