# cli_def/script/handlers.py
from typing import Sequence, Any
import argparse
import logging
import subprocess
import sys
import os
import json

from importlib import resources

from ..models import CliDef
from ..parsers import CliDefParser
from ..argparse import ArgparseBuilder
from ..runtime import (
    CliEvent,
    Dispatcher,
    CliSession,
)
from ..ops import (
    load_cli_def_path,
    dump_cli_def_pretty,
)
from ..runtime import cli_def_handler
from ..runtime.utils import (
    execute_cli,
)
from ..runtime.handlers import (
    scan_handlers,
    clear_all_handlers_catalog,
    can_import,
)


def load_builtin_cli_def(*relative_paths):
    path = resources.files("cli_def.resources")
    #print(f"relative_paths: {relative_paths!r}")
    if len(relative_paths):
        path = path.joinpath(*relative_paths)
    else:
        path = path.joinpath("cli_def.toml")
    return CliDefParser().parse_from_toml(path)


def print_handler(event: CliEvent):
    print("=== fallback handler ===")
    print("  PATH:", event.path)
    print("  PARAMS:", event.params)
    if event.extra_args:
        print("  EXTRA:", event.extra_args)


# def load_definition(path_to_toml: str) -> CliDef:
#     parser = CliDefParser()
#     if path_to_toml:
#         cli_def = parser.parse_from_toml(path_to_toml)
#     else:
#         cli_def = load_builtin_cli_def()
#     return cli_def


# --------------------------------------------------------------------------------
# command implementations (specified in cli-def toml)
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/repl")
def run_repl(event: CliEvent):
    print("=== repl command ===")
    cli_def_file = event.params.get("cli_def_file")
    if cli_def_file is None:
        print("load builtin cli_def")
        cli_def = load_builtin_cli_def()
    else:
        print(f"try to load: {cli_def_file} ")
        cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return
    dump_cli_def_pretty(cli_def)
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
    dump_cli_def_pretty(cli_def)
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
    logging.info("=== run command ===")
    cli_def_file = event.params.get("cli_def_file")
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return
    dump_cli_def_pretty(cli_def)
    print(f"[run] forwarding args: {event.extra_args}")
    execute_cli(
        cli_def,
        argv=event.extra_args if event.extra_args else [],
        fallback_handler=print_handler
    )

def run_dump(event: CliEvent):
    logging.info("=== dump command ===")
    cli_def_file = event.params.get("cli_def_file")
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return
    dump_cli_def_pretty(cli_def)


@cli_def_handler("/cli-def/scan")
def run_scan(event: CliEvent):
    logging.info("=== scan command ===")
    package_name = event.params.get("package") or __package__
    show_all = event.params.get("show_all")
    recursive = event.params.get("recursive")
    print(f"package_name: {package_name}")

    if not can_import(package_name):
        print(f"[ERROR] Cannot find package: {package_name}")
        return 1

    result = subprocess.run([
        sys.executable,
        "-m",
        "cli_def._internal.scan_runner",
        package_name,
    ] + (
        ["--all"] if show_all else []
    ) + (
        ["--recursive"] if recursive else []
    )
    , capture_output=True,
    text=True,
    env=os.environ.copy()
    )
    catalog = json.loads(result.stdout)
    #print(f"result: {catalog}")
    # catalog = scan_handlers(package_name)
    if len(catalog) == 0:
        print("handlers not found")
        return

    for key, lst in catalog.items():
        print(f"{key}:")
        indent = "    "
        for meta_digest in lst:
            # if not show_all and not meta.late_bindings:
            #     continue
            print(indent + f"{meta_digest.get("entrypoint")}, desc={meta_digest.get("description")!r}, late_bindings={meta_digest.get("late_bindings")}")



@cli_def_handler("/cli-def/test1", late_bindings=True, description="late binding test1")
def dummy1(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test2", late_bindings=True, description="late binding test2", tags=["demo"])
def dummy2(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test3", late_bindings=True, description="late binding test3", tags=["demo"])
def dummy3(event: CliEvent):
    pass