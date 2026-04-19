# cli_def/script/handlers/dump.py
from __future__ import annotations
from typing import Sequence, Any
import logging
from pathlib import Path

from ...basic.basic_types import PathLike

from ...runtime import (
    CliEvent,
    CliHandlerResult,
)
from ...ops import (
    load_cli_def_path,
    CliDefDumper,
)
from ...ops.utils.renderer import Table

from ...core.resolver import CliDefResolver

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
    assert cli_def_file
    cli_def_file = Path(cli_def_file)
    if not cli_def_file.exists():
        return CliHandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    table = dump_cli_def(
        cli_def_file,
        as_help=as_help,
        show_resolved=show_resolved,
    )

    return CliHandlerResult.make_result(
        event,
        "run_dump",
        data=table
    )


def dump_cli_def(
        cli_def_file: PathLike,
        *,
        as_help: bool,
        show_resolved: bool,
        row_offset: int|None = None,
    ) -> Table:

    cli_def = load_cli_def_path(cli_def_file)
    assert cli_def

    if show_resolved:
        logging.debug("@@@ RESOLVE @@@")
        resolver = CliDefResolver()
        cli_def = resolver.resolve(cli_def)
    
    table = CliDefDumper.dump_pretty(
        cli_def,
        as_help=as_help,
        as_resolved=show_resolved,
        row_offset=row_offset)
    return table
