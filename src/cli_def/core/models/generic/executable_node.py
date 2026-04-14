# cli_def/core/models/raw/cli_def_node.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, TypeVar, Generic

from ..protocols import ExecutableNodeProtocol, TNode_co
from .abstract_node import AbstractCliDefNode
from .argument_def import AbstractArgumentDef


TArgDef = TypeVar("TArgDef", bound="AbstractArgumentDef")
# --------------------------------------------------------------------------------
# AbstractExecutableNode abstract class
# common base class of CliDef and CommandDef
# --------------------------------------------------------------------------------
class AbstractExecutableNode(
    AbstractCliDefNode[TNode_co],
    ExecutableNodeProtocol[TArgDef],
    Generic[TArgDef, TNode_co],
    ):

    _KNOWN_FIELDS = frozenset(
        AbstractCliDefNode._KNOWN_FIELDS | {
        "entrypoint",
        "group",
    })

    def __init__(
            self,
            key: str,
            *,
            help: str|None = None,
            parent: TNode_co|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            arguments: Iterable[TArgDef]|None = None,
            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(key, help=help, parent=parent, extra_defs=extra_defs)
        self._entrypoint: str|None = entrypoint
        self._group: str|None = group
        self._arguments: list[TArgDef] = list(arguments) if arguments else []

    @property
    def entrypoint(self) -> str|None:
        return self._entrypoint

    @property
    def group(self) -> str|None:
        return self._group

    @property
    def arguments(self) -> Sequence[TArgDef]:
        return self._arguments


    def iter_children(self) -> Iterator[TNode_co]:
        yield from self._arguments or []