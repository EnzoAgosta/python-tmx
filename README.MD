# Hypomnema

[![PyPI version](https://badge.fury.io/py/hypomnema.svg)](https://badge.fury.io/py/hypomnema)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

**The industrial-grade TMX framework for Python.**

**Hypomnema** is a low-level, strictly typed infrastructure library for working with **TMX 1.4b** (Translation Memory eXchange) files in Python.

It is designed as a foundation for building localization, CAT, and NLP tooling — not as an end-user convenience API.  
Version **0.4.x** intentionally exposes only the core primitives and orchestration layers.

> ⚠️ Hypomnema is still in active development. Expect breaking changes without notice.

## 🚀 Why this library?

Most TMX parsers are simple XML wrappers. `Hypomnema` is an infrastructure library offering:

- **🛡️ Policy-Driven Recovery:** Configure exactly how to handle errors (missing segments, extra text, invalid tags)
- **🔌 Backend Agnostic:** Runs on `lxml` for speed or standard `xml.etree` for zero-dependency environments, or even build your own.
- **✨ Type Safe:** Fully annotated with modern Python 3.13+ types. Returns structured Dataclasses, not raw XML nodes.
- **🏗️ Symmetrical:** Deserialize XML to Objects, manipulate them, and Serialize back to XML with roundtrip integrity.

## 📦 Installation

```bash
pip install hypomnema
OR
uv add hypomnema
```

_For maximum performance, install with lxml support and use the LxmlBackend:_

```bash
pip install "hypomnema[lxml]"
OR
uv add hypomnema[lxml]
```

## ⚡ Usage (Low-Level API)

_Note: v0.4.x exposes the core architecture components. Better docs and high-level convenience facades are coming in v0.5._

```python
import hypomnema as hm

# Initialize the Deserializer with a backend
deserializer = hm.Deserializer(backend=hm.StandardBackend())

# Parse the file using the backend and let the deserializer do the work for you
tmx_object = deserializer.deserialize(deserializer.backend.parse("memory.tmx"))

# Inspect and manipulate the object however you want
assert isinstance(tmx_object, hm.Tmx)
print(f"Source Language: {tmx_object.header.srclang}")
print(f"Number of TUs: {len(tmx_object.body)}")
for tu in tmx_object.body:
  if tu.creationdate is None or tu.creationdate.year < 2020:
    del tu

# Initialize the Serializer with a backend (doesn't need to be the same as the Deserializer!)
serializer = hm.Serializer(backend=hm.LxmlBackend())

# Serialize the object back to XML
xml_root = serializer.serialize(tmx_object)

# Write the XML to a file
serializer.backend.write(xml_root, "output.tmx")
```

## Handling Dirty Data (Policies)

Real-world TMX files are often broken. Configure a `DeserializationPolicy` to handle errors when parsing a tmx file
and a `SerializationPolicy` to handle errors when serializing back to XML.

> By default, hypomnema is configured to fail fast and prevent silent data corruption.

You can also configure the logging level for each policy value independently of its behavior and even pass your own logger instance
to every object irrespective of its policy to control logging.

## 🧩 Architecture

The library is built on three decoupled layers:

1.  **Backend Layer:** Abstracts the XML parser. `LxmlBackend` (fast, features) vs `StandardBackend` (portable). You can also build your own by subclassing `XmlBackend` and implementing the required methods.
2.  **Orchestration Layer:** `Serializer` and `Deserializer` classes that manage recursion and dispatch to the correct handler.
3.  **Handler Layer:** Specialized classes (`TuvDeserializer`, `NoteSerializer`) that implement the business logic and policy checks for specific TMX elements.
