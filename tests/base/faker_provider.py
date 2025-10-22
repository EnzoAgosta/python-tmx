from faker import Faker
from faker.providers import BaseProvider

from python_tmx.base.models import Header, Note, Prop, SegType


class BaseElementsProvider(BaseProvider):
  generator: Faker

  def note(self) -> Note:
    return Note(
      content=self.generator.sentence(self.generator.random_int(5, 20), True),
      lang=self.generator.locale(),
      o_encoding=self.generator.file_extension(),
    )

  def prop(self) -> Prop:
    return Prop(
      content=self.generator.sentence(self.generator.random_int(5, 20), True),
      type=self.generator.word(),
      lang=self.generator.locale(),
      o_encoding=self.generator.file_extension(),
    )

  def header(self) -> Header:
    return Header(
      creationtool=self.generator.word(),
      creationtoolversion=".".join(str(self.generator.random_number(self.generator.random_digit())) for _ in self.generator.random_digit()),
      segtype=self.generator.enum(SegType),
      o_tmf=self.generator.file_extension(),
      adminlang=self.generator.locale(),
      srclang=self.generator.locale(),
      datatype=self.generator.word()
    )
