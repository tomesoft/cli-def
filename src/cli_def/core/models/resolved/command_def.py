# cli_def/core/models/resolved/command_def.py
from __future__ import annotations
from typing import Iterable, Sequence, Mapping, Iterator, Any

#from cli_def.core.models.protocols import CliDefNodeProtocol

from .resolved_node import ResolvedCliDefNode
from .executable_node import ResolvedExecutableNode
from .resolved_protocols import ResolvedCommandDefProtocol
# from ..generic.abstract_node import AbstractCliDefNode
# from ..generic.command_def import AbstractCommandDef
from ..raw.command_def import CommandDef
from .argument_def import ResolvedArgumentDef



# --------------------------------------------------------------------------------
# ResolvedCommandDef
# a concrete class for resolved command/subcommand representation
# --------------------------------------------------------------------------------
class ResolvedCommandDef(
    ResolvedExecutableNode,
    # AbstractCommandDef,
    ResolvedCommandDefProtocol
    ):

    _KNOWN_FIELDS = ResolvedExecutableNode._KNOWN_FIELDS

    def __init__(
            self,
            key: str,
            *,
            definition: CommandDef,
            help: str|None = None,
            parent: ResolvedCliDefNode|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            arguments: Iterable[ResolvedArgumentDef]|None = None,

            subcommands: Iterable[ResolvedCommandDef]|None = None,
            aliases: Iterable[str]|None = None,

            bound_params: Mapping[str, Any]|None = None,

            extra_defs: Mapping[str, Any]|None = None,
        ):
        super().__init__(
            key,
            definition=definition,
            help=help,
            parent=parent,
            entrypoint=entrypoint,
            group=group,
            arguments=arguments,
            bound_params=bound_params,
            extra_defs=extra_defs
            )

        self._subcommands: list[ResolvedCommandDef]|None = list(subcommands) if subcommands is not None else None 
        self._aliases: list[str]|None = list(aliases) if aliases is not None else None

        # fix subcommands' parents
        if self._subcommands:
            for n in self._subcommands:
                n._parent = self

    

    @property
    def aliases(self) -> Sequence[str]:
        return self._aliases or []
    
    @property
    def subcommands(self) -> Sequence[ResolvedCommandDef]:
        return self._subcommands or []

    @property
    def is_leaf(self) -> bool:
        return self._subcommands is None or len(self._subcommands) == 0


    def iter_children(self) -> Iterator[ResolvedCliDefNode]:
        yield from super().iter_children()
        yield from self.subcommands or []


    def get_command_sequence(self) -> Sequence[str]:
        key_seq = []
        node = self
        while node is not None:
            key_seq.append(node.key)
            node = node.parent
        return list(reversed(key_seq))
