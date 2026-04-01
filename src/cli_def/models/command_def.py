# cli_def/models/command_def.py
from __future__ import annotations
from typing import Iterable, Sequence
from dataclasses import dataclass, field
import re

from .abstract_node import CliDefNode, ExecutableNode
from .argument_def import ArgumentDef



# --------------------------------------------------------------------------------
# CliDef
# a concrete class for command/subcommand definition
# --------------------------------------------------------------------------------
@dataclass
class CommandDef(ExecutableNode):
    # reserved keys
    EARLY = "_early"
    # fields
    is_template: bool = False
    help: str|None = None
    aliases: list[str]|None = None
    arguments: list[ArgumentDef] = field(default_factory=list)
    subcommands: list[CommandDef]|None = None
    inherit_from: list[str]|None = None

    def iter_children(self):
        yield from self.arguments or []
        yield from self.subcommands or []

    def get_templates(self) -> Iterable[CommandDef]:
        templates = []
        if self.parent:
            for node in self.parent.iter_children():
                if isinstance(node, CommandDef) and node.is_template:
                    templates.append(node)
        if self.inherit_from is None:
            return templates
        inherit_set = set(self.inherit_from)
        return [tmpl for tmpl in templates if tmpl.key in inherit_set]

    def get_command_sequence(self) -> Sequence[str]:
        key_seq = []
        node = self
        while node is not None:
            key_seq.append(node.key)
            node = node.parent
        return list(reversed(key_seq))