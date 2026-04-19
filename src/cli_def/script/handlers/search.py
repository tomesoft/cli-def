# cli_def/script/handlers/search.py
from __future__ import annotations
from typing import Sequence, Any, Mapping
import logging
from pathlib import Path


from ...core.models.raw import (
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
from ...ops.utils.renderer_ops import TableBuilder
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
    recursive = event.params.get("recursive") or False
    dump_all = event.params.get("dump_all") or False

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

    pretty_report(event, mapping, dump_all=dump_all)

    return CliHandlerResult.make_result(
        event,
        "run_search",
        data = mapping
    )


from .dump import dump_cli_def

def pretty_report(
        event: CliEvent,
        mapping: Mapping[Path, CliDef],
        *,
        dump_all: bool
    ):

    # 1) prepare columns
    columns = ["#", "path", "cli_key", "cli_help", "nodes_count"]

    # 2) prepare valuess
    valuess: list[list[Any]] = []
    for k in sorted(mapping.keys()):
        v = mapping[k]
        values = [
            k,
            v.key,
            v.help,
            len(list(v.iter_all_nodes())),
        ]
        valuess.append(values)
    valuess.append(["---"]) # separator

    table = TableBuilder.from_columns_and_values(
        columns=columns,
        valuess=valuess,
        headers=[col.upper() for col in columns]
    )
    table.column_mapping["nodes_count"].default_style = Style(h_align="right")
    for header in table.get_rows_of_type(RowType.HEADER):
        header.default_style = Style(bold=True, fg_color="cyan")

    renderer = PrettyRenderer()
    rendered_lines = renderer.render_table(table)
    rendered_headers = [
        l for l in rendered_lines
        if isinstance(l.source, tuple) and l.source[2].source.row_type == RowType.HEADER
    ]
    after_dump = False
    for i, rendered_line in enumerate(rendered_lines):
        if after_dump and i < len(rendered_lines) - 1:
            for h in rendered_headers:
                print(h)
        print(rendered_line)
        if dump_all and isinstance(rendered_line.source, tuple):
            sub_index, sub_lines, pre_rendered_row = rendered_line.source
            assert isinstance(pre_rendered_row.source, RowRecord)
            if sub_index < sub_lines -1:
                continue
            if pre_rendered_row.source.row_type == RowType.DATA:
                # print(f"@@@ rendered_line.source:{pre_rendered_row.source.cell_mapping["path"]}")
                assert pre_rendered_row.source.cell_mapping
                path = pre_rendered_row.source.cell_mapping["path"]
                assert path
                dump_cli_def(path, as_help=False, show_resolved=False, row_offset=2)
                after_dump = True

    print(renderer.render_text(f"[{len(mapping)} items]", Style()))


