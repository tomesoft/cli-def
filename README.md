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
[cli]
"key"="MyCLI"
"help"="HELP of my CLI"
"args"= [
    {"key"="your_name", "mult"="1", "type"="str"},
]
```

### Build CLI (argparse)

```py
from cli_def import CliDefParser
from cli_def.argparse import ArgparseBuilder

cli_def_parser = CliDefParser()
cli_def = cli_def_parser.parser_from_toml("cli.toml")
builder = ArgparserBuider()
parser = builder.build_argparser(cli_def)

args = parser.parse_args()
print(f"Hello {args.your_name}")
```

---

## 🧠 Concept

cli-def introduces a declarative layer for CLI definition.

Instead of writing CLI logic directly in `argparse` or `click`, you:

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
  models/   # Core DSL structures
  parsers/  # TOML → models
  argparse/ # argparse builder
  click/    # click builder (optional)
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

## 📌 Roadmap

- See [TODO.md](./TODO.md) for full roadmap and ideas

## 🤝 Contributing

Contributions are welcome!

- Open issues
- Submit pull requests
- Share feedback

## 📄 License

MIT License