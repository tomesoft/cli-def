# cli-def

A declarative DSL for defining CLI structures with a unified runtime and REPL for argparse/click backends.

project page:
https://cli-def.tomesoft.net

source:
https://github.com/tomesoft/cli-def

## What's new in 0.2.0

- Introduced Resolved model layer
- Added parameter binding (`bind`)
- Added `validate` command
- Improved inheritance (`inherit_from`)
- Added support for relative paths (`../`)
- Improved help and dump output
- Introduced `_early` parsing phase

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
  - Runner
  - Dispatcher
  - Entrypoint resolution (`module:function`)
  - Result propagation
- Interactive REPL support
- CLI chaining (execute one CLI from another)

## 📦 Installation

Core (argparse only)

```bash
pip install cli-def
```

With click support

```bash
pip install cli-def[click]
```

## 🚀 Quick Example

```toml
[cli]
key = "Your CLI"
help = "Help of your CLI"
prompt = "yourcli> "

[cli.echo]
args = [{key="message", mult="+"}]
```

```bash
cli-def run example.toml -- echo hello world

[run] forwarding args: ['echo', 'hello', 'world'], no_ctx_propagate: False
=== fallback handler ===
  PATH: ['Your CLI', 'echo']
  PARAMS: {'message': ['hello', 'world']}
```

## 🚀 Quick Start (Demo)

```bash
cli-def demo beginner
```

beginner profile reads in beginner.toml (see GitHub repository for details)

```text
Type 'help' to list commands, 'exit' to exit
demo[beginner]> echo a b c d
a b c d

-> out[0]
demo[beginner]> greet John --upper
HELLO, JOHN!

-> out[1]
```

Advanced demo:

```bash
cli-def demo advanced
```

See profiles:
https://github.com/tomesoft/cli-def/tree/main/src/cli_def/demo/profiles

## 🖥 Interactive Mode (REPL)

```bash
cli-def repl --file your_cli.toml
yourcli> help
yourcli> command arg1 --option value
```

## 🔁 Run Another CLI (CLI chaining)

```bash
cli-def run example.toml -- command arg1 arg2
```

- `--` separates cli-def arguments from the target CLI arguments
- Remaining arguments are forwarded to the next CLI

## 📚 Documentation

Full documentation and design details are available on GitHub:

https://github.com/tomesoft/cli-def

- DSL specification
- Architecture
- Examples
- Development notes

## 📌 Roadmap

See TODO.md on GitHub:
https://github.com/tomesoft/cli-def/blob/main/TODO.md

## 🤝 Contributing

Contributions are welcome!

## 📄 License

MIT License

