# cli_def/models/cli_def_node.py
from typing import Optional, Any, Iterator, Mapping, Callable, Iterable
from dataclasses import dataclass, field
import re

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


    def dump_tree(self) -> Iterable[str]:
        lines = []
        for node in self.iter_all_nodes():
            line = "  " * node.deflevel + node.key
            lines.append(line)
        return lines


# base class of CliDef and CommandDef
class ExecutableNode(CliDefNode):
    entrypoint: Optional[str] = None