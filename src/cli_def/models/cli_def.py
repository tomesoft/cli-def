# cli_def/model.py
from __future__ import annotations
from typing import Sequence
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
    help: str|None = None
    arguments: list[ArgumentDef] = field(default_factory=list)
    commands: list[CommandDef]|None = None
    prompt: str|None = None # prompt on interactive/repl mode

    def iter_children(self):
        yield from self.arguments or []
        yield from self.commands or []

    def get_command_sequence(self) -> Sequence[str]:
        return [self.key]
