from dataclasses import asdict

import pyarrow as pa

from python_tmx.arrows.models import NOTE_STRUCT, PROP_STRUCT, TUV_STRUCT
from python_tmx.tmx.models import Note, Prop, Tuv


def prop_to_struct(prop: Prop) -> pa.StructScalar:
  return pa.scalar(value=asdict(prop), type=PROP_STRUCT)


def note_to_struct(note: Note) -> pa.StructScalar:
  return pa.scalar(value=asdict(note), type=NOTE_STRUCT)


def tuv_to_struct(tuv: Tuv) -> pa.StructScalar:
  return pa.scalar(
    value=tuv._arrow_attributes()
    | {
      "props": pa.array(
        [prop_to_struct(prop) for prop in tuv.props],
        type=PROP_STRUCT,
      ),
      "notes": pa.array(
        [note_to_struct(note) for note in tuv.notes],
        type=NOTE_STRUCT,
      ),
    },
    type=TUV_STRUCT,
  )
