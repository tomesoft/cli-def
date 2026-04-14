# cli_def/script/handlers/scan.py
from __future__ import annotations
from typing import Sequence, Any, Mapping
import logging
import copy
from pathlib import Path

from importlib import resources

from ...core.models.raw import (
    CliDef,
    CommandDef,
)
from ...core.parser import CliDefParser
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
from ...ops.utils.renderer_ops import TableBuilder

from ...runtime import cli_def_handler, CliHandlerResult
from ...runtime.scanner import CliHandlerScanner



# --------------------------------------------------------------------------------
#
# scan command handler
#
# --------------------------------------------------------------------------------
@cli_def_handler("/cli-def/scan", description="builtin scan command handler", late_binding=True)
def run_scan(event: CliEvent):
    logging.info("=== scan command ===")
    package_name = event.params.get("package") or __package__
    no_subprocess = event.params.get("no_subprocess")
    recursive = event.params.get("recursive")
    check_toml = event.params.get("check_toml_path")

    print(f"package_name: {package_name}")
    assert package_name is not None

    cli_def = None
    if check_toml:
        cli_def = load_cli_def_path(check_toml)
        if cli_def is None:
            print(f"[WARNING] cli_def file {check_toml} could not load, so will not check.")


    scanner = CliHandlerScanner()
    result = scanner.scan(
        package_name,
        no_subprocess=no_subprocess is True,
        recursive=recursive is True,
    )

    if result is None:
        return CliHandlerResult.make_error(
            event,
            f"package_name not found: {package_name}"
        )

    digest = result.to_digest()

    if digest is None or len(digest["catalog_digest"]) == 0:
        print("No handlers found")
        return CliHandlerResult.make_result(event, "No handlers found", digest)

    assert event.ctx is not None
    if event.ctx.verbose:
        print("=== scan coverage ===")
        for k, v in digest["scan_coverage"].items():
            print(f"{k} : {v}")
        print("=====================")

    specified_entry_point_set = {
        n.entrypoint for n in cli_def.iter_all_nodes() if isinstance(n, CommandDef) and n.entrypoint
    } if cli_def else None

    # catalog = digest["catalog_digest"]
    # for key, lst in catalog.items():
    #     print(f"{key}:")
    #     indent = "    "
    #     for meta_digest in lst:
    #         late_binding = meta_digest.get("late_binding")
    #         if not show_all and not late_binding:
    #             continue
    #         entrypoint = meta_digest.get("entrypoint")
    #         desc = meta_digest.get("description")
    #         bound = entrypoint in specified_entry_point_set
    #         print(indent + f"{"*" if bound else " "}{entrypoint}, desc={desc}, late_binding={late_binding}")

    pretty_report(event, digest, specified_entry_point_set)

    return CliHandlerResult.make_result(
        event,
        "run_scan",
        data = digest["catalog_digest"]
    )


def pretty_report(event: CliEvent, digest: Mapping[str, Any], entrypoint_set: set[str]|None):
    show_early = event.params.get("show_early")
    catalog: Mapping[str, Any] = digest["catalog_digest"]

    check_enabled = entrypoint_set is not None
    entrypoint_set = entrypoint_set or set()

    # 1) prepare columns
    columns = [
        Column("#", col_type=ColumnType.INDEX1, default_style=Style(h_align="right")),
        Column("defpath"),
        Column("entrypoint"),
        Column("desc"),
    ]
    if check_enabled:
        columns.append(
            Column("is_bound")
        )
    if show_early:
        columns.append(
            Column("binding_type"),
        )

    column_mapping = {col.key: col for col in columns}
    display_column_keys = list(column_mapping.keys())

    # 2) prepare rows
    row_records: list[RowRecord] = []
    row_records.append(RowRecord(row_type=RowType.HEADER_KEY))
    row_records.append(RowRecord(row_type=RowType.SEPARATOR))

    for k in sorted(catalog.keys()):
        lst = catalog[k]
        for meta_digest in lst:
            is_late_binding = meta_digest.get("late_binding")
            if not show_early and not is_late_binding:
                continue
            binding_type = "late" if is_late_binding else "early"
            entrypoint = meta_digest.get("entrypoint")
            is_bound = entrypoint in entrypoint_set
            row_style = Style(fg_color="green") if is_bound else None
            row = RowRecord(
                cell_mapping={
                    "defpath": k,
                    "entrypoint": entrypoint,
                    "desc": meta_digest.get("description"),
                    "is_bound": is_bound,
                    "binding_type": binding_type,
                }, default_style=row_style
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
    #print(renderer.render_text(f"[{len(catalog)} items]", Style()))


