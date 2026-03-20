# cli_def/models/command_def.py
from typing import Optional, Any, Iterator, Mapping, Iterable
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
    inherit_from: Optional[list[str]] = None

    def iter_children(self):
        yield from self.arguments or []
        yield from self.subcommands or []

    def get_templates(self) -> Iterable["CommandDef"]:
        templates = []
        for node in self.parent.iter_children():
            if isinstance(node, CommandDef) and node.is_template:
                templates.append(node)
        if self.inherit_from is None:
            return templates
        inherit_set = set(self.inherit_from)
        return [tmpl for tmpl in templates if tmpl.key in inherit_set]