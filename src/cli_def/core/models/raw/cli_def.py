# cli_def/core/models/raw/cli_def.py
from __future__ import annotations
from typing import Sequence, Mapping, Any, Iterable, Iterator, TypeVar, Generic
from pathlib import Path

from .raw_protocols import RawCliDefProtocol
from .raw_node import CliDefNode
from .executable_node import ExecutableNode
from .command_def import CommandDef
from .argument_def import ArgumentDef

from ....basic.basic_types import PathLike

#TCmdDef = TypeVar("TCmdDef", bound="AbstractCommandDef")

# --------------------------------------------------------------------------------
# CliDef
# a concrete class for root CLI definition or raw model
# --------------------------------------------------------------------------------
class CliDef(
    ExecutableNode,
    RawCliDefProtocol
    ):

    _KNOWN_FIELDS = frozenset(
        ExecutableNode._KNOWN_FIELDS | {
        "prompt",
        "include",
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

            prompt: str|None = None,
            commands: Iterable[CommandDef]|None = None,
            include: Iterable[str]|None = None,

            bind: Mapping[str, Any]|None = None, # for parameter binding
            extra_defs: Mapping[str, Any]|None = None,
            source: PathLike|None = None,
        ):
        super().__init__(
            key,
            help=help,
            parent=parent,
            entrypoint=entrypoint,
            group=group,
            bind=bind,
            arguments=arguments,
            extra_defs=extra_defs
            )
        self._prompt: str|None = prompt
        self._commands: list[CommandDef]|None = list(commands) if commands is not None else None
        self._include: list[str]|None = list(include) if include is not None else None
        
        self.set_source(source)


    @property
    def prompt(self) -> str|None:
        return self._prompt
    
    @property
    def commands(self) -> Sequence[CommandDef]:
        return self._commands or []

    @property
    def include(self) -> Sequence[str]:
        return self._include or []

    @property
    def source(self) -> Path|None:
        return self._source

    def set_source(self, source: PathLike|None):
        self._source: Path|None = (
            source if isinstance(source, Path)
            else Path(source) if isinstance(source, str)
            else None
        )


    @property
    def is_leaf(self) -> bool:
        return self._commands is None or len(self._commands) == 0


    def iter_children(self) -> Iterator[CliDefNode]:
        yield from super().iter_children()
        yield from self._commands or []


    def get_command_sequence(self) -> Sequence[str]:
        return [self.key]


    def merge_missing_from(self, other: CliDef):
        if self._help is None:
            self._help = other.help
        for k, v in other.extra_defs:
            self._extra_defs.setdefault(k, v)

        if self._entrypoint is None:
            self._entrypoint = other.entrypoint
        if self._group is None:
            self._group = other.group
        if self._bind is None:
            if other.bind is not None:
                self._bind = dict(other.bind)
        else:
            if other.bind is not None:
                for k, v in other.bind.items():
                    self._bind.setdefault(k, v)

        if self._prompt is None:
            self._prompt = other.prompt

    def override_with(self, other: CliDef):
        if other.help is not None:
            self._help = other.help
        self._extra_defs.update(other.extra_defs)

        if other.entrypoint is not None:
            self._entrypoint = other.entrypoint
        if other.group is not None:
            self._group = other.group
        if other.bind is not None:
            if self._bind is None:
                self._bind = dict(other.bind)
            else:
                self._bind.update(other.bind)

        if other.prompt is not None:
            self._prompt = other.prompt

