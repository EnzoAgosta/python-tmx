from hypomnema.xml.constants import XML_NS
from hypomnema.xml.policy import SerializationPolicy
import logging
from hypomnema.xml.serialization import (
  PropSerializer,
  NoteSerializer,
  HeaderSerializer,
  TuvSerializer,
  TuSerializer,
  TmxSerializer,
  BptSerializer,
  EptSerializer,
  ItSerializer,
  PhSerializer,
  SubSerializer,
  HiSerializer,
)
from typing import Any
from hypomnema.xml.serialization.base import BaseElementSerializer
import pytest
from pytest_mock import MockerFixture
from datetime import datetime, UTC
import hypomnema as hm


SERIALIZERS: tuple[
  tuple[
    type[BaseElementSerializer],  # Handler class
    type[hm.BaseElement],  # Associated Object type
    str,  # XML tag
    dict[str, tuple[str, str, Any]],  # required attrs  {xmlAttr: (helper, Attr name, test value)}
    dict[str, tuple[str, str, Any]],  # required attrs  {xmlAttr: (helper, Attr name, test value)}
    dict[str, int],  # Content handlers {handler: call count}
  ],
  ...,
] = (
  (
    PropSerializer,
    hm.Prop,
    "prop",
    {"type": ("_set_str_attribute", "type", "test_type")},
    {
      f"{XML_NS}lang": ("_set_str_attribute", "lang", "en-us"),
      "o-encoding": ("_set_str_attribute", "o_encoding", "utf-8"),
    },
    {"set_text": 1},
  ),
  (
    NoteSerializer,
    hm.Note,
    "note",
    {},
    {
      f"{XML_NS}lang": ("_set_str_attribute", "lang", "en-us"),
      "o-encoding": ("_set_str_attribute", "o_encoding", "utf-8"),
    },
    {"set_text": 1},
  ),
  (
    HeaderSerializer,
    hm.Header,
    "header",
    {
      "creationtool": ("_set_str_attribute", "creationtool", "tool"),
      "creationtoolversion": ("_set_str_attribute", "creationtoolversion", "1.0"),
      "segtype": ("_set_enum_attribute", "segtype", hm.Segtype.BLOCK),
      "adminlang": ("_set_str_attribute", "adminlang", "en"),
      "srclang": ("_set_str_attribute", "srclang", "en"),
      "datatype": ("_set_str_attribute", "datatype", "xml"),
    },
    {
      "o-tmf": ("_set_str_attribute", "o_tmf", "tmf"),
      "creationdate": ("_set_datetime_attribute", "creationdate", datetime.now(UTC)),
      "creationid": ("_set_str_attribute", "creationid", "user"),
      "changedate": ("_set_datetime_attribute", "changedate", datetime.now(UTC)),
      "changeid": ("_set_str_attribute", "changeid", "editor"),
      "o-encoding": ("_set_str_attribute", "o_encoding", "utf-8"),
    },
    {"_serialize_children": 2},
  ),
  (
    TuvSerializer,
    hm.Tuv,
    "tuv",
    {f"{XML_NS}lang": ("_set_str_attribute", "lang", "en-us")},
    {
      "o-encoding": ("_set_str_attribute", "o_encoding", "utf-8"),
      "datatype": ("_set_str_attribute", "datatype", "xml"),
      "usagecount": ("_set_int_attribute", "usagecount", 42),
      "lastusagedate": ("_set_datetime_attribute", "lastusagedate", datetime.now(UTC)),
      "creationtool": ("_set_str_attribute", "creationtool", "tool"),
      "creationtoolversion": ("_set_str_attribute", "creationtoolversion", "1.0"),
      "creationdate": ("_set_datetime_attribute", "creationdate", datetime.now(UTC)),
      "creationid": ("_set_str_attribute", "creationid", "user"),
      "changedate": ("_set_datetime_attribute", "changedate", datetime.now(UTC)),
      "changeid": ("_set_str_attribute", "changeid", "editor"),
      "o-tmf": ("_set_str_attribute", "o_tmf", "tmf"),
    },
    {"_serialize_children": 2, "_serialize_content_into": 1},
  ),
  (
    TuSerializer,
    hm.Tu,
    "tu",
    {},
    {
      "tuid": ("_set_str_attribute", "tuid", "tu1"),
      "o-encoding": ("_set_str_attribute", "o_encoding", "utf-8"),
      "datatype": ("_set_str_attribute", "datatype", "xml"),
      "usagecount": ("_set_int_attribute", "usagecount", 99),
      "lastusagedate": ("_set_datetime_attribute", "lastusagedate", datetime.now(UTC)),
      "creationtool": ("_set_str_attribute", "creationtool", "tool"),
      "creationtoolversion": ("_set_str_attribute", "creationtoolversion", "1.0"),
      "creationdate": ("_set_datetime_attribute", "creationdate", datetime.now(UTC)),
      "creationid": ("_set_str_attribute", "creationid", "user"),
      "changedate": ("_set_datetime_attribute", "changedate", datetime.now(UTC)),
      "segtype": ("_set_enum_attribute", "segtype", hm.Segtype.BLOCK),
      "changeid": ("_set_str_attribute", "changeid", "editor"),
      "o-tmf": ("_set_str_attribute", "o_tmf", "tmf"),
      "srclang": ("_set_str_attribute", "srclang", "en"),
    },
    {"_serialize_children": 3},
  ),
  (
    TmxSerializer,
    hm.Tmx,
    "tmx",
    {"version": ("_set_str_attribute", "version", "1.4")},
    {},
    {"_serialize_children": 2},
  ),
  (
    BptSerializer,
    hm.Bpt,
    "bpt",
    {"i": ("_set_int_attribute", "i", 1)},
    {"x": ("_set_int_attribute", "x", 99), "type": ("_set_str_attribute", "type", "fmt")},
    {"_serialize_content_into": 1},
  ),
  (
    EptSerializer,
    hm.Ept,
    "ept",
    {"i": ("_set_int_attribute", "i", 1)},
    {},
    {"_serialize_content_into": 1},
  ),
  (
    ItSerializer,
    hm.It,
    "it",
    {"pos": ("_set_enum_attribute", "pos", hm.Pos.BEGIN)},
    {"x": ("_set_int_attribute", "x", 99), "type": ("_set_str_attribute", "type", "fmt")},
    {"_serialize_content_into": 1},
  ),
  (
    PhSerializer,
    hm.Ph,
    "ph",
    {},
    {
      "x": ("_set_int_attribute", "x", 99),
      "assoc": ("_set_enum_attribute", "assoc", hm.Assoc.P),
      "type": ("_set_str_attribute", "type", "fmt"),
    },
    {"_serialize_content_into": 1},
  ),
  (
    SubSerializer,
    hm.Sub,
    "sub",
    {},
    {
      "datatype": ("_set_str_attribute", "datatype", "xml"),
      "type": ("_set_str_attribute", "type", "fmt"),
    },
    {"_serialize_content_into": 1},
  ),
  (
    HiSerializer,
    hm.Hi,
    "hi",
    {},
    {"x": ("_set_int_attribute", "x", 99), "type": ("_set_str_attribute", "type", "bold")},
    {"_serialize_content_into": 1},
  ),
)


