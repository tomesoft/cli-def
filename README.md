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
- Built-in runtime system:
  - Event model (`CliEvent`)
  - Dispatcher
  - Entrypoint resolution (`module:function`)
- Interactive REPL support
- CLI chaining (execute one CLI from another)

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

## 🚀 Quick Start (Demo)

Try the interactive demo:

```bash
cli-def demo beginner
```

```
Type 'help' to list commands, 'exit' to exit

demo[beginner]> greet John
Hello, John!
```

Advanced demo:

```bash
cli-def demo advanced
```

---

## 🖥 Interactive Mode (REPL)

```bash
cli-def repl --file your_cli.toml
```

```
yourcli> help
yourcli> command arg1 --option value
```

---

## 🔁 Run Another CLI (CLI chaining)

```bash
cli-def run example.toml -- command arg1 arg2
```

- `--` separates cli-def arguments from the target CLI arguments
- Remaining arguments are forwarded to the next CLI

---

## 🧩 Entrypoint

```toml
[cli.run]
entrypoint = "myapp.handlers:run"
```

Resolved as:

```
module:function
```

---

## 🚀 Quick Example

### Define CLI (TOML)

```toml
[cli]
key = "MyCLI"
help = "HELP of my CLI"

[cli.hello]
args = [
    {key="name", mult="1", type="str"}
]
```

---

### Build CLI (argparse)

```python
from cli_def import CliDefParser
from cli_def.argparse import ArgparseBuilder

parser = CliDefParser()
cli_def = parser.parse_from_toml("cli.toml")

builder = ArgparseBuilder()
argparser = builder.build_argparse(cli_def)

args = argparser.parse_args()
print(f"Hello {args.name}")
```

---

## 🧠 Concept

```
TOML / Model
↓
CliDef (AST)
↓
Builder (argparse / click)
↓
Runtime (CliEvent / Dispatcher)
↓
Executable CLI
```

---

## 🏗 Architecture

```
cli_def/
  models/
  parsers/
  argparse/
  click/
  runtime/
```

---

## 🔌 Optional Dependencies

```bash
pip install cli-def[click]
```

---

## 🧪 Testing

```bash
pytest
```

```bash
pytest -m "not click"
```

```bash
pytest -m click
```

---

## 📌 Roadmap

- See [TODO.md](./TODO.md)

---

## 🤝 Contributing

Contributions are welcome!

---

## 📄 License

MIT License