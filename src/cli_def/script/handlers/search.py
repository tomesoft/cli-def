# cli_def/script/handlers/search.py
from __future__ import annotations
from typing import Sequence, Any, Mapping
import logging
from pathlib import Path


from ...models import (
    CliDef,
)
from ...runtime import (
    CliEvent,
    CliHandlerResult,
)
from ...ops import (
    load_cli_def_path,
    CliDefDumper,
)
from ...ops.utils.renderer import (
    Style,
    Column,
    ColumnType,
    RowRecord,
    RowType,
    Cell,
    Table,
)
from ...ops.utils.pretty_renderer import PrettyRenderer

from ...runtime import cli_def_handler, CliHandlerResult
from ...runtime.scanner import CliHandlerScanner



# --------------------------------------------------------------------------------
#
# search command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/search", description="builtin search command handler", late_binding=True)
def run_search(event: CliEvent):
    logging.info("=== search command ===")
    dir_to_search = event.params.get("directory_to_search")
    recursive = event.params.get("recursive")

    assert dir_to_search
    path = Path(dir_to_search)

    if not path.is_dir():
        msg = f"[Error] directory not found: {dir_to_search}"
        print(msg)
        return CliHandlerResult.make_error(event, msg)

    toml_files = path.glob(
        "**/*.toml" if recursive else "*.toml"
    )

    toml_files = list(toml_files)
    logging.info(f"@@@ {len(toml_files)} TOMLs found")
    mapping: dict[Path, CliDef] = {}
    for toml in toml_files:
        cli_def = load_cli_def_path(toml)
        if cli_def is None:
            continue
        mapping[toml] = cli_def

    pretty_report(event, mapping)

    return CliHandlerResult.make_result(
        event,
        "run_search",
        data = mapping
    )


def pretty_report(event: CliEvent, mapping: Mapping[Path, CliDef]):
    dump_all = event.params.get("dump_all")

    columns = [
        Column("#", col_type=ColumnType.INDEX1, default_style=Style(h_align="right")),
        Column("path", default_style=Style()),
        #Column("|", col_type=ColumnType.SEPARATOR),
        Column("cli_key"),
        Column("cli_help"),
        Column("nodes_count", default_style=Style(h_align="right")),
    ]
    column_mapping = {col.key: col for col in columns}
    display_column_keys = list(column_mapping.keys())

    row_records: list[RowRecord] = []
    row_records.append(RowRecord(row_type=RowType.HEADER_KEY))
    row_records.append(RowRecord(row_type=RowType.SEPARATOR))
    for k, v in mapping.items():
        row = RowRecord(
            cell_mapping={
                "path": Cell(k),
                "cli_key": v.key,
                "cli_help": v.help,
                "nodes_count": len(list(v.iter_all_nodes())),
            }, #default_style=Style(bg_color="yellow")
        )
        row_records.append(row)
    row_records.append(RowRecord(row_type=RowType.SEPARATOR))

    table = Table(
        column_mapping=column_mapping,
        row_records=row_records,
        display_column_keys=display_column_keys,
    )

    renderer = PrettyRenderer()
    for rendered_line in renderer.render_table(table):
        print(rendered_line)
    print(renderer.render_text(f"[{len(mapping)} items]", Style()))


