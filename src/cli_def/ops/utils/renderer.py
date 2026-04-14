# cli_def/ops/utils/renderer.py
from __future__ import annotations

from typing import Protocol, Callable, Any, Sequence, Union
from dataclasses import dataclass, field
from enum import Enum, auto

import wcwidth
from wcwidth import wcswidth


@dataclass
class Style:
    DEFAULT_GAP = "  "
    DEFAULT_V_SEPARATOR = "|"
    DEFAULT_H_SEPARATOR = "-"
    DEFAULT_TRUNCATE_SYMBOL = "…"
    LAYOUT_TYPE_TRUNCATE = "truncate"
    LAYOUT_TYPE_WRAP = "wrap"

    h_align:   str|None  = None # right, left, center
    bold:      bool|None = None
    italic:    bool|None = None
    underline: bool|None = None
    fg_color:  str|None  = None
    bg_color:  str|None  = None

    prefix:    str|None  = None
    suffix:    str|None  = None

    v_separator:     str|None  = None # default "|"
    h_separator:     str|None  = None # default "-"
    gap_to_next:     str|None  = None # default "  "

    wrap_width:      int|None = None
    truncate_width:  int|None = None
    truncate_symbol: str|None = None # default "…"
    truncate_mode:   str|None = None # begin, middle, end

    min_width:       int|None = None
    max_width:       int|None = None
    layout_type:     str|None = None # wrap, truncate

    @property
    def has_variable_width(self) -> bool:
        if self.min_width is not None or self.max_width is not None:
            return self.min_width != self.max_width
        return False


    def make_display_text(self, text: str) -> str:
        if self.prefix:
            text = self.prefix + text
        if self.suffix:
            text = text + self.suffix
        if self.truncate_width and len(text) > self.truncate_width:
            symbol = self.truncate_symbol or self.DEFAULT_TRUNCATE_SYMBOL
            if self.truncate_mode == "begin":
                text = symbol + text[len(text) - self.truncate_width:]
            elif self.truncate_mode == "middle":
                len_take = self.truncate_width // 2
                text = text[:len_take] + symbol + text[-len_take:]
            else: # truncate_mode "end"
                text = text[:self.truncate_width] + symbol
        return text


    def merge(self, other: Style|None) -> Style:
        if other is None:
            return self
        return Style(
            h_align= self.h_align or other.h_align,
            bold= self.bold or other.bold,
            italic= self.italic or other.italic,
            underline= self.underline or other.underline,
            fg_color= self.fg_color or other.fg_color,
            bg_color= self.bg_color or other.bg_color,
            prefix= self.prefix or other.prefix,
            suffix= self.suffix or other.suffix,
            v_separator= self.v_separator or other.v_separator,
            h_separator= self.h_separator or other.h_separator,
            gap_to_next= self.gap_to_next or other.gap_to_next,
            wrap_width= self.wrap_width or other.wrap_width,
            truncate_width= self.truncate_width or other.truncate_width,
            truncate_symbol= self.truncate_symbol or other.truncate_symbol,
            truncate_mode= self.truncate_mode or other.truncate_mode,
            min_width= self.min_width or other.min_width,
            max_width= self.max_width or other.max_width,
            layout_type= self.layout_type or other.layout_type,
        )


class ConditinalStyle:
    cond: Callable[[Any], bool]
    style: Style


class ColumnType(Enum):
    NORMAL = auto()
    INDEX1 = auto()
    INDEX0 = auto()
    SEPARATOR = auto()


@dataclass
class Column:
    key: str
    col_type: ColumnType = ColumnType.NORMAL
    default_style: Style|None = None

    def __post_init__(self):
        if self.default_style is None:
            self.default_style = Style()


ColumnOrKey = Union[
    Column,
    str
]


@dataclass
class Cell:
    raw_value: Any
    style: Style|None = None


CellOrValue = Union[
    Cell,
    Any
]


class RowType(Enum):
    NORMAL = auto()
    TITLE = auto()
    SUBTITLE = auto()
    HEADER = auto()
    HEADER_KEY = auto()
    FOOTER = auto()
    SEPARATOR = auto()


@dataclass
class RowRecord:
    cell_mapping: dict[str, CellOrValue]|None = None
    row_type: RowType = RowType.NORMAL
    default_style: Style|None = None
    source: Any|None = None

    def get_raw_value(self, key: str, default: Any|None = None) -> Any|None:
        if self.cell_mapping is None:
            return None
        cellOrValue = self.cell_mapping.get(key, default)
        if isinstance(cellOrValue, Cell):
            return cellOrValue.raw_value
        return cellOrValue


@dataclass
class Table:
    column_mapping: dict[str, Column]
    row_records: list[RowRecord]
    display_column_keys: list[str]
    header_mapping: dict[str, CellOrValue]|None = None
    footer_mapping: dict[str, CellOrValue]|None = None


@dataclass
class RendererContext:
    extra: dict[str, Any] = field(default_factory=dict)


class RenderedObject(Protocol):
    pass


class RendererProtocol(Protocol):
    def render_value(self, raw_value: Any, style: Style|None = None) -> RenderedObject:
        ...
    def render_text(self, display_text: str, style: Style|None = None) -> RenderedObject:
        ...
    def render_table(self, table: Table) -> Sequence[RenderedObject]:
        ...



# abstract Renderer class
class BaseRenderer(RendererProtocol):

    def __init__(self, *,
                 ctx: RendererContext|None = None,
                 value_formatter: Callable[[Any], str]|None = None,
        ):
        self.renderer_context: RendererContext = ctx or RendererContext()
        self.value_formatter: Callable[[Any], str]| None = value_formatter


    def make_display_text(self, raw_value: Any, style: Style|None = None):
        if self.value_formatter:
            display_text = self.value_formatter(raw_value)
        else:
            display_text = str(raw_value)
        if style:
            return style.make_display_text(display_text)
        return display_text


    def calc_width(self, display_text: str) -> int:
        return max(wcswidth(display_text), 0) # treat wcswidhth returns < 0


    def wrap(self, display_text: str, width: int) -> list[str]:
        return wcwidth.wrap(display_text, width)