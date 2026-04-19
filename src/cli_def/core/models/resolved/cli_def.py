# cli_def/core/models/resolved/cli_def.py
from __future__ import annotations
from typing import Sequence, Mapping, Any, Iterable, Iterator


from .resolved_protocols import ResolvedCliDefProtocol
from .resolved_node import ResolvedCliDefNode
from .executable_node import ResolvedExecutableNode
from .argument_def import ResolvedArgumentDef
from .command_def import ResolvedCommandDef
from ..raw import CliDef


# --------------------------------------------------------------------------------
# ResolvedCliDef
# a concrete class for root CLI representation of resolved model
# --------------------------------------------------------------------------------
class ResolvedCliDef(
    ResolvedExecutableNode,
    ResolvedCliDefProtocol
    ):

    _KNOWN_FIELDS = ResolvedExecutableNode._KNOWN_FIELDS

    def __init__(
            self,
            key: str,
            *,
            definition: CliDef,
            help: str|None = None,
            parent: ResolvedCliDefNode|None = None,
            entrypoint: str|None = None,
            group: str|None = None,
            arguments: Iterable[ResolvedArgumentDef]|None = None,

            prompt: str|None = None,
            commands: Iterable[ResolvedCommandDef]|None = None,

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

        self._prompt: str|None = prompt
        self._commands: list[ResolvedCommandDef]|None = list(commands) if commands is not None else None
        
        # fix commands' parents
        if self._commands:
            for n in self._commands:
                n._parent = self

    
    @property
    def prompt(self) -> str|None:
        return self._prompt

    @property
    def commands(self) -> Sequence[ResolvedCommandDef]:
        return self._commands or []


    def iter_children(self) -> Iterator[ResolvedCliDefNode]:
        yield from super().iter_children()
        yield from self._commands or []


    def get_command_sequence(self) -> Sequence[str]:
        return [self.key]

