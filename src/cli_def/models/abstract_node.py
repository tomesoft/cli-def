# cli_def/models/cli_def_node.py
from __future__ import annotations
from typing import Optional, Any, Iterator, Mapping, Callable, Iterable, Sequence
from dataclasses import dataclass, field
import re

# --------------------------------------------------------------------------------
# CliDefNode class
# base class of any CliDef node
# --------------------------------------------------------------------------------
@dataclass
class CliDefNode:
    key: str
    parent: CliDefNode|None = None
    extra_defs: dict[str, Any] = field(default_factory=dict)
    source: CliDefNode|None = None # set by resolver

    @property
    def defpath(self) -> str:
        if self.parent is not None:
            return "/".join([self.parent.defpath, self.key])
        else:
            return "/" + self.key
    
    @property
    def deflevel(self) -> int:
        if self.parent is not None:
            return self.parent.deflevel + 1
        else:
            return 0

    def iter_all_nodes(self) -> Iterator[CliDefNode]:
        yield self
        for child in self.iter_children():
            yield from child.iter_all_nodes()


    def iter_children(self):
        return iter([])


    def find(self, path: str) -> CliDefNode|None:
        for node in self.iter_all_nodes():
            if node.defpath == path:
                return node
        return None


    def select_first(self, pred: Callable[[CliDefNode], Any]) -> CliDefNode|None:
        for node in self.iter_all_nodes():
            if pred(node):
                return node


    def select_all(self, pred: Callable[[CliDefNode], Any]) -> Iterable[CliDefNode]:
        selected = []
        for node in self.iter_all_nodes():
            if pred(node):
                selected.append(node)
        return selected


    # detail version moved to ops
    def dump_tree(self) -> Sequence[Sequence[str]]:
        col_keys = ("key", "cls")
        rows = []
        rows.append(col_keys)
        for node in self.iter_all_nodes():
            cells = []
            for col in col_keys:
                if col == "key":
                    cell = "  " * node.deflevel + (node.key or "")
                elif col == "cls":
                    cell = type(node).__name__
                else:
                    cell = getattr(node, col, None)
                cells.append(cell)
            rows.append(cells)
        return rows


    def merge_missing_from(self, other: CliDefNode):
        for k, v in other.extra_defs:
            self.extra_defs.setdefault(k, v)


    def override_with(self, other: CliDefNode):
        self.extra_defs.update(other.extra_defs)


# --------------------------------------------------------------------------------
# ExecutableNode
# base class of CliDef and CommandDef
# --------------------------------------------------------------------------------
class ExecutableNode(CliDefNode):
    entrypoint: str|None = None
    group: str|None = None
    bind: dict[str, Any]|None = None # for parameter binding


    def merge_missing_from(self, other: ExecutableNode):
        super().merge_missing_from(other)
        if self.entrypoint is None:
            self.entrypoint = other.entrypoint
        if self.group is None:
            self.group = other.group
        if self.bind is None:
            if other.bind is not None:
                self.bind = dict(other.bind)
        else:
            if other.bind is not None:
                for k, v in other.bind.items():
                    self.bind.setdefault(k, v)


    def override_with(self, other: ExecutableNode):
        super().override_with(other)
        if other.entrypoint is not None:
            self.entrypoint = other.entrypoint
        if other.group is not None:
            self.group = other.group
        if other.bind is not None:
            if self.bind is None:
                self.bind = dict(other.bind)
            else:
                self.bind.update(other.bind)
