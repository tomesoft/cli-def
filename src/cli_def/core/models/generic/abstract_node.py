# cli_def/core/models/generic/cli_def_node.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, Tuple
from typing import Self, Generic, TypeVar

from ..protocols import (
    CliDefNodeProtocol,
    # TreeViewProtocol,
    TNode_co,
)

#TNode = TypeVar("TNode", bound="AbstractCliDefNode")

# --------------------------------------------------------------------------------
# AbstractCliDefNode abstract class
# base class of any CliDef node
# --------------------------------------------------------------------------------
class AbstractCliDefNode(
    CliDefNodeProtocol,
    #TreeViewProtocol[TNode_co],
    Generic[TNode_co]
    ):

    _KNOWN_FIELDS = frozenset({
        "key",
        "help",
    })

    def __init__(
            self,
            key: str,
            *,
            help: str|None = None,
            parent: TNode_co|None = None,
            extra_defs: Mapping[str, Any]|None = None,
        ):
        self._key: str = key
        self._help: str|None = help
        self._parent: TNode_co|None = parent
        self._extra_defs: dict[str, Any] = dict(extra_defs) if extra_defs else {}

    @property
    def key(self) -> str:
        return self._key

    @property
    def help(self) -> str|None:
        return self._help

    @property
    def parent(self) -> TNode_co|None:
        return self._parent

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
        


    def iter_all_nodes(self) -> Iterator[TNode_co]:
        yield self
        for child in self.iter_children():
            yield from child.iter_all_nodes()


    def iter_children(self) -> Iterator[TNode_co]:
        return iter(())


    def find_by_defpath(self, path: str) -> TNode_co|None:
        return self.select_first(
            lambda n: n.defpath == path
        )


    def select_first(
            self,
            pred: Callable[[TNode_co], Any]
        ) -> TNode_co|None:
        for node in self.iter_all_nodes():
            if pred(node):
                return node
        return None


    def select_all(
            self,
            pred: Callable[[TNode_co], Any]
        ) -> Iterable[TNode_co]:
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
