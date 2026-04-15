# cli_def/script/handlers/validate.py
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
from ...core.resolver import CliDefResolver

from ...runtime import cli_def_handler, CliHandlerResult
from ...core.validator import CliDefValidator
from cli_def.ops.utils.renderer_ops import (
    TableBuilder,
)
from cli_def.ops.utils.pretty_renderer import (
    PrettyRenderer
)

# --------------------------------------------------------------------------------
#
# dump command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/validate", description="builtin validate command handler", late_binding=True)
def run_validate(event: CliEvent):

    logging.info("=== validate command ===")

    cli_def_file = event.params.get("cli_def_file")

    assert cli_def_file is not None
    cli_def = load_cli_def_path(cli_def_file)
    if cli_def is None:
        return CliHandlerResult.make_error(
            event,
            f"cli_def could not load: {cli_def_file}",
        )

    resolver = CliDefResolver()
    resolved = resolver.resolve(cli_def)
    
    validator = CliDefValidator()
    validator.validate_cli(resolved)

    if not validator.has_errors:
        msg = "No error found"
        print(msg)
        return CliHandlerResult.make_result(event, msg)
    
    table = TableBuilder.from_columns_and_values(
        columns=["#", "defpath", "error"],
        valuess=[["---"]] + [(r.node.defpath, r.error) for r in validator.records],
        headers=["defpath", "error"]
    )

    print(f"{len(validator.records)} errors found.")
    for text in PrettyRenderer().render_table(table):
        print(text)



    return CliHandlerResult.make_result(
        event,
        "run_validate",
        data=validator.records
    )

