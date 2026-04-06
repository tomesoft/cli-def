# cli_def/ops/dumper.py
from __future__ import annotations
from typing import Sequence, Any, Tuple, Iterable, Callable

from ..models import CliDef, CliDefNode, MultDef

from .utils.renderer_ops import TableBuilder
from .utils.pretty_renderer import PrettyRenderer
from .utils.renderer import (
    Style,
    RowRecord,
    RowType,
    Table,
)


class CliDefDumper:
    COL_KEY        = "key"
    COL_CLS        = "cls"
    COL_OPTION     = "option"
    COL_MULT       = "mult"
    COL_TYPE       = "type"
    COL_DEFAULT    = "default"
    COL_CHOICES    = "choices"
    COL_HELP       = "help"
    COL_ENTRYPOINT = "entrypoint"

    COL_KEYS_FULL = [
       COL_KEY, COL_CLS, COL_OPTION,
       COL_MULT, COL_TYPE, COL_DEFAULT,
       COL_CHOICES, COL_HELP, COL_ENTRYPOINT,
    ]

    COL_KEYS_FOR_HELP = [
       COL_KEY, COL_CLS, COL_OPTION,
       COL_MULT, COL_TYPE, COL_DEFAULT,
       COL_CHOICES, COL_HELP,
    ]


    @classmethod
    def to_display_text(cls, val: Any, none_expr: str|None = None) -> str:
        if none_expr is None:
            none_expr = ""
        if val is None:
            return none_expr
        return str(val)


    @classmethod
    def to_short_cls(cls, type) -> str:
        if type.__name__ == "CommandDef":
            return "cmd"
        if type.__name__ == "ArgumentDef":
            return "arg"
        if type.__name__ == "CliDef":
            return "cli"
        return "unk"


    @classmethod
    def dump_tree(
            cls,
            cli_def_node: CliDefNode,
            *,
            col_keys: Iterable[str],
        ) -> Sequence[RowRecord]:

        row_records: list[RowRecord] = []

        for node in cli_def_node.iter_all_nodes():
            cell_mapping = {}
            for col_key in col_keys:
                if col_key == cls.COL_KEY:
                    cell = "  " * node.deflevel + node.key
                elif col_key == cls.COL_CLS:
                    cell = cls.to_short_cls(type(node))
                elif col_key == cls.COL_MULT:
                    mult: MultDef|None = getattr(node, "mult", None)
                    cell = mult.to_str() if mult else None
                elif col_key == cls.COL_OPTION:
                    if opt := getattr(node, "option", None):
                        if aliases := getattr(node, "aliases", []):
                            cell = f"{opt} ({','.join(aliases)})"
                        else:
                            cell = opt
                    else:
                        cell = None
                elif col_key == cls.COL_TYPE:
                    if getattr(node, "is_flag", None):
                        cell = "flag"
                    else:
                        cell = getattr(node, "type", None)
                else:
                    cell = getattr(node, col_key, None)
                cell_mapping[col_key] = cell
            row_records.append(
                RowRecord(cell_mapping, source=node)
            )

        return row_records


    @classmethod
    def dump(
        cls,
        cli_def: CliDef,
        *,
        as_help: bool=False,
    ) -> Table:

        if as_help:
            col_keys = cls.COL_KEYS_FOR_HELP
        else:
            col_keys = cls.COL_KEYS_FULL

        row_records = cls.dump_tree(cli_def, col_keys=col_keys)
        col_keys = ["#"] + list(col_keys)
        row_separator = RowRecord(row_type=RowType.SEPARATOR)
        row_records = [row_separator] + list(row_records) + [row_separator]
        table = TableBuilder.from_row_records(
            columns=col_keys,
            row_records=row_records,
            display_column_keys=col_keys,
        )
        table.row_records.insert(
            0,
            RowRecord(
                row_type=RowType.HEADER_KEY,
                default_style=Style(bold=True)
            )
        )

        # apply column styles
        for col_key, col in table.column_mapping.items():
            if col_key == "help":
                col.default_style = Style(
                    wrap_width=30,
                ).merge(col.default_style)
            if col_key == "choices":
                col.default_style = Style(
                    wrap_width=20,
                ).merge(col.default_style)
            if as_help:
                if col_key == "option":
                    col.default_style = Style(
                        bold=True,
                        fg_color="green",
                        ).merge(col.default_style)

        if as_help:
            # apply row styles
            for row in table.row_records:
                if row.get_raw_value("cls", None) == "cmd":
                    key = row.get_raw_value("key", "")
                    if key is not None and not key.strip().startswith("_"):
                        row.default_style = Style(
                            fg_color="magenta",
                            bold=True,
                            #underline=True,
                            ).merge(row.default_style)
                # if row.get_raw_value("cls", None) == "arg":
                #     row.default_style = Style(fg_color="cyan")
        return table


    @classmethod
    def dump_pretty(
            cls,
            cli_def: CliDef,
            *,
            as_help: bool=False,
            print_func: Callable|None = None
        ) -> Table:

        table = cls.dump(cli_def, as_help=as_help)

        cls.print_table(table, print_func=print_func)

        return table


    @classmethod
    def print_table(
            cls,
            table: Table,
            *,
            print_func: Callable|None = None
    ):
        print_func = print_func or print
        renderer = PrettyRenderer()
        renderer.value_formatter = lambda v: str(v) if v is not None else ""
        rendered_seq = renderer.render_table(table)
        if rendered_seq:
            for line in rendered_seq:
                print_func(line)
