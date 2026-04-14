# cli_def/model.py
from __future__ import annotations
from typing import Sequence, Mapping, Any, Iterable, Iterator, TypeVar, Generic

from ..protocols import CliDefProtocol
from .abstract_node import AbstractCliDefNode, TNode_co
from .executable_node import AbstractExecutableNode, TArgDef
from .command_def import AbstractCommandDef
from .argument_def import AbstractArgumentDef


TCmdDef = TypeVar("TCmdDef", bound="AbstractCommandDef")

# --------------------------------------------------------------------------------
# AbstractCliDef
# an abstract class for root CLI definition
# --------------------------------------------------------------------------------
class AbstractCliDef(
    AbstractExecutableNode[TArgDef, TNode_co],
    CliDefProtocol[TArgDef, TCmdDef],
    Generic[TArgDef, TCmdDef, TNode_co]
    ):

    _KNOWN_FIELDS = frozenset(
        AbstractExecutableNode._KNOWN_FIELDS | {
        "prompt",
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

            prompt: str|None = None,
            commands: Iterable[TCmdDef]|None = None,

            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(
            key,
            help=help,
            parent=parent,
            entrypoint=entrypoint,
            group=group,
            arguments=arguments,
            extra_defs=extra_defs
            )
        self._prompt: str|None = prompt
        self._commands: list[TCmdDef]|None = list(commands) if commands is not None else None

    @property
    def prompt(self) -> str|None:
        return self._prompt
    
    @property
    def commands(self) -> Sequence[TCmdDef]:
        return self._commands or []

    @property
    def is_leaf(self) -> bool:
        return self._commands is None or len(self._commands) == 0


    def iter_children(self) -> Iterator[TNode_co]:
        yield from super().iter_children()
        yield from self._commands or []


    def get_command_sequence(self) -> Sequence[str]:
        return [self.key]

