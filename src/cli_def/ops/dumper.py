# cli_def/ops/dumper.py
from typing import Sequence, Any

from ..models import CliDef, CliDefNode, MultDef



# def tiny_pretty_table_renderer(
#         raw_values: Sequence[Sequence[Any]],
#         columns: Sequence[str],
#         ) -> list[str]:
#     pass

def to_display_text(val: Any, none_expr: str = None) -> str:
    if none_expr is None:
        none_expr = ""
    if val is None:
        return none_expr
    return str(val)


def _to_short_cls(type) -> str:
    if type.__name__ == "CommandDef":
        return "cmd"
    if type.__name__ == "ArgumentDef":
        return "arg"
    if type.__name__ == "CliDef":
        return "cli"
    return "unk"

def _dump_tree(cli_def_node: CliDefNode, *, details:bool=False) -> Sequence[Sequence[str]]:
    col_keys = ("key", "cls", "option", "mult", "type",  "default", "choices", "help", "entrypoint")
    rows = []
    rows.append(col_keys)
    for node in cli_def_node.iter_all_nodes():
        cells = []
        for col in col_keys:
            if col == "key":
                cell = "  " * node.deflevel + node.key
            elif col == "cls":
                cell = _to_short_cls(type(node))
            elif col == "mult":
                mult: MultDef = getattr(node, "mult", None)
                cell = mult.to_str() if mult else None
            elif col == "option":
                if opt := getattr(node, "option", None):
                    if aliases := getattr(node, "aliases", []):
                        cell = f"{opt} ({','.join(aliases)})"
                    else:
                        cell = opt
                else:
                    cell = None
            elif col == "type":
                if is_flag := getattr(node, "is_flag", None):
                    cell = "flag"
                else:
                    cell = getattr(node, "type", None)
            else:
                cell = getattr(node, col, None)
            cells.append(cell)
        rows.append(cells)
    return rows


def dump_cli_def_pretty(cli_def: CliDef, details: bool=False):
    col_widths = None
    row_values = _dump_tree(cli_def, details=True)
    #row_values = cli_def.dump_tree()
    # header_row = row_values[0]
    # data_rows = row_values[1:]
    rows = []
    for i, cells in enumerate(row_values, start=0):
        row = [str(i)] + [to_display_text(c) for c in cells]
        if col_widths is None:
            col_widths = [len(c) for c in row]
        else:
            for i, w in enumerate(col_widths):
                col_widths[i] = max(col_widths[i], len(row[i]))
        rows.append(row)
    # format
    rows[0][0]="#"
    col_rjust=[False for _ in rows[0]]
    col_rjust[0] = True
    lines = []
    gap = "  "
    separator = "-" * (sum(col_widths) + len(gap) * (len(col_widths)-1))
    def render_row(
            disp_vals: Sequence[Any],
            col_widths: Sequence[int],
            col_rjust: Sequence[bool]
            ) -> list[str]:
        cells = []
        for i, c in enumerate(disp_vals):
            if col_rjust[i]:
                cell = c.rjust(col_widths[i])
            else:
                cell = c.ljust(col_widths[i])
            cells.append(cell)
        return cells

    header = render_row(rows[0], col_widths, col_rjust)
    lines.append(gap.join(header))
    lines.append(separator)

    for r in rows[1:]:
        cells = render_row(r, col_widths, col_rjust)
        line = gap.join(cells)
        lines.append(line)

    lines.append(separator)
    # print
    for l in lines:
        print(l)
