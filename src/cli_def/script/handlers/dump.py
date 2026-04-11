# cli_def/script/handlers/dump.py
from __future__ import annotations
from typing import Sequence, Any
import logging

from ...runtime import (
    CliEvent,
    CliHandlerResult,
)
from ...ops import (
    load_cli_def_path,
    CliDefDumper,
)
from ...resolver import CliDefResolver

from ...runtime import cli_def_handler, CliHandlerResult



# --------------------------------------------------------------------------------
#
# dump command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/dump", description="builtin dump command handler", late_binding=True)
def run_dump(event: CliEvent):
    #check_entrypoints = event.params.get("check_entrypoints", False)
    show_resolved = event.params.get("show_resolved", False)
    as_help = event.params.get("as_help", False)

    logging.info("=== dump command ===")

    cli_def_file = event.params.get("cli_def_file")

    assert cli_def_file is not None
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return CliHandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    if show_resolved:
        print("@@@ RESOLVE @@@")
        resolver = CliDefResolver()
        cli_def = resolver.resolve(cli_def)
    
    # table = CliDefDumper.dump(cli_def)
    # if check_entrypoints:

    table = CliDefDumper.dump_pretty(cli_def, as_help=as_help, as_resolved=show_resolved)

    return CliHandlerResult.make_result(
        event,
        "run_dump",
        data=table
    )

