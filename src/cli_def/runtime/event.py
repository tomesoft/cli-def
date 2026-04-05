# cli_def/runtime/event.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Sequence
from ..models.command_def import CommandDef

from .context import CliRuntimeContext

# --------------------------------------------------------------------------------
# CliEvent class
# --------------------------------------------------------------------------------
@dataclass
class CliEvent:
    path: list[str]
    command: CommandDef
    params: dict[str, Any]
    event_source: Any|None = None
    extra_args: Sequence[str]|None = None
    ctx: CliRuntimeContext|None = None

    @property
    def name(self) -> str:
        return self.path[-1]

    def __post_init__(self):
        # fix path from defpath
        if isinstance(self.path, str):
            self.path = [p for p in self.path.split("/") if len(p)]

    @classmethod
    def create(cls, *args, **kwargs) -> CliEvent:
        return cls(
            *args,
            **kwargs
        )
