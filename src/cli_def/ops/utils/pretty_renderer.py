# cli_def/ops/utils/pretty_renderer.py
from __future__ import annotations

from typing import Protocol, Callable, Any, Sequence, Tuple, Mapping, Union
from enum import Enum
from dataclasses import dataclass

from .renderer import (
    Style,
    ColumnType,
    Column,
    Cell,
    RowType,
    RowRecord,
    Table,
    RenderedObject,
    RendererProtocol,
    BaseRenderer,
    CellOrValue,
)

@dataclass
class PrettyRenderedText(RenderedObject):
    value: str

    def __str__(self) -> str:
        return self.value


RenderedTextOrText = Union[
    PrettyRenderedText,
    str
]


class AnsiCode(Enum):
    RESET     = "\033[0m"

    BOLD      = "\033[1m"
    THIN      = "\033[2m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK     = "\033[5m"
    INVERSE   = "\033[7m"

    # foreground color
    F_BLACK    = "\033[30m"
    F_RED      = "\033[31m"
    F_GREEN    = "\033[32m"
    F_YELLOW   = "\033[33m"
    F_BLUE     = "\033[34m"
    F_MAGENTA  = "\033[35m"
    F_CYAN     = "\033[36m"
    F_WHITE    = "\033[37m"
    # bright foreground color
    F_BRIGHT_BLACK    = "\033[90m"
    F_BRIGHT_RED      = "\033[91m"
    F_BRIGHT_GREEN    = "\033[92m"
    F_BRIGHT_YELLOW   = "\033[93m"
    F_BRIGHT_BLUE     = "\033[94m"
    F_BRIGHT_MAGENTA  = "\033[95m"
    F_BRIGHT_CYAN     = "\033[96m"
    F_BRIGHT_WHITE    = "\033[97m"

    # background color
    B_BLACK    = "\033[40m"
    B_RED      = "\033[41m"
    B_GREEN    = "\033[42m"
    B_YELLOW   = "\033[43m"
    B_BLUE     = "\033[44m"
    B_MAGENTA  = "\033[45m"
    B_CYAN     = "\033[46m"
    B_WHITE    = "\033[47m"
    # bright background color
    B_BRIGHT_BLACK    = "\033[100m"
    B_BRIGHT_RED      = "\033[101m"
    B_BRIGHT_GREEN    = "\033[102m"
    B_BRIGHT_YELLOW   = "\033[103m"
    B_BRIGHT_BLUE     = "\033[104m"
    B_BRIGHT_MAGENTA  = "\033[105m"
    B_BRIGHT_CYAN     = "\033[106m"
    B_BRIGHT_WHITE    = "\033[107m"


NAME_TO_FGCOLOR: dict[str, AnsiCode] = {
    "black"          : AnsiCode.F_BLACK,
    "red"            : AnsiCode.F_RED,
    "yellow"         : AnsiCode.F_YELLOW,
    "green"          : AnsiCode.F_GREEN,
    "blue"           : AnsiCode.F_BLUE,
    "magenta"        : AnsiCode.F_MAGENTA,
    "cyan"           : AnsiCode.F_CYAN,
    "white"          : AnsiCode.F_WHITE,
    "bright_black"   : AnsiCode.F_BRIGHT_BLACK,
    "bright_red"     : AnsiCode.F_BRIGHT_RED,
    "bright_yellow"  : AnsiCode.F_BRIGHT_YELLOW,
    "bright_green"   : AnsiCode.F_BRIGHT_GREEN,
    "bright_blue"    : AnsiCode.F_BRIGHT_BLUE,
    "bright_magenta" : AnsiCode.F_BRIGHT_MAGENTA,
    "bright_cyan"    : AnsiCode.F_BRIGHT_CYAN,
    "bright_white"   : AnsiCode.F_BRIGHT_WHITE,
}

NAME_TO_BGCOLOR: dict[str, AnsiCode] = {
    "black"          : AnsiCode.B_BLACK,
    "red"            : AnsiCode.B_RED,
    "yellow"         : AnsiCode.B_YELLOW,
    "green"          : AnsiCode.B_GREEN,
    "blue"           : AnsiCode.B_BLUE,
    "magenta"        : AnsiCode.B_MAGENTA,
    "cyan"           : AnsiCode.B_CYAN,
    "white"          : AnsiCode.B_WHITE,
    "bright_black"   : AnsiCode.B_BRIGHT_BLACK,
    "bright_red"     : AnsiCode.B_BRIGHT_RED,
    "bright_yellow"  : AnsiCode.B_BRIGHT_YELLOW,
    "bright_green"   : AnsiCode.B_BRIGHT_GREEN,
    "bright_blue"    : AnsiCode.B_BRIGHT_BLUE,
    "bright_magenta" : AnsiCode.B_BRIGHT_MAGENTA,
    "bright_cyan"    : AnsiCode.B_BRIGHT_CYAN,
    "bright_white"   : AnsiCode.B_BRIGHT_WHITE,
}


def decorate_with_ansi(display_text: str, style: Style|None = None) -> PrettyRenderedText:
    if style is None:
        return PrettyRenderedText(value=display_text)
    pre: list[AnsiCode] = []
    if style.bold:
        pre.append(AnsiCode.BOLD)
    if style.italic:
        pre.append(AnsiCode.ITALIC)
    if style.underline:
        pre.append(AnsiCode.UNDERLINE)
    # fg_color
    if style.fg_color:
        ansi = NAME_TO_FGCOLOR.get(style.fg_color, None)
        if ansi:
            pre.append(ansi)
    # bg_color
    if style.bg_color:
        ansi = NAME_TO_BGCOLOR.get(style.bg_color, None)
        if ansi:
            pre.append(ansi)

    if pre:
        deco = "".join([a.value for a in pre]) + display_text + AnsiCode.RESET.value
        return PrettyRenderedText(value=deco)
    return PrettyRenderedText(value=display_text)


# @dataclass
# class TableRenderedInfo:
#     target_table: Table
#     col_widths: dict[str, int]|None = None
#     table_width: int|None = None
#     default_separator: str|None = None
#     pre_rendered_rows: list[dict[str, Any]]|None = None

@dataclass
class PreRenderedTable:
    rows: list[PreRenderedRow]
    col_widths: dict[str, int]|None = None
    table_width: int|None = None
    default_separator: str|None = None
    source: Table|None = None

@dataclass
class PreRenderedRow:
    cell_mapping: dict[str, PreRenderedCell]
    style: Style|None
    source: RowRecord

@dataclass
class PreRenderedCell:
    pre_rendered_text: str
    style: Style|None


class PrettyRenderer(BaseRenderer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def render_value(self, raw_value: Any, style: Style|None = None) -> PrettyRenderedText:
        display_text = self.make_display_text(raw_value, style)
        return self.render_text(display_text, style)

    def render_text(self, display_text: str, style: Style|None = None) -> PrettyRenderedText:
        rendered = self._decorate_with_ansi(display_text, style)
        return rendered

    def render_table(self, table: Table) -> Sequence[PrettyRenderedText]:
        self._begin_render_table(table)
        rendered_lines = self._end_render_table(table)
        return rendered_lines
        

    def _begin_render_table(self, table: Table):
        pre_rendered_table = self._pre_render_table(table)

        assert pre_rendered_table.col_widths
        col_widths: dict[str, int] = pre_rendered_table.col_widths

        # store to context
        self.renderer_context.extra["pre_rendered_table"] = pre_rendered_table


    def _end_render_table(self, table: Table) -> Sequence[PrettyRenderedText]:
        """Final Rendering"""
        pre_rendered_table: PreRenderedTable = self.renderer_context.extra["pre_rendered_table"]

        assert pre_rendered_table.default_separator
        default_h_separator: str = pre_rendered_table.default_separator

        assert pre_rendered_table.col_widths
        col_widths: dict[str, int] = pre_rendered_table.col_widths

        assert pre_rendered_table.rows
        pre_rendered_rows: list[PreRenderedRow] = pre_rendered_table.rows
        rendered_lines: list[PrettyRenderedText] = []
        for pre_rendered_row in pre_rendered_rows:
            row: RowRecord = pre_rendered_row.source
            if row.row_type == RowType.SEPARATOR:
                rendered_lines.append(PrettyRenderedText(value=default_h_separator))
                continue
            pre_rendered_cell_mappings: dict[str, PreRenderedCell] = pre_rendered_row.cell_mapping
            rendered_cells_and_gaps: list[RenderedTextOrText] = []
            for i, col_key in enumerate(table.display_column_keys):
                is_last_cell = i == len(table.display_column_keys)-1
                col_width = col_widths[col_key]
                cell = pre_rendered_cell_mappings[col_key]
                if cell.style and cell.style.h_align == "right":
                    display_text = cell.pre_rendered_text.rjust(col_width)
                elif cell.style and cell.style.h_align == "center":
                    display_text = cell.pre_rendered_text.center(col_width)
                else:
                    display_text = cell.pre_rendered_text.ljust(col_width)
                decorated_text = self._decorate_with_ansi(display_text, cell.style)
                rendered_cells_and_gaps.append(decorated_text)
                if not is_last_cell:
                    gap = cell.style.gap_to_next if cell.style and cell.style.gap_to_next else "  "
                    if row.default_style:
                        gap = self._decorate_with_ansi(gap, row.default_style)
                    rendered_cells_and_gaps.append(gap)
            rendered_lines.append(
                PrettyRenderedText(value=
                    "".join([str(rt) for rt in rendered_cells_and_gaps])
                )
            )
        return rendered_lines


    def _determine_style(self, *styles: Style | None) -> Style | None:
        style = None
        for s in styles:
            if s is not None:
                if style is None:
                    style = s
                else:
                    style = style.merge(s)
        return style


    def _pre_render_table(self, table: Table) -> PreRenderedTable:
        # 1) collect used columns
        col_widths: dict[str, int] = {}
        for col_key in table.display_column_keys:
            if col_key in table.column_mapping:
                col_widths[col_key] = 0
        
        col_key_lst = list(col_widths.keys())
        # 2) pre render rows
        pre_rendered_rows: list[PreRenderedRow] = []
        row_index = 0
        for row in table.row_records:
            if row.row_type == RowType.NORMAL: # TODO consider DATA
                row_index += 1

            pre_rendered_row = self._pre_render_row(
                table,
                row,
                row_index,
                col_key_lst,
            )

            pre_rendered_rows.append(pre_rendered_row)

        # 3) calcuate col max widths
        for row in pre_rendered_rows:
            for col_key, cell in row.cell_mapping.items():
                text_len = self.calc_width(cell.pre_rendered_text)
                col_widths[col_key] = max(col_widths[col_key], text_len)

        table_width = self._calculate_table_width(
            table,
            col_widths
        )

        default_separator = "-" * table_width

        pre_rendered_table = PreRenderedTable(
            rows=pre_rendered_rows,
            col_widths=col_widths,
            table_width=table_width,
            default_separator=default_separator,
            source=table
        )
        return pre_rendered_table


    def _calculate_table_width(
            self,
            table: Table,
            col_widths: Mapping[str, int],
        ) -> int:

        # sum of display text lengths
        table_width = sum([
            col_widths.get(col_key, 0) for col_key in table.display_column_keys
        ])
        
        # plus gaps
        gaps = [
            table.column_mapping[col_key].default_style.gap_to_next or "  "
            for col_key in table.display_column_keys
        ]

        table_width += sum([self.calc_width(gap) for gap in gaps[:-1]])
        return table_width


    def _pre_render_row(
            self,
            table: Table,
            row: RowRecord,
            row_index1: int,
            col_key_lst: list[str],
        ) -> PreRenderedRow:

        row_style = row.default_style # TODO conditional style

        pre_rendered_cell_mapping: dict[str, PreRenderedCell] = {}
        for col_key in col_key_lst:
            column = table.column_mapping[col_key]
            col_style = column.default_style # TODO conditional style

            pre_rendered_cell = None
            if row.row_type == RowType.HEADER_KEY:
                style = self._determine_style(col_style, row_style)
                display_text = col_key
                pre_rendered_cell = PreRenderedCell(display_text, style)
            elif column.col_type == ColumnType.NORMAL:
                cellOrValue = row.cell_mapping.get(col_key, None) if row.cell_mapping else None
                pre_rendered_cell = self._pre_render_cell(
                    cellOrValue,
                    col_style,
                    row_style,
                )
            elif column.col_type == ColumnType.INDEX0:
                style = self._determine_style(col_style, row_style)
                display_text = str(row_index1-1) if row.row_type == RowType.NORMAL else col_key # TODO header
                pre_rendered_cell = PreRenderedCell(display_text, style)
            elif column.col_type == ColumnType.INDEX1:
                style = self._determine_style(col_style, row_style)
                display_text = str(row_index1) if row.row_type == RowType.NORMAL else col_key # TODO header
                pre_rendered_cell = PreRenderedCell(display_text, style)
            elif column.col_type == ColumnType.SEPARATOR:
                style = self._determine_style(col_style, row_style)
                display_text = style.v_separator if style and style.v_separator else "|"
                pre_rendered_cell = PreRenderedCell(display_text, style)
            else:
                raise NotImplementedError(f"unexpected column type : {column.col_type}")
            pre_rendered_cell_mapping[col_key] = pre_rendered_cell

        return PreRenderedRow(
            cell_mapping=pre_rendered_cell_mapping,
            style=row_style,
            source=row,
        )

    
    def _pre_render_cell(
            self,
            cellOrValue: CellOrValue,
            col_style: Style|None,
            row_style: Style|None,
        ) -> PreRenderedCell:

        if isinstance(cellOrValue, Cell):
            style = self._determine_style(cellOrValue.style, col_style, row_style) # TODO consider order
            display_text = self.make_display_text(cellOrValue.raw_value, style)
            width = self.calc_width(display_text)
        else:
            style = self._determine_style(col_style, row_style) # TODO consider order
            display_text = self.make_display_text(cellOrValue, style)
            width = self.calc_width(display_text)

        return PreRenderedCell(
            pre_rendered_text=display_text,
            style=style
        )


    def _decorate_with_ansi(self, display_text: str, style: Style|None = None) -> PrettyRenderedText:
        return decorate_with_ansi(display_text, style)

    