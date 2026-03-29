# cli_def/runtime/event.py
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
    event_source: Optional[Any] = None
    extra_args: Optional[Sequence[str]] = None
    ctx: CliRuntimeContext = None

    @property
    def name(self) -> str:
        return self.path[-1]