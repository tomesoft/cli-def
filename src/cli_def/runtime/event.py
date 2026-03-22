# cli_def/runtime/event.py
from dataclasses import dataclass
from typing import Any, Optional, Sequence
from ..models.command_def import CommandDef

@dataclass
class CliEvent:
    path: list[str]
    command: CommandDef
    params: dict[str, Any]
    event_source: Optional[Any] = None
    extra_args: Optional[Sequence[str]] = None

    @property
    def name(self) -> str:
        return self.path[-1]