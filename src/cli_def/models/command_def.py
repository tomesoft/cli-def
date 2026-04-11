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

    def get_templates(self) -> Sequence[CommandDef]:
        templates = []
        if self.parent:
            for node in self.parent.iter_children():
                if isinstance(node, CommandDef) and node.is_template:
                    templates.append(node)
        if self.inherit_from is None:
            return templates
        inherit_set = set(self.inherit_from)
        return [tmpl for tmpl in templates if tmpl.key in inherit_set]

    def resolve_predecessor(self, keyOrPath: str) -> CommandDef|None:
        if "/" in keyOrPath: # means path
            return None # TODO implement
        else:
            if self.parent:
                for node in self.parent.iter_children():
                    if isinstance(node, CommandDef) and node.key == keyOrPath:
                        return node
        return None

    def get_predecessors(self) -> Sequence[CommandDef]:
        predecessors: list[CommandDef] = []
        if self.inherit_from:
            for keyOrPath in self.inherit_from:
                item = self.resolve_predecessor(keyOrPath)
                if item is not None:
                    predecessors.append(item)
        else: # fully inherit from templates
            predecessors.extend(self.get_templates())
        return predecessors


    def get_command_sequence(self) -> Sequence[str]:
        key_seq = []
        node = self
        while node is not None:
            key_seq.append(node.key)
            node = node.parent
        return list(reversed(key_seq))


    def merge_missing_from(self, other: CommandDef):
        super().merge_missing_from(other)
        if self.help is None:
            self.help = other.help
        if self.aliases is None:
            self.aliases = other.aliases


    def override_with(self, other: CommandDef):
        super().override_with(other)
        if other.help is not None:
            self.help = other.help
        if other.aliases is not None:
            self.aliases = other.aliases
