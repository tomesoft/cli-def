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
    prompt: str|None = None # prompt on interactive/repl mode
    arguments: list[ArgumentDef] = field(default_factory=list)
    commands: list[CommandDef]|None = None
    resolved: bool = False # to be set by resolver

    def iter_children(self):
        yield from self.arguments or []
        yield from self.commands or []

    def get_command_sequence(self) -> Sequence[str]:
        return [self.key]


    def merge_missing_from(self, other: CliDef):
        super().merge_missing_from(other)
        if self.help is None:
            self.help = other.help
        if self.prompt is None:
            self.prompt = other.prompt

    def override_with(self, other: CliDef):
        super().override_with(other)
        if other.help is not None:
            self.help = other.help
        if other.prompt is not None:
            self.prompt = other.prompt