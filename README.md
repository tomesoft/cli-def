# cli-def

A declarative DSL for defining CLI structures with a unified runtime and REPL for `argparse`/`click` backends.

project page:
<https://cli-def.tomesoft.net>

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
  - Runner
  - Dispatcher
  - Entrypoint resolution (`module:function`)
  - Result propagation
- Interactive REPL support
  - including safety eval mode
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

`beginner` profile reads in [beginner.toml](./src/cli_def/resources/demo/beginner.toml)

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

`advanced` profile reads in [advanced.toml](./src/cli_def/resources/demo/advanced.toml)

---

## 🖥 Interactive Mode (REPL)

```bash
cli-def repl --file your_cli.toml
```

```text
yourcli> help
yourcli> command arg1 --option value
```

### safety eval mode

for explanation, run builtin `repl` command

```bash
cli-def repl
```

then for example, run `scan` command in REPL;

```text
cli-def> scan cli_def.script.handlers2
package_name: cli_def.script.handlers2
/cli-def/testA:
    cli_def.script.handlers2:dummyA, desc='late binding testA', late_bindings=True
/cli-def/testB:
    cli_def.script.handlers2:dummyB, desc='late binding testB', late_bindings=True
/cli-def/testC:
    cli_def.script.handlers2:dummyC, desc='late binding testC', late_bindings=True

-> out[0]
```

The las message `-> out[0]` means the result has stored as `out[0]` (like Jupyter).  
Then just enter `>` to enter `safety eval mode`;

```text
cli-def> >
cli-def>eval>> len(_)
3
```

The prompt `eval>>` is stacked, so you can see in `safety eval mode`.  
In eval mode, input string is evaluated as a formula of python syntax,   `_` is an alias to the last result (identical to `out[0]` here);

```text
cli-def>eval>> [k for k in _]
['/cli-def/testA', '/cli-def/testB', '/cli-def/testC']
cli-def>eval>> _["/cli-def/testA"]
[{'description': 'late binding testA',
  'entrypoint': 'cli_def.script.handlers2:dummyA',
  'late_bindings': True,
  'module': 'cli_def.script.handlers2',
  'name': 'dummyA',
  'path': '/cli-def/testA',
  'tags': []}]
cli-def>eval>>  
```

And just return to end `safety eval mode` then back to REPL;

```text
cli-def>
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

```text
module:function
```

---

## 🚀 Quick Example

### Define CLI (TOML)

```toml
# cli_def.toml
[cli] # is fixed root entry
key = "MyCLI"
help = "HELP of my CLI"

[cli.hello] # defines "hello" command
args = [
    {key="name", mult="1", type="str"},
    {key="to_upper", option="--upper", is_flat=true, default=false},
]
# one implementation option, CliRunner dispatches "hello" command to the specific entrypoint if it is specified like below.
# entrypoint = "myapp.handlers:hello"
```

---

### Usecase #1 :  Build CLI and Run it

The first usecase is processing entire CLI pipe line. You can easily add CLI functionaly to your apps.

``` python
from cli_def import CliDefParser
from cli_def.runtime import CliRunner, CliEvent

def main():
    parser = CliDefParser()
    cli_def = parser.parse_from_toml("cli_def.toml")

    runner = CliRunner(cli_def, fallback_handler=my_command_handler)
    result = runner.run()

    return result.exit_code

# one implementation option, handling commands in fallback handler
def my_command_handler(event: CliEvent):
    if event.command.defpath == "/MyCLI/hello":
        name = event.params.get("name")
        text = f"Hello {name}"
        if event.params.get("to_upper"):
            text = text.upper()
        print(text)
```

### Usecase #2 :  Build CLI and go REPL

The second usecase is REPL mode.


``` python
from cli_def import CliDefParser
from cli_def.runtime import CliSession, CliEvent, cli_def_handler

def main():
    parser = CliDefParser()
    cli_def = parser.parse_from_toml("cli_def.toml")

    session = CliSession(cli_def)
    session.repl(prompt="MyCLI> ")

    # you can access to the stored result of the session
    # result = session.result_store.all_data()

    return 0

# another implementation option, handling specific command with early binding function that is marked decorator `cli_def_handler`
@cli_def_handler("/MyCLI/hello")
def do_hello(event: CliEvent):
    name = event.params.get("name")
    text = f"Hello {name}"
    if event.params.get("to_upper"):
        text = text.upper()
    print(text)
```

### Usecase #3 : Build argparse.ArgumentParser

The third usecase is building argparse.ArgumentBuilder from CLI definition TOML instead of handwriting it. And you can easily join your existing code.

```python
from cli_def import CliDefParser
from cli_def.backend.argparse import ArgparseBuilder

parser = CliDefParser()
cli_def = parser.parse_from_toml("cli_def.toml")

builder = ArgparseBuilder()
argparser = builder.build_argparse(cli_def)

# if you'd like to tune the argparser, you can access to specific part using defpath
# part: ArgumentParser = builder.mapping["/MyCLI/hello"]
# part.allow_abbrev = False

args = argparser.parse_args()
if args.command == "hello":
    text = f"Hello {args.name}"
    if args.to_upper:
        text = text.upper()
    print(text)
```

---

## 🧠 Concept

```text
TOML / Model
↓
CliDef (AST)
↓
Builder (argparse / click)
↓
Runtime (CliEvent / Dispatcher)
↓
Executable CLI / REPL
```

---

## 🏗 Architecture

```text
cli_def/
  backend/
    argparse/
    click/
  models/
  ops/
  parsers/
  runtime/
  script/
```

---

## 🔌 Optional Dependencies

```bash
pip install cli-def[click]
```

for developers;

```bash
pip install -e ".[dev]"
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
