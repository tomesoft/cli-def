# TODO

Roadmap and ideas. These are exploratory and not all items are guaranteed to be implemented.
See [README](README.md) for overview.

## General Concept
- [x] Declarative CLI definition
- [x] Command / subcommand definition
- [x] Positional argument definition
- [x] Optional argument definition
- [x] Flag (boolean) argument definition
- [x] Choice-based argument definition
- [ ] Command template mechanism  
  Allows reusable argument definitions shared across commands.
  - [x] Templates can be defined in the same way as commands  
    (template keys are prefixed with `_`)
- [ ] Introspection  
  Ability to inspect and analyze CLI definitions programmatically

## Parser
- [x] Parse from .toml files

## AST (Abstract Syntax Tree)
### Core Nodes
- [x] CliDef : Root of the CLI definition
- [x] CommandDef : Command / subcommand definition
- [x] ArgumentDef : Argument / option definition

### Extended Definition Vocabulary
- [x] MultDef : Multiplicity normalization
- [ ] Handler definition  
  Defines how a command is executed
- [ ] Base type definitions  
  e.g. "str", "int", ...
- [ ] Specialized type definitions  
  Higher-level abstractions (e.g. PathSpec for file system paths)
- [ ] Constraint definitions  
  e.g. mutually exclusive arguments, required groups, dependencies

## Built-in Runtime Components
- [ ] Validator  
  Validates CLI definitions (structure and semantics)
- [ ] Evaluator  
  Evaluates parsed argv against constraints
- [ ] Dispatcher  
  Dispatches execution to command handlers

## Bindings
- [x] Builder (AST → runtime implementation)
- [ ] Reverser (runtime implementation → AST)

### argparse
- [x] Builder (AST → argparse)
  - [x] ArgparseBuilder

### click
- [x] Builder (AST → click)
  - [x] ClickBuilder

## API
- [ ] Public API design (high-level entry points)
- [ ] Stable interface for parser / builder / dispatcher

## Misc
- [ ] Demo tool (dogfooding CLI)
  - Dump AST structure
  - Switch between predefined CLI profiles:
    - Beginner
    - Advanced
- [ ] Interactive mode support (e.g. integration with prompt_toolkit)
- [ ] Test generator  
  Generate test cases from CLI definitions
- [ ] Code generator  
  Generate CLI code (argparse / click) from definitions