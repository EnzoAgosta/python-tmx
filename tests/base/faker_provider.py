from datetime import UTC

from faker import Faker
from faker.providers import BaseProvider

from python_tmx.base.classes import Header, InlineTag, Note, Prop, SegmentPartType, SegType


class BaseElementsProvider(BaseProvider):
  generator: Faker

  def note(self, /, minimal: bool = False) -> Note:
    return Note(
      content=self.generator.sentence(self.generator.random_int(5, 20), True),
      lang=self.generator.locale() if minimal is False else None,
      o_encoding=self.generator.word() if minimal is False else None,
    )

  def prop(self, /, minimal: bool = False) -> Prop:
    return Prop(
      content=self.generator.sentence(self.generator.random_int(5, 20), True),
      type=self.generator.word(),
      lang=self.generator.locale() if minimal is False else None,
      o_encoding=self.generator.word() if minimal is False else None,
    )

  def header(self, /, minimal: bool = False) -> Header:
    return Header(
      creationtool=self.generator.word(),
      creationtoolversion=".".join(
        str(self.generator.random_number(self.generator.random_digit())) for _ in range(self.generator.random_digit())
      ),
      segtype=self.generator.enum(SegType),
      o_tmf=self.generator.word(),
      adminlang=self.generator.locale(),
      srclang=self.generator.locale(),
      datatype=self.generator.word(),
      o_encoding=self.generator.word() if minimal is False else None,
      creationdate=self.generator.date_time(UTC) if minimal is False else None,
      creationid=self.generator.word() if minimal is False else None,
      changedate=self.generator.date_time(UTC) if minimal is False else None,
      changeid=self.generator.word() if minimal is False else None,
      props=[self.prop() for _ in range(self.generator.random_digit_above_two())] if minimal is False else [],
      notes=[self.note() for _ in range(self.generator.random_digit_above_two())] if minimal is False else [],
    )

  def inline_tag(
    self, /, part_type: SegmentPartType, attributes: dict[str, str] | None = None, nest_level: int = 0
  ) -> InlineTag:
    if nest_level == 0:
      return InlineTag(
        content=self.generator.sentence(
          nb_words=self.generator.random_int(5, 20),
          variable_nb_words=True,
        ),
        type=part_type,
        attributes={**attributes} if attributes is not None else dict(),
      )
    return InlineTag(
      content=[
        self.inline_tag(
          part_type=self.generator.enum(SegmentPartType),
          nest_level=nest_level - 1,
        )
        for _ in range(self.generator.random_digit_above_two())
      ],
      type=part_type,
      attributes={**attributes} if attributes is not None else dict(),
    )
