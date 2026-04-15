# cli_def/ops/utils/pretty_renderer.py
from __future__ import annotations

from typing import Protocol, Callable, Any, Sequence, Tuple, Mapping, Union
from enum import Enum
from dataclasses import dataclass
import logging

import shutil

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
        decorated = (
            "".join([a.value for a in pre])
            + display_text
            + AnsiCode.RESET.value
        )
        return PrettyRenderedText(value=decorated)
    return PrettyRenderedText(value=display_text)


def get_terminal_width(default: int=80) -> int:
    return shutil.get_terminal_size(fallback=(default, 24)).columns

# --------------------------------------------------------------------------------
#
# Pre-rendered Objects
#
# --------------------------------------------------------------------------------
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
    pre_rendered_segs: list[str]
    style: Style|None



# --------------------------------------------------------------------------------
#
# Pretty Renderer
#
# --------------------------------------------------------------------------------
class PrettyRenderer(BaseRenderer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_terminal_width: bool = True


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
        if self.use_terminal_width:
            terminal_width = get_terminal_width()
            logging.info(f"@@@ terminal_width = {terminal_width}")
        pre_rendered_table = self._pre_render_table(table, terminal_width)

        logging.info(f"@@@ pre_rendered_table_width = {pre_rendered_table.table_width}")
        assert pre_rendered_table.col_widths

        # store to context
        self.renderer_context.extra["pre_rendered_table"] = pre_rendered_table


    def _end_render_table(self, table: Table) -> Sequence[PrettyRenderedText]:
        return self._post_render_table(table)


    def _determine_style(self, *styles: Style | None) -> Style | None:
        style = None
        for s in styles:
            if s is not None:
                if style is None:
                    style = s
                else:
                    style = style.merge(s)
        return style


    def _calc_cell_width(self, cell: PreRenderedCell) -> int:
        if cell.pre_rendered_segs:
            return max([self.calc_width(seg) for seg in cell.pre_rendered_segs])
        return 0


    # --------------------------------------------------------------------------------
    # Pre Rendering
    # --------------------------------------------------------------------------------
    def _pre_render_table(self, table: Table, layout_width: int|None = None) -> PreRenderedTable:

        # 1) collect used columns
        fixed_width_col_key_lst: list[str] = []
        variable_width_col_key_lst: list[str] = []
        col_widths: dict[str, int] = {}
        for col_key in table.display_column_keys:
            if col_key in table.column_mapping:
                col_widths[col_key] = 0
                col_style = table.column_mapping[col_key].default_style
                if col_style and col_style.has_variable_width:
                    variable_width_col_key_lst.append(col_key)
                else:
                    fixed_width_col_key_lst.append(col_key)

        
        col_key_lst = (
            fixed_width_col_key_lst if layout_width is not None
            else [k for k in col_widths.keys()]
        )
        # 2) pre render rows part of fixed width columns
        pre_rendered_rows: list[PreRenderedRow] = self._pre_render_rows(
            table,
            col_key_lst
        )

        # 3) calcuate col max widths
        for row in pre_rendered_rows:
            for col_key, cell in row.cell_mapping.items():
                text_len = self._calc_cell_width(cell)
                col_widths[col_key] = max(col_widths[col_key], text_len)

        tmp_table_width = self._calculate_table_width(
            table,
            col_widths
        )

        # 4) layout variable part
        if variable_width_col_key_lst and layout_width is not None:
            logging.debug("@@@@ Variable Layout @@@@")
            remaining_width = layout_width - tmp_table_width
            # 4.1) layout with remaining width
            pre_rendered_rows_variable_cols: list[PreRenderedRow] = self._pre_render_rows(
                table,
                variable_width_col_key_lst,
                layout_width=remaining_width
            )
            # 4.2) merge PreRenderedRows
            for r1, r2 in zip(pre_rendered_rows, pre_rendered_rows_variable_cols):
                assert r1.source == r2.source
                r1.cell_mapping.update(r2.cell_mapping)

            # 4.3) recalculate table_width
            for row in pre_rendered_rows_variable_cols:
                for col_key, cell in row.cell_mapping.items():
                    text_len = self._calc_cell_width(cell)
                    col_widths[col_key] = max(col_widths[col_key], text_len)

            table_width = self._calculate_table_width(
                table,
                col_widths
            )

        else:
            logging.debug("@@@@ Fixed Layout @@@@")
            table_width = tmp_table_width


        default_separator = Style.DEFAULT_H_SEPARATOR * table_width

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

        text_widths: list[int] = []
        gaps: list[str] = []
        for col_key in table.display_column_keys:
            text_widths.append(col_widths[col_key])
            style = table.column_mapping[col_key].default_style
            gaps.append(
                style.gap_to_next
                if style and style.gap_to_next is not None
                else Style.DEFAULT_GAP
            )

        # text widths plus gaps
        table_width = (
            sum(text_widths) +
            sum([self.calc_width(gap) for gap in gaps[:-1]])
        )
        return table_width


    def _pre_render_rows(
            self,
            table: Table,
            col_key_lst: list[str],
            *,
            layout_width: int|None = None
        ) -> list[PreRenderedRow]:
        pre_rendered_rows = []
        row_index = 0
        for row in table.row_records:
            if row.row_type == RowType.NORMAL: # TODO consider DATA
                row_index += 1

            pre_rendered_row = self._pre_render_row(
                table,
                row,
                row_index,
                col_key_lst,
                layout_width=layout_width,
            )

            pre_rendered_rows.append(pre_rendered_row)
        return pre_rendered_rows

    def _calculate_layout_col_widths(
            self,
            table: Table,
            layout_width: int,
            variable_col_key_lst: list[str],
            default_min_width: int = 10,
            default_max_width: int|None = None,
        ) -> dict[str, int]:

        col_width_range_map: dict[str, Tuple[int, int|None]] = {}
        total_gap_width = 0

        # 1) collect width range
        for col_key in variable_col_key_lst:
            col_style = table.column_mapping[col_key].default_style
            if col_style:
                col_width_range_map[col_key] = (
                    col_style.min_width or default_min_width,
                    col_style.max_width or default_max_width
                )
                total_gap_width += self.calc_width(col_style.gap_to_next or Style.DEFAULT_GAP)
            else:
                col_width_range_map[col_key] = (default_min_width, default_max_width)
                total_gap_width += self.calc_width(Style.DEFAULT_GAP)

        # 2) calculate total min widths
        total_min_width = sum([min for min, _ in col_width_range_map.values()])

        remaining_width = layout_width - total_gap_width

        if remaining_width <= total_min_width:
            return {k: v[0] for k, v in col_width_range_map.items()}

        # 3) calculate ratio
        ratio_map: dict[str, float] = {
            k: v[0]/total_min_width for k, v in col_width_range_map.items()
        }

        # 4) calculate rough width
        rough_width_map = {
            k: int(v[0] * remaining_width) for k, v in col_width_range_map.items()
        }

        # 5) fix width
        resolved_width_map: dict[str, int] = {}
        free_width_col_keys = []
        for k, (_, maxw) in col_width_range_map.items():
            if maxw is None:
                free_width_col_keys.append(k)
                continue
            resolved_width = min(rough_width_map[k], maxw)
            resolved_width_map[k] = resolved_width
            remaining_width -= resolved_width

        if len(free_width_col_keys) == 0:
            return  resolved_width_map
        elif len(free_width_col_keys) == 1:
            resolved_width_map[free_width_col_keys[0]] = remaining_width
            return resolved_width_map
        
        # TODO multiple free width columns layout
        raise NotImplementedError("multiple free width columns layout not implemented")


    def _pre_render_row(
            self,
            table: Table,
            row: RowRecord,
            row_index1: int,
            col_key_lst: list[str],
            *,
            layout_width: int|None = None,
        ) -> PreRenderedRow:

        if layout_width:
            logging.debug(f"@@@ row layout width = {layout_width}")
            layout_col_width_map = self._calculate_layout_col_widths(
                table, layout_width, col_key_lst
            )
        else:
            layout_col_width_map = {}

        row_style = row.default_style
        # evaluate row conditional styles
        row_primary_style = None
        if table.row_conditional_styles:
            row_conditional_styles: list[Style] = []
            for cs in table.row_conditional_styles:
                if cs.cond(row):
                    row_conditional_styles.append(cs.style)
            row_primary_style = self._determine_style(*row_conditional_styles)
            

        pre_rendered_cell_mapping: dict[str, PreRenderedCell] = {}
        for col_key in col_key_lst:
            column = table.column_mapping[col_key]
            col_style = column.default_style # TODO conditional style

            pre_rendered_cell = None
            if row.row_type == RowType.HEADER:
                if table.header_mapping:
                    cellOrValue = table.header_mapping.get(col_key, "")
                    pre_rendered_cell = self._pre_render_cell(
                        cellOrValue,
                        col_style,
                        row_style,
                        layout_width=layout_col_width_map.get(col_key, None),
                        row_primary_style=row_primary_style,
                    )
                else:
                    style = self._determine_style(
                        row_primary_style,
                        col_style,
                        row_style
                    )
                    display_text = col_key
                    pre_rendered_cell = PreRenderedCell([display_text], style)
            elif row.row_type == RowType.HEADER_KEY:
                style = self._determine_style(
                    row_primary_style,
                    col_style,
                    row_style
                )
                display_text = col_key
                pre_rendered_cell = PreRenderedCell([display_text], style)
            elif row.row_type == RowType.FOOTER:
                if table.footer_mapping:
                    cellOrValue = table.footer_mapping.get(col_key, "")
                    pre_rendered_cell = self._pre_render_cell(
                        cellOrValue,
                        col_style,
                        row_style,
                        layout_width=layout_col_width_map.get(col_key, None),
                        row_primary_style=row_primary_style,
                    )
                else:
                    style = self._determine_style(
                        row_primary_style,
                        col_style, row_style
                    )
                    display_text = "" # TODO consider default footer value
                    pre_rendered_cell = PreRenderedCell([display_text], style)
            elif column.col_type == ColumnType.NORMAL:
                cellOrValue = row.cell_mapping.get(col_key, None) if row.cell_mapping else None
                pre_rendered_cell = self._pre_render_cell(
                    cellOrValue,
                    col_style,
                    row_style,
                    layout_width=layout_col_width_map.get(col_key, None),
                    row_primary_style=row_primary_style,
                )
            elif column.col_type == ColumnType.INDEX0:
                style = self._determine_style(
                    row_primary_style,
                    col_style,
                    row_style
                )
                display_text = str(row_index1-1) if row.row_type == RowType.NORMAL else col_key # TODO header
                pre_rendered_cell = PreRenderedCell([display_text], style)
            elif column.col_type == ColumnType.INDEX1:
                style = self._determine_style(
                    row_primary_style,
                    col_style,
                    row_style
                )
                display_text = str(row_index1) if row.row_type == RowType.NORMAL else col_key # TODO header
                pre_rendered_cell = PreRenderedCell([display_text], style)
            elif column.col_type == ColumnType.SEPARATOR:
                style = self._determine_style(
                    row_primary_style,
                    col_style,
                    row_style
                )
                display_text = (
                    style.v_separator
                    if style and style.v_separator
                    else Style.DEFAULT_V_SEPARATOR
                )
                pre_rendered_cell = PreRenderedCell([display_text], style)
            else:
                raise NotImplementedError(f"unexpected column type : {column.col_type}")
            pre_rendered_cell_mapping[col_key] = pre_rendered_cell

        return PreRenderedRow(
            cell_mapping=pre_rendered_cell_mapping,
            style=self._determine_style(row_primary_style, row_style),
            source=row,
        )

    
    def _pre_render_cell(
            self,
            cellOrValue: CellOrValue,
            col_style: Style|None,
            row_style: Style|None,
            *,
            layout_width: int|None = None,
            row_primary_style: Style|None,
        ) -> PreRenderedCell:

        if isinstance(cellOrValue, Cell):
            style = self._determine_style(
                row_primary_style,
                cellOrValue.style,
                col_style,
                row_style
            ) # TODO consider order
            display_text = self.make_display_text(cellOrValue.raw_value, style)
        else:
            style = self._determine_style(
                row_primary_style,
                col_style,
                row_style
            ) # TODO consider order
            display_text = self.make_display_text(cellOrValue, style)
        
        if layout_width:
            logging.debug(f"@@@ cell layout width = {layout_width}")
            if style and style.layout_type == Style.LAYOUT_TYPE_TRUNCATE:
                raise NotImplementedError("layout_type TRUNCATE not implemented")
            else:
                pre_rendered_segs = self.wrap(display_text, layout_width)
        else:
            if style and style.wrap_width and style.wrap_width > 0:
                pre_rendered_segs = self.wrap(display_text, style.wrap_width)
            else:
                pre_rendered_segs = [display_text]

        return PreRenderedCell(
            pre_rendered_segs=pre_rendered_segs,
            style=style
        )


    # --------------------------------------------------------------------------------
    # Post Rendering
    # --------------------------------------------------------------------------------
    def _post_render_table(self, table: Table) -> Sequence[PrettyRenderedText]:
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

            rendered_lines.extend(
                self._post_render_row(table, pre_rendered_row, col_widths)
            )
        return rendered_lines


    def _post_render_row(
            self,
            table: Table,
            pre_rendered_row: PreRenderedRow,
            col_widths: Mapping[str, int],
        ) -> Sequence[PrettyRenderedText]:

        row: RowRecord = pre_rendered_row.source
        rendered_lines: list[PrettyRenderedText] = []

        pre_rendered_cell_mappings: dict[str, PreRenderedCell] = pre_rendered_row.cell_mapping

        # 1) determine required sub rows
        required_sub_rows = max([
            len(cell.pre_rendered_segs)
            for _, cell in pre_rendered_row.cell_mapping.items()
        ])

        # 2) render each sub row
        sub_row_index = 0
        while sub_row_index < required_sub_rows:
            rendered_cells_and_gaps: list[RenderedTextOrText] = []
            for i, col_key in enumerate(table.display_column_keys):
                is_last_cell = i == len(table.display_column_keys)-1
                column = table.column_mapping[col_key]
                col_width = col_widths[col_key]
                cell = pre_rendered_cell_mappings[col_key]

                decorated_text = self._post_render_cell(
                    cell,
                    column,
                    col_width,
                    sub_row_index,
                )

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

            sub_row_index += 1

        return rendered_lines


    def _post_render_cell(
            self,
            cell: PreRenderedCell,
            column: Column,
            col_width: int,
            sub_index: int,
        ) -> PrettyRenderedText:
        if sub_index < len(cell.pre_rendered_segs):
            if cell.style and cell.style.h_align == "right":
                display_text = cell.pre_rendered_segs[sub_index].rjust(col_width)
            elif cell.style and cell.style.h_align == "center":
                display_text = cell.pre_rendered_segs[sub_index].center(col_width)
            else:
                display_text = cell.pre_rendered_segs[sub_index].ljust(col_width)
        else:
            if column.col_type == ColumnType.SEPARATOR:
                display_text = cell.pre_rendered_segs[0] # from [0] to get pre-rendered separator
                remain = col_width - len(display_text)
                if remain:
                    display_text += " " * remain
            else:
                # fill with space
                display_text = " " * col_width
        decorated_text = self._decorate_with_ansi(display_text, cell.style)

        return decorated_text


    def _decorate_with_ansi(
            self,
            display_text: str,
            style: Style|None = None
        ) -> PrettyRenderedText:
        return decorate_with_ansi(display_text, style)

