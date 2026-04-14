# cli_def/models/command_def.py
from __future__ import annotations
from typing import Iterable, Sequence, Mapping, Iterator, Any, TypeVar, Self, Generic

from ..protocols import CommandDefProtocol, TNode_co
from .abstract_node import  AbstractCliDefNode
from .executable_node import AbstractExecutableNode, TArgDef
from .argument_def import AbstractArgumentDef

TCmdDef = TypeVar("TCmdDef", bound="AbstractCommandDef")


# --------------------------------------------------------------------------------
# AbstractCommandDef
# an abstract class for command/subcommand definition
# --------------------------------------------------------------------------------
class AbstractCommandDef(
    AbstractExecutableNode[TArgDef, TNode_co],
    CommandDefProtocol[TArgDef],
    Generic[TArgDef, TNode_co],
    ):

    _KNOWN_FIELDS = frozenset(
        AbstractExecutableNode._KNOWN_FIELDS | {
        "aliases",
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

            subcommands: Iterable[Self]|None = None,
            aliases: Iterable[str]|None = None,

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
        self._subcommands: list[Self]|None = list(subcommands) if subcommands is not None else None 
        self._aliases: list[str]|None = list(aliases) if aliases is not None else None


    @property
    def aliases(self) -> Sequence[str]:
        return self._aliases or []
    
    @property
    def subcommands(self) -> Sequence[Self]:
        return self._subcommands or []

    @property
    def is_leaf(self) -> bool:
        return self._subcommands is None or len(self._subcommands) == 0


    def iter_children(self) -> Iterator[TNode_co]:
        yield from super().iter_children()
        yield from self.subcommands or []


    def get_command_sequence(self) -> Sequence[str]:
        key_seq = []
        node = self
        while node is not None:
            key_seq.append(node.key)
            node = node.parent
        return list(reversed(key_seq))

