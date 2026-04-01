# cli_def/runtime/event.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Sequence
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