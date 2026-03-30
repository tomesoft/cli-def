# cli_def/script/handlers.py
from typing import Sequence, Any
import argparse
import logging
import subprocess
import sys
import os
import json
import copy

from importlib import resources

from ..models import CliDef
from ..parsers import CliDefParser
from ..runtime import (
    CliEvent,
    CliDispatcher,
    CliSession,
    CliRunner,
    HandlerResult,
)
from ..ops import (
    load_cli_def_path,
    dump_cli_def_pretty,
)
from ..runtime import cli_def_handler, HandlerResult
from ..runtime.handlers import (
    scan_handlers,
    make_digest_scan_result,
    clear_all_handlers_catalog,
    can_import,
)


def load_builtin_cli_def(*relative_paths):
    path = resources.files("cli_def.resources")
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

    logging.info("=== repl command ===")

    cli_def_file = event.params.get("cli_def_file")
    if cli_def_file is None:
        logging.info("load builtin cli_def")
        cli_def = load_builtin_cli_def()
    else:
        logging.info(f"try to load: {cli_def_file} ")
        cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return HandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file or "builtin"}",
        )

    if event.ctx.debug or event.ctx.verbose:
        dump_cli_def_pretty(cli_def)
    no_ctx_propagate = event.params.get("no_ctx_propagate")
    if not no_ctx_propagate:
        child_ctx = copy.deepcopy(event.ctx)
    else:
        child_ctx = None

    print("Type 'help' to list commands, 'exit' to exit")
    session = CliSession(
        cli_def,
        fallback_handler=print_handler,
        cli_def_file=cli_def_file,
        ctx=child_ctx,
    )
    session.repl()

    return HandlerResult.make_result(
        event,
        "run_repl",
        data=session.result_store.all_data()
    )



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
        ctx=event.ctx,
    )
    session.repl(prompt=f"demo[{profile}]> ")

    return HandlerResult.make_result(
        event,
        "run_repl",
        data=session.result_store.all_data()
    )


def run_run(event: CliEvent):
    logging.info("=== run command ===")
    cli_def_file = event.params.get("cli_def_file")
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return HandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    if event.ctx.debug or event.ctx.verbose:
        dump_cli_def_pretty(cli_def)

    no_ctx_propagate = event.params.get("no_ctx_propagate")
    if not no_ctx_propagate:
        child_ctx = copy.deepcopy(event.ctx)
    else:
        child_ctx = None

    print(f"[run] forwarding args: {event.extra_args}, no_ctx_propagate: {no_ctx_propagate}")
    runner = CliRunner(
        cli_def,
        fallback_handler=print_handler,
        default_ctx=child_ctx,
    )

    result = runner.run(
        argv=event.extra_args if event.extra_args else [],
    )

    return HandlerResult.make_result(
        event,
        "run_run",
        data=result.all_data(),
    )


def run_dump(event: CliEvent):
    logging.info("=== dump command ===")
    cli_def_file = event.params.get("cli_def_file")
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return HandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    rendered = []
    dump_cli_def_pretty(cli_def, rendered=rendered)

    return HandlerResult.make_result(
        event,
        "run_dump",
        data=rendered
    )


@cli_def_handler("/cli-def/scan")
def run_scan(event: CliEvent):
    logging.info("=== scan command ===")
    package_name = event.params.get("package") or __package__
    show_all = event.params.get("show_all")
    no_subprocess = event.params.get("no_subprocess")
    recursive = event.params.get("recursive")
    print(f"package_name: {package_name}")

    if not can_import(package_name):
        print(f"[ERROR] package not found: {package_name}")
        return HandlerResult.make_error(
            event.command.defpath,
            f"[ERROR] package not found: {package_name}"
        )

    if no_subprocess:
        logging.info("[scan without subprocess]")
        result = scan_handlers(package_name)
        digest = make_digest_scan_result(result)

    else:
        logging.info("[scan with subprocess]")
        proc_result = subprocess.run([
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
        logging.debug(f"@@@ result.stdout: {proc_result.stdout}")
        digest = json.loads(proc_result.stdout)


    if digest is None or len(digest["catalog_digest"]) == 0:
        print("handlers not found")
        return HandlerResult.make_result(event, "handlers not found", digest)


    if event.ctx.verbose:
        print("=== scan coverage ===")
        for k, v in digest["scan_coverage"].items():
            print(f"{k} : {v}")
        print("=====================")

    catalog = digest["catalog_digest"]
    #logging.info(f"catalog: {catalog}")
    for key, lst in catalog.items():
        print(f"{key}:")
        indent = "    "
        for meta_digest in lst:
            # if not show_all and not meta.late_bindings:
            #     continue
            print(indent + f"{meta_digest.get("entrypoint")}, desc={meta_digest.get("description")!r}, late_bindings={meta_digest.get("late_bindings")}")

    #return {"catalog": catalog}
    return HandlerResult.make_result(
        event,
        "run_scan",
        data = catalog
    )



@cli_def_handler("/cli-def/test1", late_bindings=True, description="late binding test1")
def dummy1(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test2", late_bindings=True, description="late binding test2", tags=["demo"])
def dummy2(event: CliEvent):
    pass

@cli_def_handler("/cli-def/test3", late_bindings=True, description="late binding test3", tags=["demo"])
def dummy3(event: CliEvent):
    pass