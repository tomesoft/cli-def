# cli_def/script/handlers/run.py
from __future__ import annotations
from typing import Sequence, Any
import logging
import copy


from ...runtime import (
    CliEvent,
    CliRunner,
    CliHandlerResult,
)
from ...ops import (
    load_cli_def_path,
    CliDefDumper,
)

from ...runtime import cli_def_handler, CliHandlerResult

from ..common import load_builtin_cli_def, print_handler




# --------------------------------------------------------------------------------
#
# run command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/run", description="builin run command handler", late_binding=True)
def run_run(event: CliEvent):
    logging.info("=== run command ===")
    cli_def_file = event.params.get("cli_def_file")
    assert cli_def_file is not None
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return CliHandlerResult.make_error(event, f"cli_def file could not load: {cli_def_file}")
    if cli_def is None:
        return CliHandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    assert event.ctx is not None
    if event.ctx.debug or event.ctx.verbose:
        CliDefDumper.dump_pretty(cli_def)

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

    return CliHandlerResult.make_result(
        event,
        "run_run",
        data=result.all_data(),
    )

