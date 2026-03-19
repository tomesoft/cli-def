# cli_def/models/command_def.py
from typing import Optional, Any, Iterator, Mapping
from dataclasses import dataclass, field
import re

from .cli_def_node import CliDefNode
from .argument_def import ArgumentDef



@dataclass
class CommandDef(CliDefNode):
    is_template: bool = False
    help: Optional[str] = None
    aliases: Optional[list[str]] = None
    arguments: list[ArgumentDef] = field(default_factory=list)
    subcommands: Optional[list["CommandDef"]] = None
    group: Optional[str] = None

    def iter_children(self):
        yield from self.arguments or []
        yield from self.subcommands or []
