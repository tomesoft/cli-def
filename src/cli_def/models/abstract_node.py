# cli_def/models/cli_def_node.py
from typing import Optional, Any, Iterator, Mapping, Callable, Iterable, Sequence
from dataclasses import dataclass, field
import re

# --------------------------------------------------------------------------------
# CliDefNode class
# base class of any CliDef node
# --------------------------------------------------------------------------------
@dataclass
class CliDefNode:
    key: str = None
    parent: Optional["CliDefNode"] = None
    extra_defs: dict[str, Any] = field(default_factory=dict)

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

    def iter_all_nodes(self) -> Iterator["CliDefNode"]:
        yield self
        for child in self.iter_children():
            yield from child.iter_all_nodes()


    def iter_children(self):
        return iter([])


    def find(self, path: str) -> "CliDefNode"|None:
        for node in self.iter_all_nodes():
            if node.defpath == path:
                return node
        return None


    def select_first(self, pred: Callable[["CliDefNode"], Any]) -> "CliDefNode" | None:
        for node in self.iter_all_nodes():
            if pred(node):
                return node


    def select_all(self, pred: Callable[["CliDefNode"], Any]) -> Iterable["CliDefNode"]:
        selected = []
        for node in self.iter_all_nodes():
            if pred(node):
                selected.append(node)
        return selected

    def to_short_cls(self, type) -> str:
        if type.__name__ == "CommandDef":
            return "cmd"
        if type.__name__ == "ArgumentDef":
            return "arg"
        if type.__name__ == "CliDef":
            return "cli"
        return "unk"

    def dump_tree(self, *, details:bool=False) -> Sequence[Sequence[str]]:
        col_keys = ("key", "cls", "option", "is_flag", "help")
        rows = []
        rows.append(col_keys)
        for node in self.iter_all_nodes():
            cells = []
            for col in col_keys:
                if col == "key":
                    cell = "  " * node.deflevel + node.key
                elif col == "cls":
                    cell = self.to_short_cls(type(node))
                else:
                    cell = getattr(node, col, None)
                cells.append(cell)
            rows.append(cells)
        return rows


# --------------------------------------------------------------------------------
# ExecutableNode
# base class of CliDef and CommandDef
# --------------------------------------------------------------------------------
class ExecutableNode(CliDefNode):
    entrypoint: Optional[str] = None