# cli_def/core/models/raw/executable_node.py
from __future__ import annotations
from typing import Any, Iterator, Mapping, Callable, Iterable, Sequence, TypeVar, Generic

from .raw_node import CliDefNode
from .raw_protocols import RawExecutableNodeProtocol
from .argument_def import ArgumentDef


# --------------------------------------------------------------------------------
# ExecutableNode abstract class
# common base class of CliDef and CommandDef of raw model
# --------------------------------------------------------------------------------
class ExecutableNode(
    CliDefNode,
    RawExecutableNodeProtocol,
    ):

    _KNOWN_FIELDS = frozenset(
        CliDefNode._KNOWN_FIELDS | {
        "entrypoint",
        "group",
        "bind",
    })

    def __init__(
            self,
            key: str,
            *,
            help: str|None = None,
            parent: CliDefNode|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            arguments: Iterable[ArgumentDef]|None = None,
            bind: Mapping[str, Any]|None = None, # for parameter binding
            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(key, help=help, parent=parent, extra_defs=extra_defs)
        self._entrypoint: str|None = entrypoint
        self._group: str|None = group
        self._arguments: list[ArgumentDef] = list(arguments) if arguments else []
        self._bind: dict[str, Any] = dict(bind) if bind else {}

    @property
    def entrypoint(self) -> str|None:
        return self._entrypoint

    @property
    def group(self) -> str|None:
        return self._group

    @property
    def arguments(self) -> Sequence[ArgumentDef]:
        return self._arguments

    @property
    def bind(self) -> Mapping[str, Any]:
        return self._bind

    def iter_children(self) -> Iterator[CliDefNode]:
        yield from self._arguments or []
