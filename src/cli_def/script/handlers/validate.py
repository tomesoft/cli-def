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
from ...core.validator import (
    CliDefValidator,
    CliDefValidationCode,
    CliDefValidationLevel,
    CliDefValidationCategory,
)
from cli_def.ops.utils.renderer import (
    Table,
    RowRecord,
    RowType,
    RowConditionalStyle,
    ColumnConditinalStyle,
    Style,
    Cell
)
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

    columns=["#", "defpath", "category", "level", "code", "message"]
    valuess=[(
        r.node.defpath,
        r.code.category,
        r.code.level,
        r.code.name,
        r.message,
        ) for r in validator.records
    ] + [["---"]] # separator
    table = TableBuilder.from_columns_and_values(
        columns=columns,
        valuess=valuess,
        headers=[col.upper() for col in columns]
        # row_conditional_styles=[
        #     RowConditionalStyle(cond=is_error_row, style=Style(fg_color="red")),
        #     RowConditionalStyle(cond=is_warning_row, style=Style(fg_color="yellow")),
        # ]
    )
    for header_row in table.get_rows_of_type(RowType.HEADER):
        header_row.default_style = Style(bold=True, fg_color="cyan")

    table.column_mapping["level"].conditional_styles = [
        ColumnConditinalStyle(
            lambda val, _: val == CliDefValidationLevel.ERROR,
            Style(fg_color="red")
        ),
        ColumnConditinalStyle(
            lambda val, _: val == CliDefValidationLevel.WARNING,
            Style(fg_color="yellow")
        ),
    ]


    errors = [r for r in validator.records if r.code.level == CliDefValidationLevel.ERROR]
    warnings = [r for r in validator.records if r.code.level == CliDefValidationLevel.WARNING]

    print(
        f" Validation failed: {len(errors)} error(s), {len(warnings)} warning(s)"
    )
    print()
    for text in PrettyRenderer().render_table(table):
        print(text)

    print(f"[{len(table.get_rows_of_type(RowType.DATA))} items]")

    return CliHandlerResult.make_result(
        event,
        "run_validate",
        data=validator.records
    )

