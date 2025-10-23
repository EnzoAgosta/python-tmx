
import pyarrow as pa

PROP_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.string(), nullable=False),
    pa.field(name="type", type=pa.string(), nullable=False),
    pa.field(name="lang", type=pa.string(), nullable=True),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
  )
)

NOTE_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.string(), nullable=False),
    pa.field(name="lang", type=pa.string(), nullable=True),
    pa.field(name="o_encoding", type=pa.string(), nullable=True),
  )
)

BPT_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="i", type=pa.int16(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

EPT_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="i", type=pa.int16(), nullable=False),
  )
)

HI_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

IT_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="pos", type=pa.string(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
  )
)

PH_STRUCT = pa.struct(
  fields=(
    pa.field(name="content", type=pa.binary(), nullable=False),
    pa.field(name="x", type=pa.int16(), nullable=True),
    pa.field(name="type", type=pa.string(), nullable=True),
    pa.field(name="assoc", type=pa.string(), nullable=True),
  )
)

SUB_STRUCT = pa.struct(
  fields=(
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
    pa.field(name="segment", type=pa.string(), nullable=False),
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
    pa.field(name="header", type=HEADER_STRUCT, nullable=True),
    pa.field(name="tus", type=pa.list_(TU_STRUCT), nullable=False),
  )
)
