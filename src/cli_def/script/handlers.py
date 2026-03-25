# cli_def/script/handlers.py
from typing import Sequence, Any
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


def dump_cli_def(cli_def: CliDef, details: bool=False):
    print("=== loaded cli_def ===")
    col_widths = None
    row_values = cli_def.dump_tree(details=True)
    # header_row = row_values[0]
    # data_rows = row_values[1:]
    rows = []
    for i, cells in enumerate(row_values, start=0):
        row = [str(i)] + [(str(c) if c else "") for c in cells]
        if col_widths is None:
            col_widths = [len(c) for c in row]
        else:
            for i, w in enumerate(col_widths):
                col_widths[i] = max(col_widths[i], len(row[i]))
        rows.append(row)
    # format
    rows[0][0]="#"
    col_rjust=[False for _ in rows[0]]
    col_rjust[0] = True
    lines = []
    gap = "  "
    separator = "-" * (sum(col_widths) + len(gap) * (len(col_widths)-1))
    def render_row(
            disp_vals: Sequence[Any],
            col_widths: Sequence[int],
            col_rjust: Sequence[bool]
            ) -> list[str]:
        cells = []
        for i, c in enumerate(disp_vals):
            if col_rjust[i]:
                cell = c.rjust(col_widths[i])
            else:
                cell = c.ljust(col_widths[i])
            cells.append(cell)
        return cells

    header = render_row(rows[0], col_widths, col_rjust)
    lines.append(gap.join(header))
    lines.append(separator)

    for r in rows[1:]:
        cells = render_row(r, col_widths, col_rjust)
        line = gap.join(cells)
        lines.append(line)

    lines.append(separator)
    # print
    for l in lines:
        print(l)

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
        # cli_def = parser.parse_from_toml_text(CLI_DEF_TOML_TEXT)
        cli_def = load_builtin_cli_def()
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