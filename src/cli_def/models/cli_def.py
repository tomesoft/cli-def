# cli_def/model.py
from typing import Optional, Any, Iterator, Mapping
from dataclasses import dataclass, field
import re

from .abstract_node import CliDefNode, ExecutableNode
from .command_def import CommandDef
from .argument_def import ArgumentDef


# --------------------------------------------------------------------------------
# CliDef
# a concrete class for root CLI definition
# --------------------------------------------------------------------------------
@dataclass
class CliDef(ExecutableNode):
    help: Optional[str] = None
    arguments: list[ArgumentDef] = field(default_factory=list)
    commands: Optional[list["CommandDef"]] = None
    group: Optional[str] = None
    prompt: Optional[str] = None # prompt on interactive/repl mode

    def iter_children(self):
        yield from self.arguments or []
        yield from self.commands or []

    def get_command_sequence(self) -> list[str]:
        return [self.key]
