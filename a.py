from src import from_file
from src.converters import to_file

a = from_file("test.tmx")
to_file(a, "new.tmx")
b = from_file("new.tmx")
print(a == b)
