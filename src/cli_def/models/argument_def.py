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


    def __post_init__(self):
        if self.mult is None:
            self.mult = MultDef(1, 1)

        elif isinstance(self.mult, str):
            self.mult = MultDef.from_str(self.mult)

        elif not isinstance(self.mult, MultDef):
            raise TypeError(f"Invalid mult type: {type(self.mult)}")

        if self.is_flag:
            if self.default is None:
                self.default = False
            if self.type is None:
                self.type = "bool"


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

