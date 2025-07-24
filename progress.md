# PythonTmx Roadmap

A living roadmap for the v0.4+ rewrite of PythonTmx

---

## ✅ Core Architecture

- [x] Robust error hierarchy
- [x] Strongly-typed element protocols and base classes
- [x] Pluggable, library-agnostic parser base
- [x] Utilities for validation, file checks, and error raising

## 🚧 TMX Element Implementations

- Structural Elements
  - [x] `Prop`
  - [ ] `Note`
  - [ ] `Map`
  - [ ] `Ude`
  - [ ] `Header`
  - [ ] `Tu`
  - [ ] `Tuv`
  - [ ] `Segment`
-  Inline Elements 
  - [ ] `Bpt`
  - [ ] `Ept`
  - [ ] `Ph`
  - [ ] `Hi`
  - [ ] `It`
  - [ ] `Ut`

## 🚧 Parser Backends

- [x] `LazyLxmlParser`
- [ ] `LxmlParser` (non-lazy, loads full XML tree)
- [ ] `LazyStandardParser` (std lib, lazy)
- [ ] `StandardParser` (std lib, non-lazy)
## 🚧 Testing

- [x] Test structure and pytest setup
- [x] Full Prop element test suite (happy/error paths)
- [ ] Test coverage for each new element
- [ ] Test parser backends (basic + edge cases)
- [ ] Error-path, malformed XML, and roundtrip tests
- [ ] Property-based/Hypothesis fuzzing (optional, local-only)

## 🚧 Documentation

- [x] Google style docstrings for core classes
- [ ] Docstrings for all element and parser classes
- [ ] Sphinx (or MkDocs) config and basic API docs
- [ ] Contributor guide, usage examples, and FAQ

## 🚧 Scripts & Demos

- [ ] CLI for validating and pretty-printing TMX files
- [ ] Example: convert between XML backends
- [ ] Example: TMX roundtrip/merge
- [ ] Showcase scripts for localization workflows

## 🏁 Release/Community

- [ ] v0.4 alpha release
- [ ] Migration guide from old version
- [ ] Gather feedback, iterate, and roadmap v1.0

---

**Legend:**  
- ✅ = Done  
- 🚧 = In progress / Next up  
- 🏁 = Release/announce