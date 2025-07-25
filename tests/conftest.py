# type: ignore
# We're intentionally creating broken stuff for testing
# so we can test the error handling, so no type checking
# possible here.
from typing import Any
from xml.etree.ElementTree import Element as StdElement

import pytest
from lxml.etree import Element as LxmlElement

from PythonTmx.core import AnyElementFactory, AnyXmlElement


@pytest.fixture(params=[LxmlElement, StdElement], scope="session")
def ElementFactory(request: Any) -> AnyElementFactory[..., AnyXmlElement]:
  return request.param


@pytest.fixture(scope="session")
def FakeAndBrokenElement() -> AnyElementFactory[..., AnyXmlElement]:
  class FakeAndBrokenElement:
    def __init__(self, **kwargs) -> None:
      for k, v in kwargs.items():
        setattr(self, k, v)

    def __iter__(self):
      yield from []

    def append(self, element: AnyXmlElement) -> None: ...

  return FakeAndBrokenElement
