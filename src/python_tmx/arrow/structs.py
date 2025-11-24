import pyarrow as pa

from python_tmx.base.types import (
  BaseElement,
  Bpt,
  Ept,
  Header,
  Hi,
  It,
  Note,
  Ph,
  Prop,
  Sub,
  Tmx,
  Tu,
  Tuv,
)

PROP_STRUCT = pa.struct(
  fields=(
    pa.field(name="text", type=pa.string(), nullable=False),
    pa.field(name="type", type=pa.string(), nullable=False),
    pa.field(name="lang", type=pa.string(), nullable=True),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
  )
)

NOTE_STRUCT = pa.struct(
  fields=(
    pa.field(name="text", type=pa.string(), nullable=False),
    pa.field(name="lang", type=pa.string(), nullable=True),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
  )
)

TAG_FIELD = pa.field(
  name="tag",
  type=pa.dictionary(index_type=pa.int8(), value_type=pa.string()),
  nullable=False,
)

BPT_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="i", type=pa.int16(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

EPT_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="i", type=pa.int16(), nullable=False),
  )
)

HI_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

IT_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="pos", type=pa.string(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

PH_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
    pa.field(name="assoc", type=pa.string(), nullable=True),
  )
)

SUB_STRUCT = pa.struct(
  fields=(
    TAG_FIELD,
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="type", type=pa.string(), nullable=True),
    pa.field(name="datatype", type=pa.string(), nullable=True),
  )
)


TUV_STRUCT = pa.struct(
  fields=(
    pa.field(name="lang", type=pa.string(), nullable=False),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
    pa.field(name="datatype", type=pa.string(), nullable=True),
    pa.field(name="usagecount", type=pa.int32(), nullable=True),
    pa.field(name="lastusagedate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="creationtool", type=pa.string(), nullable=True),
    pa.field(name="creationtoolversion", type=pa.string(), nullable=True),
    pa.field(name="creationdate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="creationid", type=pa.string(), nullable=True),
    pa.field(name="changedate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="changeid", type=pa.string(), nullable=True),
    pa.field(name="o_tmf", type=pa.string(), nullable=True),
    pa.field(name="props", type=pa.list_(PROP_STRUCT), nullable=False),
    pa.field(name="notes", type=pa.list_(NOTE_STRUCT), nullable=False),
    pa.field(name="content", type=pa.binary(), nullable=False),
  )
)

TU_STRUCT = pa.struct(
  fields=(
    pa.field(name="tuid", type=pa.string(), nullable=True),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
    pa.field(name="datatype", type=pa.string(), nullable=True),
    pa.field(name="usagecount", type=pa.int32(), nullable=True),
    pa.field(name="lastusagedate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="creationtool", type=pa.string(), nullable=True),
    pa.field(name="creationtoolversion", type=pa.string(), nullable=True),
    pa.field(name="creationdate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="creationid", type=pa.string(), nullable=True),
    pa.field(name="changedate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="segtype", type=pa.string(), nullable=True),
    pa.field(name="changeid", type=pa.string(), nullable=True),
    pa.field(name="o_tmf", type=pa.string(), nullable=True),
    pa.field(name="srclang", type=pa.string(), nullable=True),
    pa.field(name="props", type=pa.list_(PROP_STRUCT), nullable=False),
    pa.field(name="notes", type=pa.list_(NOTE_STRUCT), nullable=False),
    pa.field(name="variants", type=pa.list_(TUV_STRUCT), nullable=False),
  )
)

HEADER_STRUCT = pa.struct(
  fields=(
    pa.field(name="creationtool", type=pa.string(), nullable=False),
    pa.field(name="creationtoolversion", type=pa.string(), nullable=False),
    pa.field(name="segtype", type=pa.string(), nullable=False),
    pa.field(name="o_tmf", type=pa.string(), nullable=False),
    pa.field(name="adminlang", type=pa.string(), nullable=False),
    pa.field(name="srclang", type=pa.string(), nullable=False),
    pa.field(name="datatype", type=pa.string(), nullable=False),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
    pa.field(name="creationdate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="creationid", type=pa.string(), nullable=True),
    pa.field(name="changedate", type=pa.timestamp("s", tz="UTC"), nullable=True),
    pa.field(name="changeid", type=pa.string(), nullable=True),
    pa.field(name="props", type=pa.list_(PROP_STRUCT), nullable=False),
    pa.field(name="notes", type=pa.list_(NOTE_STRUCT), nullable=False),
  )
)

TMX_STRUCT = pa.struct(
  fields=(
    pa.field(name="version", type=pa.string(), nullable=False),
    pa.field(name="header", type=HEADER_STRUCT, nullable=True),
    pa.field(name="body", type=pa.list_(TU_STRUCT), nullable=False),
  )
)
TMX_SCHEMA = pa.schema(
  fields=(
    pa.field(name="version", type=pa.string(), nullable=False),
    pa.field(name="header", type=HEADER_STRUCT, nullable=True),
    pa.field(name="body", type=pa.list_(TU_STRUCT), nullable=False),
  )
)

STRUCT_FROM_DATACLASS: dict[type[BaseElement], pa.StructType] = {
  Prop: PROP_STRUCT,
  Note: NOTE_STRUCT,
  Header: HEADER_STRUCT,
  Bpt: BPT_STRUCT,
  Ept: EPT_STRUCT,
  Hi: HI_STRUCT,
  It: IT_STRUCT,
  Ph: PH_STRUCT,
  Sub: SUB_STRUCT,
  Tuv: TUV_STRUCT,
  Tu: TU_STRUCT,
  Tmx: TMX_STRUCT,
}
