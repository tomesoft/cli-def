# cli_def/model.py
from __future__ import annotations
from typing import Any, Iterator, Mapping
from dataclasses import dataclass, field

from .abstract_node import CliDefNode
from .mult_def import MultDef



# --------------------------------------------------------------------------------
# ArgumentDef
# a concrete class for argument/option definition
# --------------------------------------------------------------------------------
@dataclass
class ArgumentDef(CliDefNode):
    dest: str|None = None
    option: str|None = None # "--<option>"
    aliases: list[str]|None = None
    type: str|None = None
    mult: MultDef|None = None
    choices: list[Any]|None = None
    default: Any|None = None
    help: str|None = None
    is_flag: bool|None = None
    bound: Any|None = None # set from resolver


    def __post_init__(self):
        if self.mult is None:
            if self.is_positional:
                self.mult = MultDef(1, 1)
            else:
                self.mult = MultDef(0, 1)

        elif isinstance(self.mult, str):
            self.mult = MultDef.from_str(self.mult)

        elif not isinstance(self.mult, MultDef):
            raise TypeError(f"Invalid mult type: {type(self.mult)}")

        if self.is_flag:
            if self.default is None:
                self.default = False
            if self.type is None:
                self.type = "bool"


    def merge_missing_from(self, other: ArgumentDef):
        super().merge_missing_from(other)
        if self.dest is None:
            self.dest = other.dest
        if self.option is None:
            self.option = other.option
        if self.aliases is None:
            self.aliases = other.aliases
        if self.type is None:
            self.type = other.type
        if self.mult is None:
            self.mult = other.mult
        if self.choices is None:
            self.choices = other.choices
        if self.default is None:
            self.default = other.default
        if self.help is None:
            self.help = other.help
        if self.is_flag is None:
            self.is_flag = other.is_flag


    def override_with(self, other: ArgumentDef):
        super().override_with(other)
        if other.dest is not None:
            self.dest = other.dest
        if other.option is not None:
            self.option = other.option
        if other.aliases is not None:
            self.aliases = other.aliases
        if other.type is not None:
            self.type = other.type
        if other.mult is not None:
            self.mult = other.mult
        if other.choices is not None:
            self.choices = other.choices
        if other.default is not None:
            self.default = other.default
        if other.help is not None:
            self.help = other.help
        if other.is_flag is not None:
            self.is_flag = other.is_flag


    @property
    def is_positional(self) -> bool:
        return self.option is None


    @classmethod
    def from_mapping(cls, mapping: Mapping[str, Any]) -> ArgumentDef:
        known = {}
        extra = {}

        for k, v in mapping.items():
            if k in cls.__dataclass_fields__:
                known[k] = v
            else:
                extra[k] = v

        obj = cls(**known)
        obj.extra_defs.update(extra)
        return obj


    def iter_children(self):
        return iter([])


    def get_dest(self) -> str | None:
        if self.option is None:
            # positional parameter ignores dest
            return None
        return self.dest or self.key

    def get_action(self) -> str | None:
        if self.is_flag:
            if "action" in self.extra_defs:
                return self.extra_defs["action"]
            if self.default is not None and self.default == True:
                return "store_false"
            return "store_true"
        return None

