# cli_def/ops/utils/renderer_ops.py
from __future__ import annotations

from typing import Mapping, Any, Sequence, Callable, Iterable, Union


from .renderer import (
    Style,
    Column,
    ColumnType,
    RowType,
    RowRecord,
    Table,
    CellOrValue,
    ColumnOrKey,
    RowConditionalStyle,
    Cell,
)


class TableBuilder:

    @classmethod
    def from_row_records(
        cls,
        columns: Iterable[ColumnOrKey],
        row_records: Iterable[RowRecord],
        *,
        display_column_keys: Iterable[str]|None = None,
        headers: Iterable[CellOrValue]|None = None,
        footers: Iterable[CellOrValue]|None = None,
        row_conditional_styles: Iterable[RowConditionalStyle]|None = None,
    ) -> Table:

        columns = cls.normalize_columns(columns)
        column_mapping = {
            col.key: col for col in columns
        }
        if display_column_keys is None:
            display_column_keys = [col.key for col in columns]
        else:
            display_column_keys = list(display_column_keys)

        if headers:
            header_mapping = {
                col.key: v for col, v in zip(columns, headers)
            }
        else:
            header_mapping = None

        if footers:
            footer_mapping = {
                col.key: v for col, v in zip(columns, footers)
            }
        else:
            footer_mapping = None


        result = Table(
            column_mapping=column_mapping,
            row_records=list(row_records),
            display_column_keys=display_column_keys,
            header_mapping=header_mapping,
            footer_mapping=footer_mapping,
            row_conditional_styles=list(row_conditional_styles) if row_conditional_styles is not None else None
        )
        return result


    @classmethod
    def from_columns_and_values(
        cls,
        columns: Iterable[ColumnOrKey],
        valuess: Iterable[Iterable[CellOrValue]],
        *,
        display_column_keys: Iterable[str]|None = None,
        headers: Iterable[CellOrValue]|None = None,
        footers: Iterable[CellOrValue]|None = None,
        row_conditional_styles: Iterable[RowConditionalStyle]|None = None,
        header_compositions: Iterable[RowType] | None = None,
        footer_compositions: Iterable[RowType] | None = None,
    ) -> Table:
        columns = cls.normalize_columns(columns)
        column_mapping = {
            col.key: col for col in columns
        }
        if display_column_keys is None:
            display_column_keys = [col.key for col in columns]
        else:
            display_column_keys = list(display_column_keys)

        if headers:
            header_mapping = {
                col.key: v for col, v in zip(columns, headers)
            }
        else:
            header_mapping = None

        if footers:
            footer_mapping = {
                col.key: v for col, v in zip(columns, footers)
            }
        else:
            footer_mapping = None
        
        if header_compositions is None:
            header_compositions = [RowType.HEADER, RowType.SEPARATOR]
        if footer_compositions is None:
            footer_compositions = []

        normal_column_keys = [col.key for col in columns if col.col_type == ColumnType.NORMAL]
        rows: list[RowRecord] = []
        for h in header_compositions:
            rows.append(RowRecord(row_type=h))
        for values in valuess:
            row = cls.make_row(normal_column_keys, values)
            rows.append(row)
        for f in footer_compositions:
            rows.append(RowRecord(row_type=f))

        result = Table(
            column_mapping=column_mapping,
            row_records=rows,
            display_column_keys=display_column_keys,
            header_mapping=header_mapping,
            footer_mapping=footer_mapping,
            row_conditional_styles=list(row_conditional_styles) if row_conditional_styles is not None else None
        )
        return result


    @classmethod
    def normalize_columns(cls, columns: Iterable[ColumnOrKey]) -> Sequence[Column]:
        normalized: list[Column] = []
        for col in columns:
            if isinstance(col, Column):
                normalized.append(col)
            else:
                normalized.append(
                    cls.make_column(col)
                )
        return normalized


    @classmethod
    def make_column(cls, col_key: str, default_style: Style|None = None) -> Column:
        if col_key == "#":
            default_style = Style(h_align="right").merge(default_style)
            return Column(col_key, col_type=ColumnType.INDEX1, default_style=default_style)
        if col_key == "#0":
            default_style = Style(h_align="right").merge(default_style)
            return Column(col_key, col_type=ColumnType.INDEX0, default_style=default_style)
        if col_key == "|":
            return Column(col_key, col_type=ColumnType.SEPARATOR, default_style=default_style)
        return Column(col_key, col_type=ColumnType.NORMAL, default_style=default_style)
        

    @classmethod
    def make_row(
        cls,
        col_keys: Iterable[str],
        values: Iterable[CellOrValue],
        *,
        fillValue: CellOrValue|None = None,
        default_style: Style|None = None,
    ) -> RowRecord:

        col_keys = list(col_keys)
        values = list(values)

        assert len(values) > 0
        if values[0] == "---":
            return RowRecord(row_type=RowType.SEPARATOR, default_style=default_style)

        cell_mapping: dict[str, CellOrValue] = {}
        for i, col_key in enumerate(col_keys):
            if i < len(values):
                cellOrValue = values[i]
            else:
                cellOrValue = fillValue
            cell_mapping[col_key] = cellOrValue
        return RowRecord(
            cell_mapping=cell_mapping,
            default_style=default_style
        )

