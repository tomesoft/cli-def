# cli_def/script/handlers.py
import argparse

from importlib import resources

from ..parsers import CliDefParser
from ..models import CliDef
from ..argparse import ArgparseBuilder
from ..runtime import (
    CliEvent,
    Dispatcher,
    CliSession,
)
from ..runtime import cli_def_handler
from ..runtime.utils import (
    execute_cli,
)
from ..runtime.handlers import (
    scan_handlers,
)

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
    {"key"="positional_param2", "mult"="*", "type"="str"},
]
"entrypoint"="cli_def.script.handlers:command2_handler"

"""

def load_builtin_cli_def(*relative_paths):
    path = resources.files("cli_def.resources")
    #print(f"relative_paths: {relative_paths!r}")
    if len(relative_paths):
        path = path.joinpath(*relative_paths)
    else:
        path = path.joinpath("cli_def.toml")
    return CliDefParser().parse_from_toml(path)


def dump_cli_def(cli_def: CliDef):
    print("=== loaded cli_def ===")
    for i, line in enumerate(cli_def.dump_tree(), start=1):
        print(f"{i}| {line}")
    print("======================")


def command2_handler(event: CliEvent):
    print("=== command2 handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)
    if event.extra_args:
        print("  EXTRA:", event.extra_args)

def print_handler(event: CliEvent):
    print("=== fallback handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)
    if event.extra_args:
        print("  EXTRA:", event.extra_args)


def load_definition(path_to_toml: str) -> CliDef:
    parser = CliDefParser()
    if path_to_toml:
        cli_def = parser.parse_from_toml(path_to_toml)
    else:
        cli_def = parser.parse_from_toml_text(CLI_DEF_TOML_TEXT)
    return cli_def

# --------------------------------------------------------------------------------
# command implementations (specified in cli-def toml)
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/repl")
def run_repl(event: CliEvent):
    print("=== repl command ===")
    cli_def_file = event.params.get("cli_def_file")
    if cli_def_file is None:
        return

    cli_def = load_definition(cli_def_file)
    dump_cli_def(cli_def)
    print("Type 'help' to list commands, 'exit' to exit")
    session = CliSession(
        cli_def,
        fallback_handler=print_handler,
        cli_def_file=cli_def_file,
    )
    session.repl()

@cli_def_handler("/cli-def/demo")
def run_demo(event: CliEvent):
    profile = event.params.get("profile") or "beginner"
    cli_def = load_builtin_cli_def("demo", profile + ".toml")
    dump_cli_def(cli_def)
    print(f"=== demo: {profile} ===")
    print("Type 'help' to list commands, 'exit' to exit")
    # go repl 
    session = CliSession(
        cli_def,
        fallback_handler=print_handler,
        profile=profile,
    )
    session.repl(prompt=f"demo[{profile}]> ")

def run_run(event: CliEvent):
    print("=== run command ===")
    toml_file = event.params.get("cli_def_file")
    cli_def = load_definition(toml_file)
    if cli_def is None:
        print(f"Error invalid cli-def file: {toml_file}")
        return
    dump_cli_def(cli_def)
    print(f"[run] forwarding args: {event.extra_args}")
    execute_cli(
        cli_def,
        argv=event.extra_args if event.extra_args else [],
        fallback_handler=print_handler
    )

def run_dump(event: CliEvent):
    print("=== dump command ===")
    toml_file = event.params.get("cli_def_file")
    cli_def = load_definition(toml_file)
    if cli_def is None:
        print(f"Error invalid cli-def file: {toml_file}")
        return
    dump_cli_def(cli_def)


@cli_def_handler("/cli-def/scan")
def run_scan(event: CliEvent):
    print("=== scan command ===")
    package_name = event.params.get("package") or __package__
    show_all = event.params.get("show_all")
    print(f"package_name: {package_name}")
    catalog = scan_handlers(package_name)
    if len(catalog) == 0:
        print("handlers not found")
        return

    for key, lst in catalog.items():
        print(f"{key}:")
        indent = "    "
        for meta in lst:
            if not show_all and not meta.late_bindings:
                continue
            print(indent + f"{meta.entrypoint}, desc={meta.description!r}, late_bindings={meta.late_bindings}, ")



@cli_def_handler("/cli-def/test1", late_bindings=True, description="late binding test1")
def dummy1(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test2", late_bindings=True, description="late binding test2", tags=["demo"])
def dummy2(event: CliEvent):
    pass