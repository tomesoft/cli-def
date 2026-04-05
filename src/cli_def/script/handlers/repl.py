# cli_def/script/handlers/repl.py
from __future__ import annotations
from typing import Sequence, Any
import logging
import copy


from ...runtime import (
    CliEvent,
    CliSession,
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
# repl command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/repl", description="builtin repl command handler", late_binding=True)
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
        return CliHandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file or "builtin"}",
        )

    assert event.ctx is not None
    if event.ctx.debug or event.ctx.verbose:
        CliDefDumper.dump_pretty(cli_def)
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

    return CliHandlerResult.make_result(
        event,
        "run_repl",
        data=session.result_store.all_data()
    )

