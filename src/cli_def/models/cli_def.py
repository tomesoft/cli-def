# cli_def/model.py
from typing import Optional, Any, Iterator, Mapping
from dataclasses import dataclass, field
import re

from .cli_def_node import CliDefNode
from .command_def import CommandDef
from .argument_def import ArgumentDef


@dataclass
class CliDef(CliDefNode):
    help: Optional[str] = None
    arguments: list[ArgumentDef] = field(default_factory=list)
    commands: Optional[list["CommandDef"]] = None
    group: Optional[str] = None

    def iter_children(self):
        yield from self.arguments or []
        yield from self.commands or []
