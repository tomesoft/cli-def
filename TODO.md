# TODO

This is a roadmap and idea list for cli-def.  
Some items are experimental and not guaranteed to be implemented.
See [README](README.md) for overview.

---

## ✅ Done

### Core Concept

- Declarative CLI definition
- Command / subcommand structure
- Positional / optional / flag arguments
- Choice parameters
- Command templates (inheritance model)

### Parser

- Parse CLI definitions from TOML

### AST

- CliDef (root node)
- CommandDef (command / subcommand)
- ArgumentDef (argument / option)
- MultDef (multiplicity normalization)

### Runtime

- CliRunner
- CliSession supports REPL
- CliEvent abstraction
- Dispatcher
- Entrypoint (`module:function`) early and late bindings
- Argument normalization based on multiplicity

### Builders

- ArgparseBuilder
- ClickBuilder

### Tooling

- REPL (interactive mode)
- Selectable backend argparse / click
- Demo CLI (beginner / advanced)
- CLI chaining (`run` command)

---

## 🚧 In Progress


---

## 🟡 Next (High Priority)

### Runtime Features

- Evaluator
  - Argument validation
  - Constraint handling
  - Exclusive argument groups

- Dispatcher improvements
  - Middleware / hook system
  - Pre/post dispatch hooks

---

## 🔵 Next (Medium Priority)

### Definition Extensions

- Handler definition abstraction (HandlerDef)
- Base types (str, int, etc.)
- Spec types (e.g. PathSpec)
- Constraint definitions

### Tooling

- Demo improvements
- CLI inspection tools
- AST visualization utilities

---

## 🧪 Later (Exploratory)

### Advanced Features

- Reverse builder
  - argparse → CliDef AST

- Dynamic CLI
  - Runtime AST modification
  - Context-dependent commands

- Interactive Enhancements
  - Prompt Toolkit integration
  - Autocomplete / suggestions

- Code Generation
- Test Generator

---

## 💡 Ideas

- CLI as a runtime platform (not just definition)
- Middleware-style execution model
- Plugin system for extensions