class TestAllHandlersSerialize:
  backend: hm.XmlBackend
  logger: logging.Logger
  policy: SerializationPolicy
  mocker: MockerFixture

  @pytest.fixture(autouse=True)
  def _setup(
    self, backend: hm.XmlBackend, test_logger: logging.Logger, mocker: MockerFixture
  ) -> None:
    self.backend = backend
    self.logger = test_logger
    self.policy = SerializationPolicy()
    self.mocker = mocker

  @pytest.mark.parametrize(
    ("handler_cls", "obj_type", "xml_tag", "required", "optional", "content_handlers"), SERIALIZERS
  )
  def test_handler(
    self,
    handler_cls: type[BaseElementSerializer],
    obj_type: type[hm.BaseElement],
    xml_tag: str,
    required: dict[str, tuple[str, str, Any]],
    optional: dict[str, tuple[str, str, Any]],
    content_handlers: dict[str, int],
  ) -> None:
    # Create real handler
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler._emit = self.mocker.Mock()
    # Setup spy objects
    assert_object_type_spy = self.mocker.spy(hm.xml.serialization._handlers, "assert_object_type")
    backend_spy = self.mocker.spy(handler, "backend")
    fake_elem = backend_spy.make_elem.return_value
    _set_datetime_attribute_spy = self.mocker.spy(handler, "_set_datetime_attribute")
    _set_int_attribute_spy = self.mocker.spy(handler, "_set_int_attribute")
    _set_enum_attribute_spy = self.mocker.spy(handler, "_set_enum_attribute")
    _set_str_attribute_spy = self.mocker.spy(handler, "_set_str_attribute")
    _serialize_children_spy = (
      self.mocker.spy(handler, "_serialize_children")
      if hasattr(handler, "_serialize_children")
      else None
    )
    _serialize_content_into_spy = (
      self.mocker.spy(handler, "_serialize_content_into")
      if hasattr(handler, "_serialize_content_into")
      else None
    )
    _set_text_spy = backend_spy.set_text

    spy_map = {
      "_set_datetime_attribute": _set_datetime_attribute_spy,
      "_set_int_attribute": _set_int_attribute_spy,
      "_set_enum_attribute": _set_enum_attribute_spy,
      "_set_str_attribute": _set_str_attribute_spy,
      "_serialize_children": _serialize_children_spy,
      "_serialize_content_into": _serialize_content_into_spy,
      "set_text": _set_text_spy,
    }

    # Create mock object
    mock_obj = self.mocker.Mock(spec=obj_type)

    # Fill in attributes
    for _, (helper, attr_name, val) in required.items():
      setattr(mock_obj, attr_name, val)

    for _, (helper, attr_name, val) in optional.items():
      setattr(mock_obj, attr_name, val)

    # mock content attributes
    mock_obj.text = "text"
    mock_obj.content = ["child"]
    mock_obj.props = []
    mock_obj.notes = []
    mock_obj.variants = []
    mock_obj.body = []
    mock_obj.header = self.mocker.Mock(spec=hm.Header)

    # Actually serialize the element
    handler._serialize(mock_obj)

    # Assert object type was checked
    assert_object_type_spy.assert_called_once_with(
      mock_obj, obj_type, logger=self.logger, policy=self.policy
    )

    # Assert required attributes were set correctly
    for xml_attr, (helper, _, val) in required.items():
      spy = spy_map[helper]
      if helper == "_set_enum_attribute":
        spy.assert_any_call(fake_elem, val, xml_attr, type(val), required=True)
      else:
        spy.assert_any_call(fake_elem, val, xml_attr, required=True)

    # Assert optional attributes were set correctly
    for xml_attr, (helper, _, val) in optional.items():
      spy = spy_map[helper]
      if helper == "_set_enum_attribute":
        spy.assert_any_call(fake_elem, val, xml_attr, type(val), required=False)
      else:
        spy.assert_any_call(fake_elem, val, xml_attr, required=False)

    for content_handler, call_count in content_handlers.items():
      content_handler_spy = spy_map[content_handler]
      assert content_handler_spy.call_count == call_count

  @pytest.mark.parametrize(("handler_cls"), (param[0] for param in SERIALIZERS))
  def test_handler_returns_none_if_incorrect_type(self, handler_cls: type[BaseElementSerializer]):
    handler = handler_cls(self.backend, self.policy, self.logger)
    handler.policy.invalid_object_type.behavior = "ignore"
    out = handler._serialize(1)
    assert out is None
