# cli_def/core/models/resolved/resolved_node.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, Tuple
from typing import Self, Generic, TypeVar

from cli_def.core.models.protocols import CliDefNodeProtocol

from .resolved_protocols import (
    ResolvedCliDefNodeProtocol,
)
from ..raw.raw_node import CliDefNode

#TNode = TypeVar("TNode", bound="AbstractCliDefNode")

# --------------------------------------------------------------------------------
# AbstractCliDefNode abstract class
# base class of any CliDef node
# --------------------------------------------------------------------------------
class ResolvedCliDefNode(
    ResolvedCliDefNodeProtocol,
    #TreeViewProtocol[TNode_co],
    ):

    _KNOWN_FIELDS = frozenset({
        "key",
        "help",
    })

    def __init__(
            self,
            key: str,
            *,
            definition: CliDefNode,
            help: str|None = None,
            parent: ResolvedCliDefNode|None = None,
            extra_defs: Mapping[str, Any]|None = None,
        ):
        self._key: str = key
        self._help: str|None = help
        self._parent: ResolvedCliDefNode|None = parent
        self._extra_defs: dict[str, Any] = dict(extra_defs) if extra_defs else {}
        self._definition: CliDefNode = definition

    @property
    def key(self) -> str:
        return self._key

    @property
    def help(self) -> str|None:
        return self._help

    @property
    def parent(self) -> ResolvedCliDefNode|None:
        return self._parent

    @property
    def definition(self) -> CliDefNode:
        return self._definition

    @property
    def extra_defs(self) -> Mapping[str, Any]:
        return self._extra_defs

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

    @property
    def is_leaf(self) -> bool:
        return not any(True for _ in self.iter_children())
        


    def iter_all_nodes(self) -> Iterator[ResolvedCliDefNode]:
        yield self
        for child in self.iter_children():
            yield from child.iter_all_nodes()


    def iter_children(self) -> Iterator[ResolvedCliDefNode]:
        return iter(())


    def find_by_defpath(self, path: str) -> ResolvedCliDefNode|None:
        return self.select_first(
            lambda n: n.defpath == path
        )


    def select_first(
            self,
            pred: Callable[[ResolvedCliDefNode], Any]
        ) -> ResolvedCliDefNode|None:
        for node in self.iter_all_nodes():
            if pred(node):
                return node
        return None


    def select_all(
            self,
            pred: Callable[[ResolvedCliDefNode], Any]
        ) -> Iterable[ResolvedCliDefNode]:
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


    @classmethod
    def split_mapping(
        cls,
        mapping: Mapping[str, Any]
        ) -> Tuple[Mapping[str, Any], Mapping[str, Any]]:
        known = {}
        extra = {}
        for k, v in mapping.items():
            if k in cls._KNOWN_FIELDS:
                known[k] = v
            else:
                extra[k] = v
        return known, extra
