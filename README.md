# cli-def

A declarative DSL for defining CLI structures and generating command-line interfaces for `argparse` and `click`.

---

## ✨ Features

- Define CLI structure declaratively (TOML / Python models)
- Generate CLI implementations for:
  - `argparse` (standard library, no dependencies)
  - `click` (optional dependency)
- Separation of:
  - CLI definition (DSL)
  - Runtime implementation (builders)
- Extensible architecture for additional backends

---

## 📦 Installation

### Core (argparse only)

```bash
pip install cli-def
```

### With Click support
```bash
pip install cli-def[click]
```

# cli-def

A declarative DSL for defining CLI structures and generating command-line interfaces for `argparse` and `click`.

---

## ✨ Features

- Define CLI structure declaratively (TOML / Python models)
- Generate CLI implementations for:
  - `argparse` (standard library, no dependencies)
  - `click` (optional dependency)
- Separation of:
  - CLI definition (DSL)
  - Runtime implementation (builders)
- Extensible architecture for additional backends

---

## 📦 Installation
### Core (argparse only)
```bash
pip install cli-def
```

### With click support
```bash
pip install cli-def[click]
```

---

## 🚀 Quick Example
### Define CLI (TOML)
```toml
[command]
name = "hello"

[[command.arguments]]
name = "--name"
type = "str"
default = "world"
```

### Build CLI (argparse)

```py
from cli_def.parsers import parse
from cli_def.argparse import build

cli_def = parse("cli.toml")
parser = build(cli_def)

args = parser.parse_args()
print(f"Hello {args.name}")
```

---

## 🧠 Concept

cli-def introduces a declarative layer for CLI definition.

Instead of writing CLI logic directly in argparse or click, you:

1. Define structure (commands, arguments, options)

2. Convert it into a runtime implementation
```
TOML / Model
↓
CliDef (AST)
↓
Builder (argparse / click)
↓
Executable CLI
```

---

## 🏗 Architecture

```
cli_def/
  models/ # Core DSL structures
  parsers/ # TOML → models
  argparse/ # argparse builder
  click/ # click builder (optional)
```

## 🔌 Optional Dependencies

Feature: click backend

Install: pip install cli-def[click]

---

## 🧪 Testing

Run all tests:
```bash
pytest
```

Run tests excluding click:
```bash
pytest -m "not click"
```

Run only click-related tests:
```bash
pytest -m click
```

## ⚠️ click Support

The click backend requires the optional dependency:
```bash
pip install cli-def[click]
```

If not installed, importing click-related modules will raise an error.

## 🛠 Roadmap

- [ ] YAML / JSON parser support
- [ ] Rich help output
- [ ] CLI schema validation
- [ ] Plugin system for builders

## 🤝 Contributing

Contributions are welcome!

- Open issues
- Submit pull requests
- Share feedback

## 📄 License

MIT License