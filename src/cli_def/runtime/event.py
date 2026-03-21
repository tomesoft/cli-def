# cli_def/runtime/event.py
from dataclasses import dataclass
from typing import Any
from ..models.command_def import CommandDef

@dataclass
class CliEvent:
    path: list[str]
    command: CommandDef
    params: dict[str, Any]

    @property
    def name(self) -> str:
        return self.path[-1]