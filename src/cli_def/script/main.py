# cli_def/script/main.py
import argparse

from ..parsers import CliDefParser
from ..models import CliDef
from ..argparse import ArgparseBuilder

CLI_DEF_TOML_TEXT="""
title = "CLI definition"
[cli]
"key"="MyCLI"
"help"="Help of MyCLI"

[cli.command1]
"help"="HELP of command1"
"args"= [
    {"key"="positional_param1", "mult"="1", "type"="str"},
]

[cli.command2]
"help"="HELP of command2"
"args"= [
    {"key"="positional_param2", "mult"="1", "type"="str"},
]
"entrypoint"="cli_def.script.main:command2_handler"

"""

def command2_handler(event):
    print("=== command2 handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)

def print_handler(event):
    print("=== my fallback handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)

def load_definition() -> CliDef:
    parser = CliDefParser()
    #cli_def = parser.parse_from_toml("simple_cli_def.toml")
    cli_def = parser.parse_from_toml_text(CLI_DEF_TOML_TEXT)
    return cli_def

def build_parser(cli_def: CliDef) -> argparse.ArgumentParser:
    builder = ArgparseBuilder()
    return builder.build_argparse(cli_def)


from cli_def.runtime import Dispatcher

def main():
    cli_def = load_definition()
    parser = build_parser(cli_def)
    dispatcher = Dispatcher(cli_def, print_handler)

    print("=== loaded cli_def ===")
    for line in cli_def.dump_tree():
        print(line)
    print("======================")

    args = parser.parse_args()

    dispatcher.dispatch(args)

if __name__ == "__main__":
    main()